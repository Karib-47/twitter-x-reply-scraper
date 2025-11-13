thonimport threading
import time
from collections import deque
from typing import Deque

class RateLimiter:
    """
    Simple thread-safe rate limiter using a moving window of timestamps.

    Example: RateLimiter(calls=30, period=60.0) allows up to 30 calls per
    60-second window. Additional calls will block until a slot becomes free.
    """

    def __init__(self, calls: int, period: float) -> None:
        if calls <= 0:
            raise ValueError("calls must be positive")
        if period <= 0:
            raise ValueError("period must be positive")

        self.calls = calls
        self.period = period
        self._timestamps: Deque[float] = deque()
        self._lock = threading.Lock()

    def acquire(self) -> None:
        """
        Block until a new call is allowed based on the configured rate.

        This uses a simple moving window where we track timestamps of the
        last `calls` invocations and ensure no more than `calls` occur
        within `period` seconds.
        """
        while True:
            with self._lock:
                now = time.monotonic()

                # Drop timestamps outside the window
                while self._timestamps and now - self._timestamps[0] > self.period:
                    self._timestamps.popleft()

                if len(self._timestamps) < self.calls:
                    # We have capacity for another call
                    self._timestamps.append(now)
                    return

                # Need to wait until the oldest timestamp falls out of the window
                oldest = self._timestamps[0]
                sleep_for = self.period - (now - oldest)

            if sleep_for > 0:
                time.sleep(sleep_for)
            else:
                # Edge case: if computed sleep is non-positive, loop again
                time.sleep(0.001)