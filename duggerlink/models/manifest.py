"""
Chrome Extension Manifest V3 models for DuggerLinkTools.

Pydantic models for validating Chrome Extension manifests and ensuring compliance.
"""

from enum import Enum
from typing import Dict, List, Optional, Union, Any

from pydantic import BaseModel, Field, validator


class ManifestVersion(str, Enum):
    """Supported manifest versions."""
    V3 = "3"


class Permission(str, Enum):
    """Standard Chrome extension permissions."""
    STORAGE = "storage"
    ACTIVE_TAB = "activeTab"
    SCRIPTING = "scripting"
    TABS = "tabs"
    BOOKMARKS = "bookmarks"
    HISTORY = "history"
    COOKIES = "cookies"
    WEB_NAVIGATION = "webNavigation"
    BACKGROUND = "background"
    UNLIMITED_STORAGE = "unlimitedStorage"
    NOTIFICATIONS = "notifications"
    ALARMS = "alarms"


class HostPermission(str, Enum):
    """Common host permission patterns."""
    ALL_URLS = "<all_urls>"
    HTTPS_ALL = "https://*/*"
    HTTP_ALL = "http://*/*"


class ContentScript(BaseModel):
    """Content script configuration."""
    matches: List[str] = Field(..., description="URL patterns for content script injection")
    js: Optional[List[str]] = Field(None, description="JavaScript files to inject")
    css: Optional[List[str]] = Field(None, description="CSS files to inject")
    run_at: Optional[str] = Field("document_idle", description="When to inject the script")
    
    @validator('run_at')
    def validate_run_at(cls, v):
        valid_values = ["document_idle", "document_start", "document_end"]
        if v not in valid_values:
            raise ValueError(f"run_at must be one of {valid_values}")
        return v


class WebAccessibleResource(BaseModel):
    """Web accessible resource configuration."""
    resources: List[str] = Field(..., description="Resource paths")
    matches: List[str] = Field(..., description="URL patterns where resources are accessible")


class Action(BaseModel):
    """Browser action configuration."""
    default_popup: Optional[str] = Field(None, description="Path to popup HTML file")
    default_title: Optional[str] = Field(None, description="Default title")
    default_icon: Optional[Union[str, Dict[str, str]]] = Field(None, description="Default icon")


class Background(BaseModel):
    """Background script configuration."""
    service_worker: str = Field(..., description="Path to service worker script")
    type: str = Field("module", description="Script type")
    
    @validator('type')
    def validate_type(cls, v):
        if v != "module":
            raise ValueError("Background type must be 'module' for Manifest V3")
        return v


class ContentSecurityPolicy(BaseModel):
    """Content Security Policy configuration."""
    extension_pages: str = Field(
        "script-src 'self'; object-src 'self'",
        description="CSP for extension pages"
    )


