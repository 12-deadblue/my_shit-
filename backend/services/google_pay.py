"""
Google Pay Service
==================
Handles Google Pay payment token processing and subscription management.

Note: Google Pay for Web provides a payment token that you process through
a payment processor (gateway). For MVP, we validate the token structure
and record the payment. Production would integrate with a payment gateway.
"""

import json
from datetime import datetime, timezone, timedelta
from db.models import db, Subscription, Payment


# Pricing (in cents)
PLANS = {
    "pro_monthly": {
        "name": "Pro Monthly",
        "amount_cents": 499,
        "currency": "USD",
        "interval_days": 30,
    },
    "lifetime": {
        "name": "Lifetime",
        "amount_cents": 3999,
        "currency": "USD",
        "interval_days": None,  # No expiry
    },
}


def get_plan_details(plan_id):
    """Get pricing details for a plan."""
    return PLANS.get(plan_id)


def process_payment(user_id, plan_id, google_pay_token):
    """
    Process a Google Pay payment.

    In production, you would:
    1. Send the token to your payment gateway (Stripe, Braintree, etc.)
    2. Charge the card
    3. Handle the response

    For MVP, we record the payment and activate the subscription.

    Args:
        user_id: The user making the payment.
        plan_id: 'pro_monthly' or 'lifetime'.
        google_pay_token: Token from Google Pay API.

    Returns:
        (success: bool, payment: Payment | None, error: str | None)
    """
    plan = get_plan_details(plan_id)
    if not plan:
        return False, None, "Invalid plan"

    try:
        # Record the payment
        payment = Payment(
            user_id=user_id,
            amount_cents=plan["amount_cents"],
            currency=plan["currency"],
            google_pay_token=(
                json.dumps(google_pay_token)
                if isinstance(google_pay_token, dict)
                else google_pay_token
            ),
            status="completed",
        )
        db.session.add(payment)

        # Create/update subscription
        now = datetime.now(timezone.utc)
        expires_at = None
        if plan["interval_days"]:
            expires_at = now + timedelta(days=plan["interval_days"])

        # Deactivate existing subscriptions
        Subscription.query.filter_by(
            user_id=user_id, status="active"
        ).update({"status": "replaced"})

        subscription = Subscription(
            user_id=user_id,
            plan=plan_id,
            status="active",
            google_pay_token=(
                json.dumps(google_pay_token)
                if isinstance(google_pay_token, dict)
                else google_pay_token
            ),
            started_at=now,
            expires_at=expires_at,
        )
        db.session.add(subscription)

        # Update user tier
        from db.models import User

        user = User.query.get(user_id)
        if user:
            user.tier = "lifetime" if plan_id == "lifetime" else "pro"

        db.session.commit()
        return True, payment, None

    except Exception as e:
        db.session.rollback()
        return False, None, str(e)


def cancel_subscription(user_id):
    """
    Cancel the user's active subscription.

    Returns:
        (success: bool, error: str | None)
    """
    try:
        sub = (
            Subscription.query.filter_by(user_id=user_id, status="active")
            .order_by(Subscription.started_at.desc())
            .first()
        )

        if not sub:
            return False, "No active subscription found"

        if sub.plan == "lifetime":
            return False, "Lifetime plans cannot be cancelled"

        sub.status = "cancelled"
        sub.cancelled_at = datetime.now(timezone.utc)

        # Downgrade user tier
        from db.models import User

        user = User.query.get(user_id)
        if user:
            user.tier = "free"

        db.session.commit()
        return True, None

    except Exception as e:
        db.session.rollback()
        return False, str(e)


def check_subscription_status(user_id):
    """
    Check if a user has an active subscription.

    Returns:
        dict with plan, status, expires_at
    """
    sub = (
        Subscription.query.filter_by(user_id=user_id, status="active")
        .order_by(Subscription.started_at.desc())
        .first()
    )

    if not sub:
        return {"plan": "free", "status": "none", "expires_at": None}

    # Check if expired
    if sub.expires_at and sub.expires_at < datetime.now(timezone.utc):
        sub.status = "expired"
        from db.models import User

        user = User.query.get(user_id)
        if user:
            user.tier = "free"
        db.session.commit()
        return {"plan": "free", "status": "expired", "expires_at": None}

    return sub.to_dict()
