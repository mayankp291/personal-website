import asyncio
from contextlib import asynccontextmanager, suppress
from datetime import UTC, datetime
from os import getenv
from pathlib import Path
from sqlite3 import connect
from socket import create_connection
from threading import Lock
from time import monotonic
from datetime import timedelta
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


class Project(BaseModel):
    slug: str
    title: str
    summary: str
    tags: list[str]


class SiteStatus(BaseModel):
    status: str
    checked_at: datetime
    services: list[dict[str, str]]


class ServiceStatus(BaseModel):
    id: str
    name: str
    status: str
    latency_ms: int | None = None
    detail: str
    checked_at: datetime


class HomelabStatus(BaseModel):
    status: str
    checked_at: datetime
    services: list[ServiceStatus]
    cache_ttl_seconds: int = Field(default=15)


class HistoryPoint(BaseModel):
    timestamp: datetime
    status: str
    latency_ms: int | None = None


class ServiceHistory(BaseModel):
    id: str
    name: str
    points: list[HistoryPoint]


class HomelabHistory(BaseModel):
    hours: int
    services: list[ServiceHistory]


async def _status_sampler() -> None:
    while True:
        await asyncio.to_thread(_refresh_status_cache)
        await asyncio.sleep(30)


@asynccontextmanager
async def lifespan(_app):
    sampler = asyncio.create_task(_status_sampler())
    yield
    sampler.cancel()
    with suppress(asyncio.CancelledError):
        await sampler


app = FastAPI(title="mayankp.me API", version="0.1.0", lifespan=lifespan)

origins = [
    origin.strip()
    for origin in getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,https://mayankp.me,https://www.mayankp.me",
    ).split(",")
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

_status_cache: HomelabStatus | None = None
_status_cache_time = 0.0
_status_cache_lock = Lock()
_status_cache_ttl = 15
_history_path = Path(getenv("STATUS_DB_PATH", "/tmp/mayank-status.db"))
_homelab_host = getenv("HOMELAB_HOST", "host.containers.internal")


def _init_history() -> None:
    _history_path.parent.mkdir(parents=True, exist_ok=True)
    with connect(_history_path) as database:
        database.execute(
            """CREATE TABLE IF NOT EXISTS service_checks (
                service_id TEXT NOT NULL,
                service_name TEXT NOT NULL,
                checked_at TEXT NOT NULL,
                status TEXT NOT NULL,
                latency_ms INTEGER
            )"""
        )
        database.execute(
            "CREATE INDEX IF NOT EXISTS service_checks_time ON service_checks (checked_at)"
        )


_init_history()
_immich_health_url = getenv(
    "IMMICH_HEALTH_URL",
    f"http://{_homelab_host}:2283/api/server/ping",
)


def _http_probe(url: str) -> tuple[str, int | None]:
    started = monotonic()
    try:
        request = Request(url, headers={"User-Agent": "mayankp.me-status/1.0"})
        with urlopen(request, timeout=3) as response:
            if 200 <= response.status < 400:
                return "operational", round((monotonic() - started) * 1000)
            return "degraded", round((monotonic() - started) * 1000)
    except (HTTPError, URLError, TimeoutError, OSError):
        return "offline", None


def _postgres_probe() -> tuple[str, int | None]:
    started = monotonic()
    try:
        with create_connection((getenv("POSTGRES_HOST", _homelab_host), 5432), timeout=2):
            return "operational", round((monotonic() - started) * 1000)
    except OSError:
        return "offline", None


def _build_homelab_status() -> HomelabStatus:
    checked_at = datetime.now(UTC)
    immich_status, immich_latency = _http_probe(_immich_health_url)
    postgres_status, postgres_latency = _postgres_probe()
    services = [
        ServiceStatus(
            id="website-api",
            name="Website API",
            status="operational",
            latency_ms=0,
            detail="Serving the public status API",
            checked_at=checked_at,
        ),
        ServiceStatus(
            id="immich",
            name="Immich",
            status=immich_status,
            latency_ms=immich_latency,
            detail="Self-hosted photo library",
            checked_at=checked_at,
        ),
        ServiceStatus(
            id="postgresql",
            name="PostgreSQL",
            status=postgres_status,
            latency_ms=postgres_latency,
            detail="Persistent website data store",
            checked_at=checked_at,
        ),
    ]
    overall = "operational" if all(service.status == "operational" for service in services) else "degraded"
    result = HomelabStatus(status=overall, checked_at=checked_at, services=services)
    with connect(_history_path) as database:
        database.executemany(
            "INSERT INTO service_checks (service_id, service_name, checked_at, status, latency_ms) VALUES (?, ?, ?, ?, ?)",
            [
                (service.id, service.name, service.checked_at.isoformat(), service.status, service.latency_ms)
                for service in services
            ],
        )
    return result


def _refresh_status_cache() -> HomelabStatus:
    global _status_cache, _status_cache_time

    with _status_cache_lock:
        if _status_cache is None or monotonic() - _status_cache_time >= _status_cache_ttl:
            _status_cache = _build_homelab_status()
            _status_cache_time = monotonic()
        return _status_cache


@app.get("/healthz", tags=["operations"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/v1/projects", response_model=list[Project], tags=["content"])
def projects() -> list[Project]:
    return [
        Project(
            slug="platform-reliability",
            title="Platform reliability",
            summary="Paved roads for teams to ship safely, with observable defaults and boring failure modes.",
            tags=["Kubernetes", "Go", "OpenTelemetry"],
        )
    ]


@app.get("/api/v1/status", response_model=SiteStatus, tags=["operations"])
def site_status() -> SiteStatus:
    return SiteStatus(
        status="operational",
        checked_at=datetime.now(UTC),
        services=[
            {"name": "website", "status": "operational"},
            {"name": "api", "status": "operational"},
        ],
    )


@app.get("/api/v1/homelab/status", response_model=HomelabStatus, tags=["operations"])
def homelab_status() -> HomelabStatus:
    return _refresh_status_cache()


@app.get("/api/v1/homelab/history", response_model=HomelabHistory, tags=["operations"])
def homelab_history(hours: int = 24) -> HomelabHistory:
    hours = max(1, min(hours, 168))
    since = (datetime.now(UTC) - timedelta(hours=hours)).isoformat()
    with connect(_history_path) as database:
        rows = database.execute(
            """SELECT service_id, service_name, checked_at, status, latency_ms
            FROM service_checks WHERE checked_at >= ? ORDER BY checked_at ASC""",
            (since,),
        ).fetchall()

    grouped: dict[str, ServiceHistory] = {}
    for service_id, service_name, checked_at, status, latency_ms in rows:
        grouped.setdefault(service_id, ServiceHistory(id=service_id, name=service_name, points=[])).points.append(
            HistoryPoint(timestamp=datetime.fromisoformat(checked_at), status=status, latency_ms=latency_ms)
        )
    return HomelabHistory(hours=hours, services=list(grouped.values()))
