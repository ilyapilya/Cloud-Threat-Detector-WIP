import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes.scan_routes import router as scan_router

app = FastAPI(
    title="CloudGuard API",
    description="Cloud security scanner — detects misconfigurations across AWS, Azure, GCP.",
    version="0.2.0",
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


@app.get("/", tags=["health"])
def health():
    return {"status": "ok", "service": "cloudguard-api"}
