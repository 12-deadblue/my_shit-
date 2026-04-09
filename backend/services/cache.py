"""
Redis Cache Service
===================
Wrapper around Redis for caching user sessions, subscription status,
saved page counts, and admin dashboard metrics.

Cache keys:
  user:{google_id}        → user profile + tier (TTL: 15min)
  sub:{user_id}           → subscription status (TTL: 15min)
  pages:{user_id}:count   → saved page count (TTL: 5min)
  pages:{user_id}:recent  → recent page IDs list (TTL: 5min)
  admin:stats             → dashboard metrics (TTL: 5min)
  rate:{ip}               → rate limit counter (TTL: 1hr)
"""

import json
import redis


class RedisCache:
    """Redis cache layer with write-through invalidation."""

    def __init__(self):
        self._client = None

    def init_app(self, app):
        """Initialize Redis connection from Flask app config."""
        redis_url = app.config.get("REDIS_URL", "redis://localhost:6379/0")
        try:
            self._client = redis.from_url(
                redis_url, decode_responses=True, socket_timeout=5
            )
            self._client.ping()
            app.logger.info("✅ Redis connected: %s", redis_url)
        except redis.ConnectionError:
            app.logger.warning(
                "⚠️ Redis unavailable at %s — running without cache",
                redis_url,
            )
            self._client = None

    @property
    def available(self):
        """Check if Redis is connected and responsive."""
        if self._client is None:
            return False
        try:
            self._client.ping()
            return True
        except (redis.ConnectionError, redis.TimeoutError):
            return False

    # ── User Cache ──────────────────────────────────────────────

    def cache_user(self, google_id, user_dict, ttl=900):
        """Cache user profile data (15 min default)."""
        if not self.available:
            return
        key = f"user:{google_id}"
        self._client.setex(key, ttl, json.dumps(user_dict))

    def get_cached_user(self, google_id):
        """Get cached user profile."""
        if not self.available:
            return None
        key = f"user:{google_id}"
        data = self._client.get(key)
        return json.loads(data) if data else None

    def invalidate_user(self, google_id):
        """Clear user cache (call after profile updates)."""
        if not self.available:
            return
        self._client.delete(f"user:{google_id}")

    # ── Subscription Cache ──────────────────────────────────────

    def cache_subscription(self, user_id, sub_dict, ttl=900):
        """Cache subscription status (15 min default)."""
        if not self.available:
            return
        key = f"sub:{user_id}"
        self._client.setex(key, ttl, json.dumps(sub_dict))

    def get_cached_subscription(self, user_id):
        """Get cached subscription status."""
        if not self.available:
            return None
        key = f"sub:{user_id}"
        data = self._client.get(key)
        return json.loads(data) if data else None

    def invalidate_subscription(self, user_id):
        """Clear subscription cache (call after payment events)."""
        if not self.available:
            return
        self._client.delete(f"sub:{user_id}")

    # ── Page Count Cache ────────────────────────────────────────

    def cache_page_count(self, user_id, count, ttl=300):
        """Cache saved page count (5 min default)."""
        if not self.available:
            return
        key = f"pages:{user_id}:count"
        self._client.setex(key, ttl, str(count))

    def get_cached_page_count(self, user_id):
        """Get cached page count. Returns int or None."""
        if not self.available:
            return None
        key = f"pages:{user_id}:count"
        data = self._client.get(key)
        return int(data) if data is not None else None

    def increment_page_count(self, user_id):
        """Increment cached page count (write-through)."""
        if not self.available:
            return
        key = f"pages:{user_id}:count"
        if self._client.exists(key):
            self._client.incr(key)

    def decrement_page_count(self, user_id):
        """Decrement cached page count (write-through)."""
        if not self.available:
            return
        key = f"pages:{user_id}:count"
        if self._client.exists(key):
            self._client.decr(key)

    # ── Admin Stats Cache ───────────────────────────────────────

    def cache_admin_stats(self, stats_dict, ttl=300):
        """Cache admin dashboard metrics (5 min default)."""
        if not self.available:
            return
        self._client.setex("admin:stats", ttl, json.dumps(stats_dict))

    def get_cached_admin_stats(self):
        """Get cached admin stats."""
        if not self.available:
            return None
        data = self._client.get("admin:stats")
        return json.loads(data) if data else None

    def invalidate_admin_stats(self):
        """Clear admin stats cache."""
        if not self.available:
            return
        self._client.delete("admin:stats")

    # ── Rate Limiting ───────────────────────────────────────────

    def check_rate_limit(self, key, max_requests, window_seconds):
        """
        Simple sliding window rate limiter.
        Returns (allowed: bool, remaining: int).
        """
        if not self.available:
            return True, max_requests

        current = self._client.get(key)
        if current is None:
            self._client.setex(key, window_seconds, 1)
            return True, max_requests - 1

        current = int(current)
        if current >= max_requests:
            return False, 0

        self._client.incr(key)
        return True, max_requests - current - 1


# Singleton instance — initialized via init_app()
redis_client = RedisCache()
