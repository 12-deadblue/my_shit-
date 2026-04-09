"""
Database Models
===============
SQLAlchemy models for Users, Subscriptions, Payments, SavedPages,
Highlights, and UsageEvents.
"""

from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    """Registered user (via Google OAuth)."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    google_id = db.Column(db.String(128), unique=True, nullable=False)
    email = db.Column(db.String(256), unique=True, nullable=False)
    name = db.Column(db.String(256))
    avatar_url = db.Column(db.String(512))
    tier = db.Column(db.String(20), default="free")  # free | pro | lifetime
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )
    last_active = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    subscriptions = db.relationship(
        "Subscription", backref="user", lazy="dynamic"
    )
    saved_pages = db.relationship("SavedPage", backref="user", lazy="dynamic")
    highlights = db.relationship("Highlight", backref="user", lazy="dynamic")
    usage_events = db.relationship(
        "UsageEvent", backref="user", lazy="dynamic"
    )
    payments = db.relationship("Payment", backref="user", lazy="dynamic")

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "avatar_url": self.avatar_url,
            "tier": self.tier,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_active": self.last_active.isoformat() if self.last_active else None,
        }


class Subscription(db.Model):
    """User subscription record."""

    __tablename__ = "subscriptions"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    plan = db.Column(db.String(50), nullable=False)  # pro_monthly | lifetime
    status = db.Column(
        db.String(20), nullable=False
    )  # active | cancelled | expired | paused
    google_pay_token = db.Column(db.Text)
    started_at = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime)
    cancelled_at = db.Column(db.DateTime)

    def to_dict(self):
        return {
            "id": self.id,
            "plan": self.plan,
            "status": self.status,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
        }


class Payment(db.Model):
    """Payment transaction record."""

    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    amount_cents = db.Column(db.Integer, nullable=False)
    currency = db.Column(db.String(3), default="USD")
    google_pay_token = db.Column(db.Text)
    status = db.Column(
        db.String(20), nullable=False
    )  # completed | failed | refunded
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self):
        return {
            "id": self.id,
            "amount_cents": self.amount_cents,
            "currency": self.currency,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class SavedPage(db.Model):
    """A page saved by the user."""

    __tablename__ = "saved_pages"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    url = db.Column(db.Text, nullable=False)
    title = db.Column(db.Text)
    favicon_url = db.Column(db.Text)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self):
        return {
            "id": self.id,
            "url": self.url,
            "title": self.title,
            "favicon_url": self.favicon_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Highlight(db.Model):
    """A text highlight made by the user."""

    __tablename__ = "highlights"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    page_url = db.Column(db.Text, nullable=False)
    text_content = db.Column(db.Text, nullable=False)
    color = db.Column(db.String(20), default="#ffeb3b")
    selector_path = db.Column(db.Text)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self):
        return {
            "id": self.id,
            "page_url": self.page_url,
            "text_content": self.text_content,
            "color": self.color,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class UsageEvent(db.Model):
    """Analytics event for admin dashboard."""

    __tablename__ = "usage_events"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    event_type = db.Column(
        db.String(50), nullable=False
    )  # highlight | save_page | export | login
    metadata_json = db.Column(db.Text)  # JSON blob
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self):
        return {
            "id": self.id,
            "event_type": self.event_type,
            "metadata": self.metadata_json,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
