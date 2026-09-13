"""Disk-based cache for API responses."""
import os
import json
import hashlib
from typing import Optional, Dict, Any


class ResponseCache:
    """Disk-based cache for API responses."""

    def __init__(self, cache_dir: str = ".cache/"):
        """Initialize cache.

        Args:
            cache_dir: Directory to store cached responses
        """
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)

    def _get_key_hash(self, key: str) -> str:
        """Generate hash for cache key."""
        return hashlib.sha256(key.encode()).hexdigest()

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached response.

        Args:
            key: Cache key

        Returns:
            Cached response or None if not found
        """
        key_hash = self._get_key_hash(key)
        cache_file = os.path.join(self.cache_dir, f"{key_hash}.json")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return None
        return None

    def set(self, key: str, value: Dict[str, Any]):
        """Cache response to disk.

        Args:
            key: Cache key
            value: Response data to cache
        """
        key_hash = self._get_key_hash(key)
        cache_file = os.path.join(self.cache_dir, f"{key_hash}.json")
        try:
            with open(cache_file, 'w') as f:
                json.dump(value, f)
        except Exception:
            pass
