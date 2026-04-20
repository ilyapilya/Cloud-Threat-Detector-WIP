import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes.scan_routes import router as scan_router
from .routes.schedule_routes import router as schedule_router
from .services.scheduler import start_scheduler, stop_scheduler

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(
    title="CloudGuard API",
    description="Cloud security scanner — detects misconfigurations across AWS, Azure, GCP.",
    version="0.3.0",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
_origins = [
    "http://localhost:5173",   # Vite dev server
    "http://localhost:4173",   # Vite preview
]
frontend_url = os.getenv("FRONTEND_URL", "")
if frontend_url:
    _origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ────────────────────────────────────────────────────────────────────
app.include_router(scan_router)
app.include_router(schedule_router)


@app.get("/", tags=["health"])
def health():
    return {"status": "ok", "service": "cloudguard-api"}
