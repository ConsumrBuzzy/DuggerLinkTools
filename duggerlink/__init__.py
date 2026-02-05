"""DuggerLinkTools - Shared infrastructure for the Dugger ecosystem."""

__version__ = "0.1.0"

__all__ = [
    "DuggerToolError",
    "ttl_cache",
    "DuggerProject",
    "GitState",
    "GitOperations",
    "IDESync",
    "TaskExtractor",
    "RetrofitEngine",
    "safe_read",
    "safe_write",
    "safe_copy",
    "ChromeManifestV3",
    "validate_manifest_file",
]

from .core.exceptions import DuggerToolError
from .git.operations import GitOperations
from .git.models import GitState
from .ide_sync import IDESync
from .models.project import DuggerProject
from .models.manifest import ChromeManifestV3, validate_manifest_file
from .retrofit_engine import RetrofitEngine
from .task_extractor import TaskExtractor
from .utils.caching import ttl_cache
from .utils.io import safe_read, safe_write, safe_copy