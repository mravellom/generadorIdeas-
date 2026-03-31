"""Tests for the rate limiter."""
import time

from app.services.rate_limiter import RateLimiter


class TestRateLimiter:
    def test_allows_within_limit(self):
        limiter = RateLimiter(max_calls=5, period=60.0)
        for _ in range(5):
            limiter.wait()
        # Should not raise or block significantly

    def test_tracks_timestamps(self):
        limiter = RateLimiter(max_calls=3, period=60.0)
        limiter.wait()
        limiter.wait()
        assert len(limiter._timestamps) == 2

    def test_blocks_when_limit_reached(self):
        limiter = RateLimiter(max_calls=2, period=0.5)
        limiter.wait()
        limiter.wait()
        start = time.monotonic()
        limiter.wait()
        elapsed = time.monotonic() - start
        # Should have waited ~0.5s for the window to clear
        assert elapsed >= 0.3
