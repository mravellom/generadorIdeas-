"""Simple rate limiter for Gemini API (free tier: 15 RPM)."""
import time
import threading


class RateLimiter:
    """Token-bucket rate limiter. Thread-safe."""

    def __init__(self, max_calls: int = 14, period: float = 60.0):
        self._max_calls = max_calls
        self._period = period
        self._timestamps: list[float] = []
        self._lock = threading.Lock()

    def wait(self) -> None:
        """Block until a request slot is available."""
        with self._lock:
            now = time.monotonic()
            # Purge timestamps older than the period
            self._timestamps = [t for t in self._timestamps if now - t < self._period]

            if len(self._timestamps) >= self._max_calls:
                sleep_until = self._timestamps[0] + self._period
                sleep_time = sleep_until - now
                if sleep_time > 0:
                    time.sleep(sleep_time)

            self._timestamps.append(time.monotonic())


# Global instance — 14 RPM to leave margin below 15 RPM limit
gemini_limiter = RateLimiter(max_calls=14, period=60.0)
