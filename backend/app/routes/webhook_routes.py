"""
Stripe Webhook Handler
POST /api/v1/webhooks/stripe

Handles checkout.session.completed → upgrades user plan to 'pro'.
"""

import os
import logging
import stripe
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from ..deps import get_db
from ..models import User

router = APIRouter(prefix="/api/v1")
logger = logging.getLogger(__name__)


@router.post("/webhooks/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig = request.headers.get("stripe-signature", "")
    secret = os.getenv("STRIPE_WEBHOOK_SECRET", "")

    stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")

    try:
        event = stripe.Webhook.construct_event(payload, sig, secret)
    except stripe.errors.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid webhook signature.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        clerk_user_id = session.get("metadata", {}).get("clerk_user_id")
        customer_email = session.get("customer_email") or session.get("customer_details", {}).get("email")
        stripe_customer_id = session.get("customer")

        if clerk_user_id:
            user = db.query(User).filter(User.clerk_id == clerk_user_id).first()
            if user:
                user.plan               = "pro"
                user.stripe_customer_id = stripe_customer_id
            else:
                db.add(User(
                    clerk_id           = clerk_user_id,
                    email              = customer_email,
                    plan               = "pro",
                    stripe_customer_id = stripe_customer_id,
                ))
            db.commit()
            logger.info("Upgraded user %s to pro", clerk_user_id)

    # Return 200 for all event types (Stripe retries on non-2xx)
    return {"received": True}
