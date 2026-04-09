"""
Data Routes
============
CRUD for saved pages, highlights, and data sync/export.
Enforces free tier limits.
"""

import json
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from db.models import db, User, SavedPage, Highlight
from services.cache import redis_client
from services.analytics import track_event

data_bp = Blueprint("data", __name__)


def _is_premium(user):
    """Check if user has a paid tier."""
    return user.tier in ("pro", "lifetime")


# ── Saved Pages ─────────────────────────────────────────────────


@data_bp.route("/pages", methods=["GET"])
@jwt_required()
def get_pages():
    """Get saved pages for the current user (paginated)."""
    user_id = int(get_jwt_identity())
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    per_page = min(per_page, 100)  # Cap at 100

    pagination = (
        SavedPage.query.filter_by(user_id=user_id)
        .order_by(SavedPage.created_at.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )

    return jsonify({
        "pages": [p.to_dict() for p in pagination.items],
        "total": pagination.total,
        "page": page,
        "per_page": per_page,
        "has_next": pagination.has_next,
    })


@data_bp.route("/pages", methods=["POST"])
@jwt_required()
def save_page():
    """Save a page. Free users limited to FREE_MAX_SAVED_PAGES."""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    data = request.get_json()

    if not data or not data.get("url"):
        return jsonify({"error": "url is required"}), 400

    # Check free tier limit
    if not _is_premium(user):
        max_pages = current_app.config["FREE_MAX_SAVED_PAGES"]

        # Try cache first for count
        count = redis_client.get_cached_page_count(user_id)
        if count is None:
            count = SavedPage.query.filter_by(user_id=user_id).count()
            redis_client.cache_page_count(user_id, count)

        if count >= max_pages:
            return jsonify({
                "error": "Free tier limit reached",
                "limit": max_pages,
                "upgrade_url": "/api/subscription/plans",
            }), 403

    page = SavedPage(
        user_id=user_id,
        url=data["url"],
        title=data.get("title", ""),
        favicon_url=data.get("favicon_url", ""),
    )
    db.session.add(page)
    db.session.commit()

    # Update cache
    redis_client.increment_page_count(user_id)

    # Track event
    track_event(user_id, "save_page", {"url": data["url"]})

    return jsonify({"page": page.to_dict()}), 201


@data_bp.route("/pages/<int:page_id>", methods=["DELETE"])
@jwt_required()
def delete_page(page_id):
    """Delete a saved page."""
    user_id = int(get_jwt_identity())

    page = SavedPage.query.filter_by(id=page_id, user_id=user_id).first()
    if not page:
        return jsonify({"error": "Page not found"}), 404

    db.session.delete(page)
    db.session.commit()

    # Update cache
    redis_client.decrement_page_count(user_id)

    return jsonify({"message": "Page deleted"})


# ── Highlights ──────────────────────────────────────────────────


@data_bp.route("/highlights", methods=["GET"])
@jwt_required()
def get_highlights():
    """Get highlights for the current user."""
    user_id = int(get_jwt_identity())
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 50, type=int)
    per_page = min(per_page, 100)

    pagination = (
        Highlight.query.filter_by(user_id=user_id)
        .order_by(Highlight.created_at.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )

    return jsonify({
        "highlights": [h.to_dict() for h in pagination.items],
        "total": pagination.total,
        "page": page,
        "per_page": per_page,
        "has_next": pagination.has_next,
    })


@data_bp.route("/highlights", methods=["POST"])
@jwt_required()
def save_highlight():
    """Save a text highlight."""
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data or not data.get("page_url") or not data.get("text_content"):
        return jsonify({"error": "page_url and text_content are required"}), 400

    highlight = Highlight(
        user_id=user_id,
        page_url=data["page_url"],
        text_content=data["text_content"],
        color=data.get("color", "#ffeb3b"),
        selector_path=data.get("selector_path", ""),
    )
    db.session.add(highlight)
    db.session.commit()

    track_event(user_id, "highlight", {"page_url": data["page_url"]})

    return jsonify({"highlight": highlight.to_dict()}), 201


# ── Sync ────────────────────────────────────────────────────────


@data_bp.route("/sync", methods=["POST"])
@jwt_required()
def sync_data():
    """
    Bulk sync from extension (Pro/Lifetime only).
    Accepts arrays of pages and highlights to sync.
    """
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not _is_premium(user):
        return jsonify({
            "error": "Cloud sync is a Pro feature",
            "upgrade_url": "/api/subscription/plans",
        }), 403

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    synced = {"pages": 0, "highlights": 0}

    # Sync pages
    for page_data in data.get("pages", []):
        # Check if already exists (by URL + user)
        existing = SavedPage.query.filter_by(
            user_id=user_id, url=page_data.get("url", "")
        ).first()
        if not existing and page_data.get("url"):
            page = SavedPage(
                user_id=user_id,
                url=page_data["url"],
                title=page_data.get("title", ""),
                favicon_url=page_data.get("favicon_url", ""),
            )
            db.session.add(page)
            synced["pages"] += 1

    # Sync highlights
    for hl_data in data.get("highlights", []):
        if hl_data.get("page_url") and hl_data.get("text_content"):
            highlight = Highlight(
                user_id=user_id,
                page_url=hl_data["page_url"],
                text_content=hl_data["text_content"],
                color=hl_data.get("color", "#ffeb3b"),
                selector_path=hl_data.get("selector_path", ""),
            )
            db.session.add(highlight)
            synced["highlights"] += 1

    db.session.commit()

    # Invalidate page count cache
    redis_client.cache_page_count(
        user_id, SavedPage.query.filter_by(user_id=user_id).count()
    )

    track_event(user_id, "sync", synced)

    return jsonify({"message": "Sync complete", "synced": synced})


# ── Export ──────────────────────────────────────────────────────


@data_bp.route("/export", methods=["GET"])
@jwt_required()
def export_data():
    """Export all user data as JSON (Pro/Lifetime only)."""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not _is_premium(user):
        return jsonify({
            "error": "Data export is a Pro feature",
            "upgrade_url": "/api/subscription/plans",
        }), 403

    pages = [p.to_dict() for p in SavedPage.query.filter_by(user_id=user_id).all()]
    highlights = [h.to_dict() for h in Highlight.query.filter_by(user_id=user_id).all()]

    track_event(user_id, "export")

    return jsonify({
        "export": {
            "user": user.to_dict(),
            "saved_pages": pages,
            "highlights": highlights,
        }
    })
