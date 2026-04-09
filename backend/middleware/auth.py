"""
Auth Middleware
===============
JWT validation and user loading for protected routes.
"""

from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from db.models import User


def require_premium(fn):
    """
    Decorator that requires the user to have a Pro or Lifetime subscription.
    Must be used AFTER @jwt_required().
    """

    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)

        if not user:
            return jsonify({"error": "User not found"}), 404

        if user.tier not in ("pro", "lifetime"):
            return jsonify({
                "error": "This feature requires a Pro subscription",
                "tier": user.tier,
                "upgrade_url": "/api/subscription/plans",
            }), 403

        return fn(*args, **kwargs)

    return wrapper
