import os
import time
import httpx
import jwt
from typing import Generator, Optional
from fastapi import Header
from .database import SessionLocal

# ── DB session ────────────────────────────────────────────────────────────────

def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── Clerk JWT → user_id ───────────────────────────────────────────────────────

CLERK_JWKS_URL = "https://api.clerk.dev/v1/jwks"

# Simple in-memory JWKS cache (Clerk rotates keys rarely)
_jwks_cache: dict = {"keys": [], "fetched_at": 0.0}
_JWKS_TTL = 3600  # re-fetch every hour


def _get_jwks() -> list:
    now = time.time()
    if now - _jwks_cache["fetched_at"] > _JWKS_TTL or not _jwks_cache["keys"]:
        try:
            resp = httpx.get(CLERK_JWKS_URL, timeout=5)
            resp.raise_for_status()
            _jwks_cache["keys"] = resp.json().get("keys", [])
            _jwks_cache["fetched_at"] = now
        except Exception:
            pass  # return stale cache on network error
    return _jwks_cache["keys"]


def get_optional_user_id(authorization: Optional[str] = Header(default=None)) -> Optional[str]:
    """
    Extract Clerk user_id (sub) from the Bearer JWT.
    Returns None silently if the header is missing or the token is invalid —
    unauthenticated requests are still allowed (user_id stored as NULL).
    """
    if not authorization or not authorization.startswith("Bearer "):
        return None

    token = authorization[7:]
    try:
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")
        keys = _get_jwks()
        jwk = next((k for k in keys if k.get("kid") == kid), None)
        if not jwk:
            return None
        public_key = jwt.algorithms.RSAAlgorithm.from_jwk(jwk)
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            options={"verify_aud": False},
        )
        return payload.get("sub")
    except Exception:
        return None
