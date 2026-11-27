import threading
import time


class TTLCache:
    def __init__(self, ttl_seconds: float = 60.0, max_items: int = 1000):
        self.ttl = ttl_seconds
        self.max_items = max_items
        self._data = {}
        self._lock = threading.Lock()

    def get(self, key):
        with self._lock:
            item = self._data.get(key)
            if item is None:
                return None
            value, expires_at = item
            if time.monotonic() >= expires_at:
                del self._data[key]
                return None
            return value

    def set(self, key, value):
        with self._lock:
            if len(self._data) >= self.max_items:
                oldest = min(self._data, key=lambda k: self._data[k][1])
                del self._data[oldest]
            self._data[key] = (value, time.monotonic() + self.ttl)
