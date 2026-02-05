"""DuggerLinkTools: Pydantic-powered standard library for the Dugger ecosystem."""

__version__ = "0.1.0"
__all__ = ["DuggerToolError", "ttl_cache", "DuggerProject"]

from .core.exceptions import DuggerToolError
from .utils.caching import ttl_cache
from .models.project import DuggerProject