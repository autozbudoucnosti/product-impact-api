"""
Simple in-memory rate limiter: max N requests per API key per time window.
No Redis; suitable for single-instance deployment. 429 when exceeded.
"""

import time
from collections import defaultdict
from threading import Lock

# Max requests per key per window
MAX_REQUESTS_PER_WINDOW = 5
WINDOW_SECONDS = 1.0

# key -> list of request timestamps (within current window)
_request_timestamps: dict[str, list[float]] = defaultdict(list)
_lock = Lock()


def _prune_old(timestamps: list[float], now: float) -> list[float]:
    """Keep only timestamps within the last WINDOW_SECONDS."""
    cutoff = now - WINDOW_SECONDS
    return [t for t in timestamps if t > cutoff]


def check_rate_limit(api_key: str) -> bool:
    """
    Record a request for this API key and return True if allowed.
    Return False if over limit (caller should return 429).
    """
    now = time.monotonic()
    with _lock:
        timestamps = _request_timestamps[api_key]
        timestamps = _prune_old(timestamps, now)
        if len(timestamps) >= MAX_REQUESTS_PER_WINDOW:
            return False
        timestamps.append(now)
        _request_timestamps[api_key] = timestamps
    return True
