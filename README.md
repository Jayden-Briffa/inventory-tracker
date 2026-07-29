# Inventory Tracker — Backend

**Prerequisites**
- **Python**: 3.10 or newer.

**Setup**
- **Create virtual environment and install dependencies:**

```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

**Database**
- The database is initialized automatically on import (see `backend/migrations.py` and `backend/database.py`).
- The SQLite file will be created at `backend/db.sqlite` when the server first runs.

**Run the API**
- Recommended (uvicorn):

```bash
cd backend
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

- Or run the module directly:

```bash
cd backend
python main.py
```

**Verify**
- Open the interactive docs at: http://127.0.0.1:8000/docs
- Or Redoc: http://127.0.0.1:8000/redoc

**Run tests**

```bash
cd backend
pytest
```

**Notes**
- Server entrypoint: `backend/main.py`.
- Dependencies: `backend/requirements.txt`.
- CORS origins configured for `http://localhost:5173` and `http://127.0.0.1:5173` in `main.py`.
- To change the database location, edit `DATABASE_URL` in `backend/database.py`.