class ChromeManifestV3(BaseModel):
    """Chrome Extension Manifest V3 validation model."""
    
    manifest_version: ManifestVersion = Field(..., description="Manifest version")
    name: str = Field(..., min_length=1, max_length=45, description="Extension name")
    version: str = Field(..., pattern=r"^\d+(\.\d+){0,3}$", description="Version string")
    description: Optional[str] = Field(None, max_length=132, description="Extension description")
    
    # Permissions
    permissions: Optional[List[Union[Permission, str]]] = Field(
        default_factory=list,
        description="API permissions"
    )
    host_permissions: Optional[List[str]] = Field(
        default_factory=list,
        description="Host permissions"
    )
    
    # Background and content scripts
    background: Optional[Background] = Field(None, description="Background service worker")
    content_scripts: Optional[List[ContentScript]] = Field(
        default_factory=list,
        description="Content scripts"
    )
    
    # UI components
    action: Optional[Action] = Field(None, description="Browser action")
    icons: Optional[Dict[str, str]] = Field(None, description="Extension icons")
    
    # Resources
    web_accessible_resources: Optional[List[WebAccessibleResource]] = Field(
        default_factory=list,
        description="Web accessible resources"
    )
    
    # Security
    content_security_policy: Optional[ContentSecurityPolicy] = Field(
        None,
        description="Content Security Policy"
    )
    
    # Optional metadata
    author: Optional[str] = Field(None, description="Extension author")
    homepage_url: Optional[str] = Field(None, description="Homepage URL")
    
    @validator('permissions')
    def validate_permissions(cls, v):
        if v is None:
            return []
        
        # Validate known permissions
        known_permissions = {perm.value for perm in Permission}
        for perm in v:
            if isinstance(perm, str) and perm not in known_permissions:
                # Allow custom permissions but warn
                pass
        return v
    
    @validator('host_permissions')
    def validate_host_permissions(cls, v):
        if v is None:
            return []
        
        # Basic validation of host permission patterns
        for perm in v:
            if not any(pattern in perm for pattern in ["http://", "https://", "chrome://", "moz-extension://"]):
                if perm not in ["<all_urls>"]:
                    raise ValueError(f"Invalid host permission pattern: {perm}")
        return v
    
    @validator('icons')
    def validate_icons(cls, v):
        if v is None:
            return v
        
        # Validate icon sizes
        valid_sizes = ["16", "48", "128", "256", "512"]
        for size in v.keys():
            if size not in valid_sizes:
                raise ValueError(f"Invalid icon size: {size}. Valid sizes: {valid_sizes}")
        return v
    
    @validator('content_security_policy')
    def validate_csp(cls, v):
        if v is None:
            return v
        
        # Basic CSP validation - ensure 'unsafe-eval' is not used
        if "unsafe-eval" in v.extension_pages:
            raise ValueError("'unsafe-eval' is not allowed in extension_pages CSP")
        return v
    
    def get_required_permissions(self) -> List[str]:
        """Get list of required permissions for this manifest."""
        permissions = []
        
        if self.permissions:
            permissions.extend([str(p) for p in self.permissions])
        
        # Add implied permissions
        if self.content_scripts:
            permissions.append("activeTab")
        
        if self.background:
            permissions.append("background")
        
        return list(set(permissions))
    
    def get_host_permissions_summary(self) -> Dict[str, List[str]]:
        """Get summary of host permissions by type."""
        if not self.host_permissions:
            return {"all": [], "https": [], "http": [], "other": []}
        
        summary = {"all": [], "https": [], "http": [], "other": []}
        
        for perm in self.host_permissions:
            if perm == "<all_urls>":
                summary["all"].append(perm)
            elif perm.startswith("https://"):
                summary["https"].append(perm)
            elif perm.startswith("http://"):
                summary["http"].append(perm)
            else:
                summary["other"].append(perm)
        
        return summary
    
    def validate_for_store(self) -> List[str]:
        """Validate manifest for Chrome Web Store requirements.
        
        Returns:
            List of validation warnings/errors
        """
        warnings = []
        
        # Check required fields
        if not self.description:
            warnings.append("Description is required for Chrome Web Store")
        
        if not self.icons:
            warnings.append("Icons are required for Chrome Web Store")
        elif "128" not in self.icons:
            warnings.append("128x128 icon is required for Chrome Web Store")
        
        # Check permissions
        if self.host_permissions:
            for perm in self.host_permissions:
                if perm.startswith("http://"):
                    warnings.append(f"HTTP permission '{perm}' may require additional review")
        
        # Check CSP
        if not self.content_security_policy:
            warnings.append("Content Security Policy is recommended")
        
        return warnings


def validate_manifest_file(manifest_path: str) -> tuple[Optional[ChromeManifestV3], List[str]]:
    """Validate a manifest.json file against the V3 schema.
    
    Args:
        manifest_path: Path to manifest.json file
        
    Returns:
        Tuple of (validated_manifest, validation_errors)
    """
    from ..utils.io import safe_read
    import json
    
    errors = []
    manifest = None
    
    try:
        # Read and parse manifest
        content = safe_read(manifest_path)
        manifest_data = json.loads(content)
        
        # Validate with Pydantic
        manifest = ChromeManifestV3(**manifest_data)
        
        # Additional store validation
        store_warnings = manifest.validate_for_store()
        errors.extend(store_warnings)
        
    except FileNotFoundError:
        errors.append(f"Manifest file not found: {manifest_path}")
    except json.JSONDecodeError as e:
        errors.append(f"Invalid JSON in manifest: {e}")
    except Exception as e:
        errors.append(f"Validation error: {e}")
    
    return manifest, errors