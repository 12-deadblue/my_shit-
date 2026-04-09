"""
Rate Limiting Middleware
========================
Redis-based rate limiting for API endpoints.
"""

from functools import wraps
from flask import request, jsonify
from services.cache import redis_client


def rate_limit(max_requests=100, window_seconds=3600):
    """
    Rate limit decorator using Redis.

    Args:
        max_requests: Maximum requests allowed in the window.
        window_seconds: Time window in seconds (default: 1 hour).
    """

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Use IP + endpoint as the rate limit key
            client_ip = request.remote_addr or "unknown"
            key = f"rate:{client_ip}:{request.endpoint}"

            allowed, remaining = redis_client.check_rate_limit(
                key, max_requests, window_seconds
            )

            if not allowed:
                return jsonify({
                    "error": "Rate limit exceeded",
                    "retry_after_seconds": window_seconds,
                }), 429

            response = fn(*args, **kwargs)

            # Add rate limit headers if response is a tuple or Response
            # (simplified — in production use after_request)
            return response

        return wrapper

    return decorator
