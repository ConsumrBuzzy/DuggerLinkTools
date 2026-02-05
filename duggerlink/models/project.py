"""Project models for DuggerLinkTools ecosystem."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, field_validator


class DuggerProject(BaseModel):
    """Pydantic model representing a project in the Dugger ecosystem.
    
    This model serves as the canonical schema for project metadata
    across all Dugger tools and automation systems.
    """
    
    name: str = Field(..., description="Project name")
    path: Path = Field(..., description="Absolute path to project root")
    capabilities: list[str] = Field(
        default_factory=list,
        description="Project capabilities (e.g., 'git', 'python', 'trading')"
    )
    health_score: int = Field(
        default=100,
        ge=0,
        le=100,
        description="Project health score (0-100)"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional project metadata"
    )
    
    @field_validator("path")
    @classmethod
    def validate_path(cls, value: Path) -> Path:
        """Ensure path is absolute and exists."""
        if not value.is_absolute():
            raise ValueError("Project path must be absolute")
        return value.resolve()
    
    @field_validator("capabilities")
    @classmethod
    def validate_capabilities(cls, value: list[str]) -> list[str]:
        """Normalize capabilities to lowercase."""
        return [cap.lower() for cap in value]
    
    @field_validator("health_score")
    @classmethod
    def validate_health_score(cls, value: int) -> int:
        """Ensure health score is within valid range."""
        if not 0 <= value <= 100:
            raise ValueError("Health score must be between 0 and 100")
        return value
    
    def has_capability(self, capability: str) -> bool:
        """Check if project has a specific capability."""
        return capability.lower() in self.capabilities
    
    def add_capability(self, capability: str) -> None:
        """Add a capability to the project."""
        cap = capability.lower()
        if cap not in self.capabilities:
            self.capabilities.append(cap)
    
    def remove_capability(self, capability: str) -> None:
        """Remove a capability from the project."""
        cap = capability.lower()
        if cap in self.capabilities:
            self.capabilities.remove(cap)
    
    def is_healthy(self, threshold: int = 80) -> bool:
        """Check if project health meets threshold."""
        return self.health_score >= threshold
    
    def get_status_summary(self) -> dict[str, Any]:
        """Get a summary of project status."""
        return {
            "name": self.name,
            "path": str(self.path),
            "capabilities": self.capabilities,
            "health_score": self.health_score,
            "is_healthy": self.is_healthy(),
            "capability_count": len(self.capabilities),
        }
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            Path: lambda v: str(v),
        }
        extra = "forbid"  # Prevent additional fields