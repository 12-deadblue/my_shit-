"""
My Extension — Flask Backend
=============================
Main application factory and entry point.
"""

import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from config import config
from db.models import db
from services.cache import redis_client
from routes import register_blueprints


def create_app(config_name=None):
    """Application factory pattern."""
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "default")

    app = Flask(__name__)
    config_class = config[config_name]
    app.config.from_object(config_class)

    # Run config-specific validation (e.g., ProductionConfig checks secrets)
    if hasattr(config_class, "init_app"):
        config_class.init_app(app)

    # ── Extensions ──────────────────────────────────────────────
    CORS(app, origins=app.config["CORS_ORIGINS"])
    JWTManager(app)
    db.init_app(app)

    # ── Redis ───────────────────────────────────────────────────
    redis_client.init_app(app)

    # ── Blueprints ──────────────────────────────────────────────
    register_blueprints(app)

    # ── Database ────────────────────────────────────────────────
    with app.app_context():
        # Ensure the database directory exists (SQLite won't create it)
        db_uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")
        if db_uri.startswith("sqlite:///"):
            db_path = db_uri.replace("sqlite:///", "", 1)
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
        db.create_all()

    # ── Health Check ────────────────────────────────────────────
    @app.route("/api/health")
    def health():
        return {"status": "healthy", "version": "1.0.0"}

    return app


# ── Entry Point ─────────────────────────────────────────────────
if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
