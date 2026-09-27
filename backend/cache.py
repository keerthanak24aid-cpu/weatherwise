import time

_CACHE = {}

def set_cache(key: str, value, ttl: int = 300):
    """Store value under key for ttl seconds."""
    _CACHE[key] = (time.time() + ttl, value)


def get_cache(key: str):
    """Return cached value or None if expired/missing."""
    entry = _CACHE.get(key)
    if not entry:
        return None
    expires_at, value = entry
    if time.time() > expires_at:
        try:
            del _CACHE[key]
        except KeyError:
            pass
        return None
    return value
