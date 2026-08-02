import asyncio
from contextlib import asynccontextmanager, suppress
from datetime import UTC, datetime
from os import getenv
from socket import create_connection
from threading import Lock
from time import monotonic
from datetime import timedelta
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from psycopg import Connection, connect as pg_connect
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


class Visits(BaseModel):
    total: int


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
_homelab_host = getenv("HOMELAB_HOST", "host.containers.internal")


def _pg_dsn() -> str:
    return (
        f"host={getenv('POSTGRES_HOST', 'personal-website-db')} "
        f"port={getenv('POSTGRES_PORT', '5432')} "
        f"dbname={getenv('POSTGRES_DB', 'postgres')} "
        f"user={getenv('POSTGRES_USER', '')} "
        f"password={getenv('POSTGRES_PASSWORD', '')}"
    )


def _pg_connect() -> Connection:
    connection = pg_connect(_pg_dsn(), autocommit=True)
    connection.execute(
        """CREATE TABLE IF NOT EXISTS visits (
            id BIGSERIAL PRIMARY KEY,
            visited_at TIMESTAMPTZ NOT NULL
        )"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS service_checks (
            service_id TEXT NOT NULL,
            service_name TEXT NOT NULL,
            checked_at TIMESTAMPTZ NOT NULL,
            status TEXT NOT NULL,
            latency_ms INTEGER
        )"""
    )
    connection.execute(
        "CREATE INDEX IF NOT EXISTS service_checks_time ON service_checks (checked_at)"
    )
    return connection


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
    with _pg_connect() as connection:
        for service in services:
            connection.execute(
                "INSERT INTO service_checks (service_id, service_name, checked_at, status, latency_ms) VALUES (%s, %s, %s, %s, %s)",
                (service.id, service.name, service.checked_at, service.status, service.latency_ms),
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
    since = datetime.now(UTC) - timedelta(hours=hours)
    with _pg_connect() as connection:
        rows = connection.execute(
            """SELECT service_id, service_name, checked_at, status, latency_ms
            FROM service_checks WHERE checked_at >= %s ORDER BY checked_at ASC""",
            (since,),
        ).fetchall()

    grouped: dict[str, ServiceHistory] = {}
    for service_id, service_name, checked_at, status, latency_ms in rows:
        grouped.setdefault(service_id, ServiceHistory(id=service_id, name=service_name, points=[])).points.append(
            HistoryPoint(timestamp=checked_at, status=status, latency_ms=latency_ms)
        )
    return HomelabHistory(hours=hours, services=list(grouped.values()))


@app.post("/api/v1/visits", response_model=Visits, tags=["operations"])
def record_visit() -> Visits:
    try:
        with _pg_connect() as connection:
            connection.execute("INSERT INTO visits (visited_at) VALUES (now())")
            (total,) = connection.execute("SELECT COUNT(*) FROM visits").fetchone()
    except Exception:
        raise HTTPException(status_code=503, detail="visits store unavailable")
    return Visits(total=total)


@app.get("/api/v1/visits", response_model=Visits, tags=["operations"])
def visit_count() -> Visits:
    try:
        with _pg_connect() as connection:
            (total,) = connection.execute("SELECT COUNT(*) FROM visits").fetchone()
    except Exception:
        raise HTTPException(status_code=503, detail="visits store unavailable")
    return Visits(total=total)
