"""Caching utilities for DuggerLinkTools ecosystem."""

from __future__ import annotations

import functools
import time
from typing import Any, Callable, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


def ttl_cache(ttl_seconds: int = 30) -> Callable[[F], F]:
    """Simple TTL cache decorator for tool status and ephemeral data.
    
    Args:
        ttl_seconds: Time-to-live in seconds for cached entries.
        
    Returns:
        Decorated function with TTL caching behavior.
        
    Example:
        @ttl_cache(ttl_seconds=60)
        def get_git_status(path: str) -> str:
            # Expensive operation
            return subprocess.check_output(["git", "status"], cwd=path)
    """
    def decorator(func: F) -> F:
        cache: dict[str, Any] = {}
        timestamps: dict[str, float] = {}
        
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Create cache key from function arguments
            key = str(args) + str(sorted(kwargs.items()))
            current_time = time.time()
            
            # Check if cache entry exists and is still valid
            if key in cache and current_time - timestamps[key] < ttl_seconds:
                return cache[key]
            
            # Compute and cache result
            result = func(*args, **kwargs)
            cache[key] = result
            timestamps[key] = current_time
            return result
        
        # Add cache management methods
        def cache_clear() -> None:
            """Clear all cached entries."""
            cache.clear()
            timestamps.clear()
        
        def cache_info() -> dict[str, Any]:
            """Get cache statistics."""
            return {
                "size": len(cache),
                "ttl_seconds": ttl_seconds,
                "keys": list(cache.keys()),
            }
        
        wrapper.cache_clear = cache_clear  # type: attr
        wrapper.cache_info = cache_info  # type: attr
        
        return wrapper  # type: return
    
    return decorator