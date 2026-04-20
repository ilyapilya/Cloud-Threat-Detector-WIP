"""
Stripe Routes
POST /api/v1/stripe/checkout  — create Stripe Checkout Session → return URL
GET  /api/v1/me               — return current user's plan
"""

import os
import stripe
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..deps import get_db, get_optional_user_id
from ..models import User

router = APIRouter(prefix="/api/v1")

FRONTEND_URL = os.getenv("FRONTEND_URL", "https://cloudguard.app")


def _stripe_client():
    key = os.getenv("STRIPE_SECRET_KEY")
    if not key:
        raise HTTPException(status_code=503, detail="Stripe is not configured.")
    stripe.api_key = key
    return stripe


class CheckoutRequest(BaseModel):
    email: str


@router.post("/stripe/checkout")
def create_checkout(
    body: CheckoutRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_optional_user_id),
):
    """Create a Stripe Checkout Session and return the hosted URL."""
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required.")

    price_id = os.getenv("STRIPE_PRICE_ID")
    if not price_id:
        raise HTTPException(status_code=503, detail="Stripe price not configured.")

    client = _stripe_client()

    session = client.checkout.sessions.create(
        mode="subscription",
        customer_email=body.email,
        line_items=[{"price": price_id, "quantity": 1}],
        metadata={"clerk_user_id": user_id},
        success_url=f"{FRONTEND_URL}/dashboard?upgraded=true",
        cancel_url=f"{FRONTEND_URL}/dashboard",
    )

    return {"url": session.url}


@router.get("/me")
def get_me(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_optional_user_id),
):
    """Return the authenticated user's plan."""
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required.")

    user = db.query(User).filter(User.clerk_id == user_id).first()
    return {"plan": user.plan if user else "free"}
