Development run (SQLite)

1. Create a virtualenv and install deps:

```bash
python -m venv .venv
source .venv/bin/activate  # on Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Enable SQLite and start the server:

```powershell
$env:USE_SQLITE = '1'
uvicorn main:app --reload --port 8000
```

3. Open the UI (served from FastAPI):

http://127.0.0.1:8000/

Notes:
- This repo includes a lightweight ML model loader that expects model files in `models/`.
