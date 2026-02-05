"""Tests for TTL caching functionality."""

import time
from typing import Any

import pytest

from duggerlink import ttl_cache


class TestTTLCache:
    """Test cases for TTL cache decorator."""
    
    def test_cache_basic_functionality(self) -> None:
        """Test basic caching behavior."""
        call_count = 0
        
        @ttl_cache(ttl_seconds=1)
        def expensive_function(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x * 2
        
        # First call should execute function
        result1 = expensive_function(5)
        assert result1 == 10
        assert call_count == 1
        
        # Second call with same args should use cache
        result2 = expensive_function(5)
        assert result2 == 10
        assert call_count == 1  # Still only called once
        
        # Different args should execute function
        result3 = expensive_function(10)
        assert result3 == 20
        assert call_count == 2
    
    def test_cache_expiration(self) -> None:
        """Test cache expiration after TTL."""
        call_count = 0
        
        @ttl_cache(ttl_seconds=0.1)  # Very short TTL
        def time_sensitive() -> str:
            nonlocal call_count
            call_count += 1
            return f"call_{call_count}"
        
        # First call
        result1 = time_sensitive()
        assert result1 == "call_1"
        assert call_count == 1
        
        # Immediate second call should use cache
        result2 = time_sensitive()
        assert result2 == "call_1"
        assert call_count == 1
        
        # Wait for cache to expire
        time.sleep(0.2)
        
        # Next call should execute function again
        result3 = time_sensitive()
        assert result3 == "call_2"
        assert call_count == 2
    
    def test_cache_with_kwargs(self) -> None:
        """Test caching with keyword arguments."""
        call_count = 0
        
        @ttl_cache(ttl_seconds=1)
        def func_with_kwargs(a: int, b: int = 0) -> int:
            nonlocal call_count
            call_count += 1
            return a + b
        
        # Test different call patterns
        result1 = func_with_kwargs(5, b=3)
        assert result1 == 8
        assert call_count == 1
        
        # Same args should use cache
        result2 = func_with_kwargs(5, b=3)
        assert result2 == 8
        assert call_count == 1
        
        # Different kwargs should execute function
        result3 = func_with_kwargs(5, b=5)
        assert result3 == 10
        assert call_count == 2
        
        # Positional args should be treated differently
        result4 = func_with_kwargs(5, 3)
        assert result4 == 8
        assert call_count == 3  # Different call pattern
    
    def test_cache_clear(self) -> None:
        """Test cache clearing functionality."""
        call_count = 0
        
        @ttl_cache(ttl_seconds=10)
        def cached_func(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x * 2
        
        # Populate cache
        cached_func(5)
        cached_func(10)
        assert call_count == 2
        
        # Clear cache
        cached_func.cache_clear()  # type: attr
        
        # Calls should execute function again
        cached_func(5)
        cached_func(10)
        assert call_count == 4
    
    def test_cache_info(self) -> None:
        """Test cache information functionality."""
        @ttl_cache(ttl_seconds=10)
        def cached_func(x: int) -> int:
            return x * 2
        
        # Initial cache info
        info = cached_func.cache_info()  # type: attr
        assert info["size"] == 0
        assert info["ttl_seconds"] == 10
        assert info["keys"] == []
        
        # Add some entries
        cached_func(5)
        cached_func(10)
        
        info = cached_func.cache_info()  # type: attr
        assert info["size"] == 2
        assert len(info["keys"]) == 2
    
    def test_cache_preserves_function_attributes(self) -> None:
        """Test that cache decorator preserves function attributes."""
        @ttl_cache(ttl_seconds=1)
        def decorated_func(x: int) -> int:
            """Original function docstring."""
            return x * 2
        
        assert decorated_func.__name__ == "decorated_func"
        assert "Original function docstring" in decorated_func.__doc__
    
    def test_cache_with_different_types(self) -> None:
        """Test cache with various argument types."""
        call_count = 0
        
        @ttl_cache(ttl_seconds=1)
        def multi_type_func(
            s: str,
            i: int,
            f: float,
            b: bool,
            lst: list[int],
            d: dict[str, int]
        ) -> str:
            nonlocal call_count
            call_count += 1
            return f"{s}_{i}_{f}_{b}_{len(lst)}_{len(d)}"
        
        result1 = multi_type_func("test", 42, 3.14, True, [1, 2, 3], {"a": 1, "b": 2})
        assert result1 == "test_42_3.14_True_3_2"
        assert call_count == 1
        
        # Same args should use cache
        result2 = multi_type_func("test", 42, 3.14, True, [1, 2, 3], {"a": 1, "b": 2})
        assert result2 == "test_42_3.14_True_3_2"
        assert call_count == 1