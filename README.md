# Productify

A photo of any object goes in; a self-contained HTML pitch page for an invented company
comes out. See `CLAUDE.md` for context and `contracts/` for the frozen interfaces.

## Run

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env                    # then paste the key (Station 1 only)
MOCK=1 uvicorn app.main:app --reload    # development, no API calls
uvicorn app.main:app --reload           # real API calls
```

Then open http://localhost:8000/web/index.html — health check at
http://localhost:8000/health.
