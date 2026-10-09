import threading
import time


class RateLimiter:
    """Fixed-window in-memory rate limiter. Thread-safe, single-process."""

    def __init__(self, max_requests: int, window_seconds: int) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._lock = threading.Lock()
        # key → (window_start, count)
        self._windows: dict[str, tuple[float, int]] = {}

    def is_allowed(self, key: str) -> tuple[bool, int]:
        """Return (allowed, seconds_until_reset).

        seconds_until_reset is 0 when allowed, positive when blocked.
        """
        now = time.monotonic()
        with self._lock:
            start, count = self._windows.get(key, (now, 0))

            if now - start >= self.window_seconds:
                # Window expired — start a fresh one
                self._windows[key] = (now, 1)
                return True, 0

            if count >= self.max_requests:
                reset_in = int(self.window_seconds - (now - start)) + 1
                return False, reset_in

            self._windows[key] = (start, count + 1)
            return True, 0
