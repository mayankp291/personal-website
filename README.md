# Mayank's personal website

Dark, technical, operations-inspired personal website for Mayank Panjiyara —
live at [mayankp.me](https://mayankp.me).

A static SvelteKit frontend deployed to Cloudflare Pages, backed by a
FastAPI service running in a rootless Podman homelab and exposed through a
Cloudflare Tunnel at `api.mayankp.me`.

## Architecture

```text
browser
  ├── mayankp.me         Cloudflare Pages (static SvelteKit build)
  └── api.mayankp.me     Cloudflare Tunnel
                            └── homeserver (Podman, rootless)
                                  ├── personal-website-api   FastAPI :8000
                                  ├── personal-website-db    PostgreSQL 17
                                  └── personal-website-status SQLite volume
```

## Repository layout

```text
frontend/        SvelteKit static site (Cloudflare Pages)
backend/         FastAPI service (Podman homelab)
infrastructure/  Podman Quadlet files and deployment notes
.github/         GitHub Actions workflows
```

## Frontend

- SvelteKit 2 / Svelte 5 with `@sveltejs/adapter-static`
- Plain CSS design system in `frontend/src/app.css`
- Fonts: `DM Mono`, `Manrope`, `Space Grotesk`

Key routes:

| Route             | Purpose                                  |
| ----------------- | ---------------------------------------- |
| `/`               | Portfolio homepage                       |
| `/lab`            | Live homelab status and uptime dashboard |
| `/architecture`   | Interactive homelab topology             |
| `/projects/[slug]`| Static project detail pages              |
| `/writing`        | Placeholder writing page                 |

Project content is centralized in `frontend/src/lib/projects.js`. The
resume is served from `frontend/static/resume.pdf`.

The dashboard calls the public API (`https://api.mayankp.me`) in both local
and production environments, since the local API cannot reach homelab-only
services.

## Backend

A small FastAPI application in `backend/app/main.py`.

Endpoints:

- `GET /healthz`
- `GET /api/v1/status`
- `GET /api/v1/projects`
- `GET /api/v1/homelab/status`
- `GET /api/v1/homelab/history?hours=24`
- `GET /api/v1/visits` / `POST /api/v1/visits` (visit counter, stored in PostgreSQL)
- `GET /docs`

The homelab status API probes the website API, Immich
(`/api/server/ping`), and PostgreSQL (TCP `:5432`). A background sampler
collects status every 30 seconds into SQLite (mounted at `/data/status.db`
via the `personal-website-status` volume).

The API intentionally returns only sanitized fields — no private
addresses, container IDs, credentials, raw errors, or private application
URLs.

## Local development

Node.js is installed user-locally at `~/.local/node` in the current
environment:

```sh
export PATH="$HOME/.local/node/bin:$PATH"
```

Frontend:

```sh
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

Backend:

```sh
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Useful checks:

```sh
cd frontend && npm run check && npm run build
cd backend && python3 -m compileall -q app
```

Note: the local API runs outside the homelab network, so its homelab
service checks report offline. The frontend dashboard therefore targets the
public homelab API instead.

## Homelab deployment

Homelab host: `homeserver` (`169.42.0.189`), user `website-deploy`, rootless
Podman with systemd linger enabled. Production Quadlet files live in
`infrastructure/podman/`.

Current services:

- `personal-website-db.service` — PostgreSQL 17
- `personal-website-api.service` — FastAPI backend (bound to loopback `:8000`)
- `personal-website.target` — enabled user target
- Root-managed `cloudflared.service` — routes `api.mayankp.me` to `127.0.0.1:8000`

Manual backend deployment:

```sh
scp -q -i /home/mayank/.ssh/mayank-homelab-deploy \
  backend/Containerfile backend/healthcheck.py backend/requirements.txt \
  website-deploy@169.42.0.189:~/personal-website/backend/

scp -q -r -i /home/mayank/.ssh/mayank-homelab-deploy \
  backend/app \
  website-deploy@169.42.0.189:~/personal-website/backend/
```

Application files under `backend/app/` go into the remote
`~/personal-website/backend/app/` directory, not the backend root. Then
rebuild and restart:

```sh
ssh -i /home/mayank/.ssh/mayank-homelab-deploy \
  website-deploy@169.42.0.189 \
  'podman build --network=host --tag localhost/mayank-personal-website-api:latest ~/personal-website/backend && systemctl --user restart personal-website-api.service'
```

The homelab build needs `--network=host` because the default Podman build
network cannot resolve PyPI in this environment.

Verify the deployment:

```sh
curl https://api.mayankp.me/healthz
curl https://api.mayankp.me/api/v1/homelab/status
curl 'https://api.mayankp.me/api/v1/homelab/history?hours=24'
```

## CI/CD

`.github/workflows/frontend-pages.yml` runs on pushes to `main` that touch
`frontend/` (or the workflow itself): `npm ci`, `npm run check`,
`npm run build`, then `wrangler pages deploy`.

Required GitHub settings: secrets `CLOUDFLARE_API_TOKEN` and
`CLOUDFLARE_ACCOUNT_ID`, variable `CLOUDFLARE_PAGES_PROJECT`.

## Contributing

This is a personal site; contributions aren't expected. If you do work on
it, keep uploaded reference material (`Portfolio.html`, resume sources,
etc.) uncommitted, and never commit `.env` files, tunnel tokens, passwords,
or API tokens.
