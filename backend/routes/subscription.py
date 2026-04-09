"""
Subscription Routes
===================
Google Pay payment processing, subscription status, and cancellation.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.google_pay import (
    process_payment,
    cancel_subscription,
    check_subscription_status,
    get_plan_details,
    PLANS,
)
from services.cache import redis_client

subscription_bp = Blueprint("subscription", __name__)


@subscription_bp.route("/plans", methods=["GET"])
def list_plans():
    """List available subscription plans with pricing."""
    plans = []
    for plan_id, details in PLANS.items():
        plans.append({
            "id": plan_id,
            "name": details["name"],
            "amount_cents": details["amount_cents"],
            "amount_formatted": f"${details['amount_cents'] / 100:.2f}",
            "currency": details["currency"],
            "interval_days": details["interval_days"],
        })
    return jsonify({"plans": plans})


@subscription_bp.route("/status", methods=["GET"])
@jwt_required()
def get_status():
    """Check the current user's subscription status."""
    user_id = int(get_jwt_identity())

    # Try cache first
    cached = redis_client.get_cached_subscription(user_id)
    if cached:
        return jsonify({"subscription": cached, "cached": True})

    # Fall back to DB
    status = check_subscription_status(user_id)

    # Cache the result
    redis_client.cache_subscription(user_id, status)

    return jsonify({"subscription": status, "cached": False})


@subscription_bp.route("/create", methods=["POST"])
@jwt_required()
def create_subscription():
    """
    Process a Google Pay payment and create a subscription.

    Expects:
      {
        "plan_id": "pro_monthly" | "lifetime",
        "payment_token": { ... }  // Google Pay token
      }
    """
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    plan_id = data.get("plan_id")
    payment_token = data.get("payment_token")

    if not plan_id or not payment_token:
        return jsonify({"error": "plan_id and payment_token required"}), 400

    plan = get_plan_details(plan_id)
    if not plan:
        return jsonify({"error": f"Invalid plan: {plan_id}"}), 400

    # Process payment
    success, payment, error = process_payment(user_id, plan_id, payment_token)

    if not success:
        return jsonify({"error": error}), 400

    # Invalidate caches
    redis_client.invalidate_subscription(user_id)
    redis_client.invalidate_admin_stats()

    return jsonify({
        "message": "Subscription activated",
        "payment": payment.to_dict(),
        "plan": plan_id,
    })


@subscription_bp.route("/cancel", methods=["POST"])
@jwt_required()
def cancel():
    """Cancel the current user's subscription."""
    user_id = int(get_jwt_identity())

    success, error = cancel_subscription(user_id)

    if not success:
        return jsonify({"error": error}), 400

    # Invalidate caches
    redis_client.invalidate_subscription(user_id)
    redis_client.invalidate_admin_stats()

    return jsonify({"message": "Subscription cancelled"})
