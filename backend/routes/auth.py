"""
Auth Routes
===========
Google OAuth login/logout and user profile.
"""

from datetime import datetime, timezone
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
)
from db.models import db, User
from services.google_auth import verify_google_token, get_user_info_from_access_token
from services.cache import redis_client
from services.analytics import track_event

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/google", methods=["POST"])
def google_login():
    """
    Exchange a Google OAuth token for a JWT.

    Accepts either:
      - { "id_token": "..." }  (ID token from Google Sign-In)
      - { "access_token": "..." }  (Access token from chrome.identity)

    Returns:
      - JWT access & refresh tokens
      - User profile
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    client_id = current_app.config["GOOGLE_CLIENT_ID"]
    user_info = None

    # Try ID token first, then access token
    if "id_token" in data:
        user_info = verify_google_token(data["id_token"], client_id)
    elif "access_token" in data:
        user_info = get_user_info_from_access_token(data["access_token"])

    if not user_info:
        return jsonify({"error": "Invalid token"}), 401

    # Find or create user
    user = User.query.filter_by(google_id=user_info["google_id"]).first()

    if user:
        # Update existing user
        user.name = user_info["name"]
        user.avatar_url = user_info["avatar_url"]
        user.last_active = datetime.now(timezone.utc)
    else:
        # Create new user
        user = User(
            google_id=user_info["google_id"],
            email=user_info["email"],
            name=user_info["name"],
            avatar_url=user_info["avatar_url"],
            tier="free",
            is_admin=user_info["email"] in current_app.config["ADMIN_EMAILS"],
        )
        db.session.add(user)

    db.session.commit()

    # Cache user data
    redis_client.cache_user(user.google_id, user.to_dict())

    # Track login event
    track_event(user.id, "login")

    # Generate JWT tokens
    identity = str(user.id)
    access_token = create_access_token(identity=identity)
    refresh_token = create_refresh_token(identity=identity)

    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": user.to_dict(),
    })


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_profile():
    """Get the current user's profile."""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    # Update last active
    user.last_active = datetime.now(timezone.utc)
    db.session.commit()

    return jsonify({"user": user.to_dict()})


@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    """
    Logout — invalidate cached session.
    Note: JWT tokens are stateless. For true invalidation,
    you'd need a token blacklist (future enhancement).
    """
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if user:
        redis_client.invalidate_user(user.google_id)

    return jsonify({"message": "Logged out"})
