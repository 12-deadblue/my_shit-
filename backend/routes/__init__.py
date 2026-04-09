"""
Routes Package
==============
Register all Flask blueprints.
"""

from routes.auth import auth_bp
from routes.subscription import subscription_bp
from routes.data import data_bp
from routes.admin import admin_bp


def register_blueprints(app):
    """Register all API blueprints with the app."""
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(subscription_bp, url_prefix="/api/subscription")
    app.register_blueprint(data_bp, url_prefix="/api/data")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
