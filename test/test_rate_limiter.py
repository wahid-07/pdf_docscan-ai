import time

from services.rate_limiter import InMemoryRateLimiter


def test_rate_limiter_blocks_excess_requests_within_window():
    limiter = InMemoryRateLimiter(limit=2, window_seconds=1)

    assert limiter.allow("client-1") is True
    assert limiter.allow("client-1") is True
    assert limiter.allow("client-1") is False


def test_rate_limiter_allows_after_window_passes():
    limiter = InMemoryRateLimiter(limit=1, window_seconds=0.01)

    assert limiter.allow("client-2") is True
    time.sleep(0.02)
    assert limiter.allow("client-2") is True
