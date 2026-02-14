Development run (local sqlite fallback)

1. Create a virtualenv and install deps:

```bash
python -m venv .venv
source .venv/bin/activate  # on Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Enable sqlite fallback and start the server:

```powershell
$env:USE_SQLITE = '1'
uvicorn main:app --reload --port 8000
```

3. Open the UI (served from FastAPI):

http://127.0.0.1:8000/

Notes:
- To use Supabase/Postgres, unset `USE_SQLITE` and set the env vars in `backend/.env` or set `DATABASE_URL`.
- This repo includes a lightweight ML model loader that expects model files in `models/`.
