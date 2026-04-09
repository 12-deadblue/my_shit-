"""
Analytics Service
=================
Track and aggregate usage events for the admin dashboard.
"""

from datetime import datetime, timezone, timedelta
from sqlalchemy import func
from db.models import db, User, UsageEvent, Payment, SavedPage, Subscription


def track_event(user_id, event_type, metadata=None):
    """
    Record a usage event.

    Args:
        user_id: The user who triggered the event.
        event_type: Type of event (highlight, save_page, export, login, etc.)
        metadata: Optional JSON-serializable dict with extra data.
    """
    import json

    event = UsageEvent(
        user_id=user_id,
        event_type=event_type,
        metadata_json=json.dumps(metadata) if metadata else None,
    )
    db.session.add(event)
    db.session.commit()


def get_dashboard_stats():
    """
    Aggregate metrics for the admin dashboard.

    Returns:
        dict with user counts, revenue, activity metrics.
    """
    now = datetime.now(timezone.utc)
    day_ago = now - timedelta(days=1)
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)

    # User metrics
    total_users = User.query.count()
    new_users_today = User.query.filter(User.created_at >= day_ago).count()
    new_users_week = User.query.filter(User.created_at >= week_ago).count()
    active_users_today = User.query.filter(
        User.last_active >= day_ago
    ).count()

    # Tier breakdown
    free_users = User.query.filter_by(tier="free").count()
    pro_users = User.query.filter_by(tier="pro").count()
    lifetime_users = User.query.filter_by(tier="lifetime").count()

    # Revenue
    total_revenue_cents = (
        db.session.query(func.sum(Payment.amount_cents))
        .filter_by(status="completed")
        .scalar()
        or 0
    )
    revenue_this_month = (
        db.session.query(func.sum(Payment.amount_cents))
        .filter(Payment.status == "completed", Payment.created_at >= month_ago)
        .scalar()
        or 0
    )

    # Activity
    events_today = UsageEvent.query.filter(
        UsageEvent.created_at >= day_ago
    ).count()
    total_saved_pages = SavedPage.query.count()

    # Active subscriptions
    active_subs = Subscription.query.filter_by(status="active").count()

    return {
        "users": {
            "total": total_users,
            "new_today": new_users_today,
            "new_this_week": new_users_week,
            "active_today": active_users_today,
            "by_tier": {
                "free": free_users,
                "pro": pro_users,
                "lifetime": lifetime_users,
            },
        },
        "revenue": {
            "total_cents": total_revenue_cents,
            "total_formatted": f"${total_revenue_cents / 100:.2f}",
            "this_month_cents": revenue_this_month,
            "this_month_formatted": f"${revenue_this_month / 100:.2f}",
        },
        "activity": {
            "events_today": events_today,
            "total_saved_pages": total_saved_pages,
            "active_subscriptions": active_subs,
        },
        "generated_at": now.isoformat(),
    }


def get_user_activity(user_id, days=30):
    """
    Get activity breakdown for a specific user.

    Returns:
        dict with event counts by type.
    """
    since = datetime.now(timezone.utc) - timedelta(days=days)

    events = (
        db.session.query(UsageEvent.event_type, func.count(UsageEvent.id))
        .filter(
            UsageEvent.user_id == user_id, UsageEvent.created_at >= since
        )
        .group_by(UsageEvent.event_type)
        .all()
    )

    return {event_type: count for event_type, count in events}
