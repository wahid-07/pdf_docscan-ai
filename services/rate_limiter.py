import time
from collections import defaultdict, deque


class InMemoryRateLimiter:
    def __init__(self, limit: int, window_seconds: int = 60):
        self.limit = limit
        self.window_seconds = window_seconds
        self._requests = defaultdict(deque)

    def allow(self, key: str) -> bool:
        now = time.time()
        bucket = self._requests[key]

        while bucket and now - bucket[0] >= self.window_seconds:
            bucket.popleft()

        if len(bucket) >= self.limit:
            return False

        bucket.append(now)
        return True
