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
    app.config.from_object(config[config_name])

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
