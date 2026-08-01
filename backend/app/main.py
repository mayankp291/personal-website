from datetime import UTC, datetime
from os import getenv

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


class Project(BaseModel):
    slug: str
    title: str
    summary: str
    tags: list[str]


class SiteStatus(BaseModel):
    status: str
    checked_at: datetime
    services: list[dict[str, str]]


app = FastAPI(title="mayankp.me API", version="0.1.0")

origins = [origin.strip() for origin in getenv("CORS_ORIGINS", "http://localhost:5173").split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


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
