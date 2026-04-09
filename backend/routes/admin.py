"""
Admin Routes
=============
Dashboard metrics, user management, revenue tracking.
Restricted to admin users only.
"""

from functools import wraps
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from db.models import db, User, Payment, SavedPage, Highlight, UsageEvent
from services.cache import redis_client
from services.analytics import get_dashboard_stats, get_user_activity

admin_bp = Blueprint("admin", __name__)


def admin_required(fn):
    """Decorator to restrict routes to admin users."""

    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        if not user or not user.is_admin:
            return jsonify({"error": "Admin access required"}), 403
        return fn(*args, **kwargs)

    return wrapper


@admin_bp.route("/dashboard", methods=["GET"])
@admin_required
def dashboard():
    """
    Get aggregated dashboard metrics.
    Uses Redis cache (5 min TTL) to avoid heavy queries on every request.
    """
    # Try cache first
    cached = redis_client.get_cached_admin_stats()
    if cached:
        return jsonify({"stats": cached, "cached": True})

    # Compute fresh stats
    stats = get_dashboard_stats()

    # Cache for 5 minutes
    redis_client.cache_admin_stats(stats)

    return jsonify({"stats": stats, "cached": False})


@admin_bp.route("/users", methods=["GET"])
@admin_required
def list_users():
    """
    List all users with filtering and pagination.

    Query params:
      - page (int, default 1)
      - per_page (int, default 20, max 100)
      - tier (str, filter by tier)
      - search (str, search by email or name)
      - sort (str, 'created_at' | 'last_active' | 'email')
      - order (str, 'asc' | 'desc')
    """
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 20, type=int), 100)
    tier = request.args.get("tier")
    search = request.args.get("search")
    sort = request.args.get("sort", "created_at")
    order = request.args.get("order", "desc")

    query = User.query

    # Filters
    if tier:
        query = query.filter_by(tier=tier)
    if search:
        query = query.filter(
            db.or_(
                User.email.ilike(f"%{search}%"),
                User.name.ilike(f"%{search}%"),
            )
        )

    # Sorting
    sort_column = getattr(User, sort, User.created_at)
    if order == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "users": [u.to_dict() for u in pagination.items],
        "total": pagination.total,
        "page": page,
        "per_page": per_page,
        "has_next": pagination.has_next,
    })


@admin_bp.route("/users/<int:user_id>", methods=["GET"])
@admin_required
def get_user(user_id):
    """Get detailed info for a single user."""
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Get activity breakdown
    activity = get_user_activity(user_id)

    # Get counts
    pages_count = SavedPage.query.filter_by(user_id=user_id).count()
    highlights_count = Highlight.query.filter_by(user_id=user_id).count()

    # Get payment history
    payments = [
        p.to_dict()
        for p in Payment.query.filter_by(user_id=user_id)
        .order_by(Payment.created_at.desc())
        .limit(10)
        .all()
    ]

    return jsonify({
        "user": user.to_dict(),
        "stats": {
            "saved_pages": pages_count,
            "highlights": highlights_count,
            "activity": activity,
        },
        "payments": payments,
    })


@admin_bp.route("/revenue", methods=["GET"])
@admin_required
def revenue():
    """Get revenue breakdown."""
    from sqlalchemy import func
    from datetime import datetime, timezone, timedelta

    now = datetime.now(timezone.utc)

    # Monthly revenue for last 12 months
    monthly = []
    for i in range(12):
        month_start = (now.replace(day=1) - timedelta(days=30 * i)).replace(day=1)
        if i == 0:
            month_end = now
        else:
            month_end = (month_start + timedelta(days=32)).replace(day=1)

        revenue = (
            db.session.query(func.sum(Payment.amount_cents))
            .filter(
                Payment.status == "completed",
                Payment.created_at >= month_start,
                Payment.created_at < month_end,
            )
            .scalar()
            or 0
        )

        monthly.append({
            "month": month_start.strftime("%Y-%m"),
            "revenue_cents": revenue,
            "revenue_formatted": f"${revenue / 100:.2f}",
        })

    monthly.reverse()

    return jsonify({"monthly_revenue": monthly})


@admin_bp.route("/analytics", methods=["GET"])
@admin_required
def analytics():
    """Get usage analytics breakdown."""
    from sqlalchemy import func
    from datetime import datetime, timezone, timedelta

    now = datetime.now(timezone.utc)
    week_ago = now - timedelta(days=7)

    # Events by type (last 7 days)
    events = (
        db.session.query(UsageEvent.event_type, func.count(UsageEvent.id))
        .filter(UsageEvent.created_at >= week_ago)
        .group_by(UsageEvent.event_type)
        .all()
    )

    # Daily active users (last 7 days)
    daily_active = []
    for i in range(7):
        day = (now - timedelta(days=i)).date()
        day_start = datetime.combine(day, datetime.min.time()).replace(
            tzinfo=timezone.utc
        )
        day_end = day_start + timedelta(days=1)

        count = (
            User.query.filter(
                User.last_active >= day_start,
                User.last_active < day_end,
            ).count()
        )
        daily_active.append({
            "date": day.isoformat(),
            "active_users": count,
        })

    daily_active.reverse()

    return jsonify({
        "events_by_type": {event_type: count for event_type, count in events},
        "daily_active_users": daily_active,
    })
