import base64
import os
import re
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from dotenv import load_dotenv
from databases import Database
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "")
database = Database(DATABASE_URL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not set in environment")
    await database.connect()
    await database.execute(
        """
        CREATE TABLE IF NOT EXISTS photos (
            id UUID PRIMARY KEY,
            image TEXT NOT NULL,
            "timestamp" TIMESTAMPTZ NOT NULL
        );
        """
    )
    yield
    await database.disconnect()


app = FastAPI(title="Photo Capture API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class UploadPhotoBody(BaseModel):
    image: str = Field(..., description="Base64-encoded image (optionally data URL)")


def strip_data_url(b64: str) -> str:
    s = b64.strip()
    if s.startswith("data:"):
        m = re.match(r"data:image/[^;]+;base64,(.+)", s, re.DOTALL)
        if m:
            return m.group(1)
    return s


def validate_base64(raw: str) -> str:
    pad = len(raw) % 4
    if pad:
        raw += "=" * (4 - pad)
    try:
        try:
            data = base64.b64decode(raw, validate=True)
        except TypeError:
            data = base64.b64decode(raw)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64 image data")
    if len(data) > 15 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Image too large (max 15MB)")
    return raw


@app.get("/")
async def root():
    return {"status": "ok", "service": "photo-capture-api"}


@app.post("/upload-photo")
async def upload_photo(body: UploadPhotoBody):
    raw = strip_data_url(body.image)
    raw = validate_base64(raw)

    photo_id = uuid.uuid4()
    ts = datetime.now(timezone.utc)

    await database.execute(
        """
        INSERT INTO photos (id, image, "timestamp")
        VALUES (:id, :image, :ts)
        """,
        {"id": photo_id, "image": raw, "ts": ts},
    )

    return {
        "id": str(photo_id),
        "image": raw,
        "timestamp": ts.isoformat(),
    }


@app.get("/photos")
async def list_photos():
    rows = await database.fetch_all(
        """
        SELECT id, image, "timestamp" AS ts
        FROM photos
        ORDER BY "timestamp" DESC
        """
    )
    photos = []
    for row in rows:
        ts = row["ts"]
        ts_out = ts.isoformat() if isinstance(ts, datetime) else str(ts)
        photos.append(
            {
                "id": str(row["id"]),
                "image": row["image"],
                "timestamp": ts_out,
            }
        )
    return {"photos": photos}
