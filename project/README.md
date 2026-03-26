# Photo Capture — Full-stack demo

A small full-stack app: **FastAPI** stores base64 JPEGs in **PostgreSQL** (`databases` + **asyncpg**); static pages capture from the webcam, show a **3-second countdown**, then upload and preview; **gallery** lists all photos with timestamps in a **masonry** layout.

## Project layout

```
project/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── index.html
│   └── gallery.html
└── README.md
```

---

## 1. Set up PostgreSQL and `DATABASE_URL`

1. Install **PostgreSQL** locally (or use [Docker](https://hub.docker.com/_/postgres), or a hosted DB such as [Neon](https://neon.tech/), [Supabase](https://supabase.com/), or [Railway Postgres](https://railway.app/)).
2. Create a database and a user with permission to create tables (or use your provider’s connection string).
3. Set **`DATABASE_URL`** in `backend/.env` using the **asyncpg** / `postgresql://` form, for example:

   ```text
   DATABASE_URL=postgresql://user:password@localhost:5432/photodb
   ```

   On startup, the API creates a `photos` table if it does not exist (`id` UUID, `image` TEXT base64, `timestamp` timestamptz).

**Railway:** add a **PostgreSQL** plugin or use the connection URL Railway provides, and set `DATABASE_URL` to that URL (often under `Variables` or the database service).

---

## 2. Install Python dependencies

Use Python 3.10+.

```bash
cd backend
python -m venv .venv
```

**Windows (PowerShell):**

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**macOS / Linux:**

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 3. Run the FastAPI server

From `backend/` with the virtual environment activated:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

- API: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- Interactive docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

Endpoints:

- `POST /upload-photo` — JSON body `{ "image": "<base64>" }` (optional `data:image/jpeg;base64,` prefix). Saves the image as text and returns `{ "id", "image", "timestamp" }`.
- `GET /photos` — JSON `{ "photos": [ { "id", "image", "timestamp" }, ... ] }`, newest first.

---

## 4. Open the frontend in the browser

The pages call the API at **`http://127.0.0.1:8000`**. Serve the folder over HTTP (recommended) or open files directly; some browsers restrict `file://` + `fetch` to localhost.

**Option A — Python static server** (from `frontend/`):

```bash
cd ../frontend
python -m http.server 5500
```

Then open:

- [http://127.0.0.1:5500/index.html](http://127.0.0.1:5500/index.html)
- [http://127.0.0.1:5500/gallery.html](http://127.0.0.1:5500/gallery.html)

**Option B — VS Code / Cursor:** use “Live Server” or similar on the `frontend` folder.

**Production URL:** in both `index.html` and `gallery.html`, set `API_BASE` to your deployed API base URL (no trailing slash).

---

## 5. Deploy frontend to Vercel

1. Push the repo to GitHub (or use Vercel CLI).
2. In [Vercel](https://vercel.com/), **New Project** → import the repo.
3. Set **Root Directory** to `frontend` (or the folder that contains `index.html` and `gallery.html`).
4. Framework preset: **Other** (static). Build command: leave empty. Output: `.` or `frontend` depending on root.
5. Deploy. Note the site URL (e.g. `https://your-app.vercel.app`).
6. Edit `API_BASE` in `index.html` and `gallery.html` to your **Railway** backend URL, commit, and redeploy.

**Optional `vercel.json`** at repo root if the app lives in `frontend/`:

```json
{
  "buildCommand": null,
  "outputDirectory": "frontend"
}
```

(Adjust to match how you connected the project in Vercel.)

---

## 6. Deploy backend to Railway

1. Push the same repo to GitHub.
2. In [Railway](https://railway.app/), **New Project** → **Deploy from GitHub** → select the repo.
3. Set **Root Directory** to `backend`.
4. **Variables** (example):
   - `DATABASE_URL` — PostgreSQL connection string from Railway’s Postgres service or your host.
5. **Start command:** a `Procfile` is included with `uvicorn` bound to `$PORT`. If Railway does not pick it up, set the start command to:

   ```bash
   uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

6. Generate a public URL for the service and use it as **`API_BASE`** on the Vercel site.

---

## Local checklist

| Step | Action |
|------|--------|
| 1 | PostgreSQL running + `DATABASE_URL` in `backend/.env` |
| 2 | Fill `backend/.env` |
| 3 | `pip install -r requirements.txt` |
| 4 | `uvicorn main:app --reload --host 0.0.0.0 --port 8000` |
| 5 | Serve `frontend/` and open `index.html` |
| 6 | Update `API_BASE` after Vercel + Railway deploys |

---

## License

MIT-0 / use freely for learning and demos.
