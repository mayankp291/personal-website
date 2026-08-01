# Mayank's personal website

A SvelteKit frontend on Cloudflare Pages with a FastAPI backend hosted in a
Podman homelab.

## Local development

Frontend:

```sh
export PATH="$HOME/.local/node/bin:$PATH"
cd frontend
npm install
npm run dev
```

Backend:

```sh
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

The frontend uses `PUBLIC_API_URL` for the API origin and defaults to
`http://localhost:8000`.
