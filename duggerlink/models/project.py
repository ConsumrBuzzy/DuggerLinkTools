"""Project models for DuggerLinkTools ecosystem."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .git import GitState


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
    git: GitState | None = Field(
        default=None,
        description="Git repository state information"
    )
    
    model_config = ConfigDict(
        extra="allow",  # Allow additional fields for backward compatibility (ADR-003)
    )
    
    @field_validator("path")
    @classmethod
    def validate_path(cls, value: Path) -> Path:
        """Ensure path is absolute."""
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
        summary = {
            "name": self.name,
            "path": str(self.path),
            "capabilities": self.capabilities,
            "health_score": self.health_score,
            "is_healthy": self.is_healthy(),
            "capability_count": len(self.capabilities),
        }
        
        # Add Git status if available
        if self.git:
            summary["git"] = self.git.get_status_summary()
        
        return summary
    
    def calculate_health_score(self) -> int:
        """Calculate project health score based on DLT standards.
        
        Scoring Formula:
        +40 points: DLT-Linked (dugger.yaml present)
        +30 points: Git Clean (No uncommitted changes)
        +20 points: README/ROADMAP present
        +10 points: All TODOs are tagged with a priority
        
        Returns:
            Health score (0-100)
        """
        score = 0
        
        # +40 points: DLT-Linked (dugger.yaml present)
        if (self.path / "dugger.yaml").exists():
            score += 40
        
        # +30 points: Git Clean (No uncommitted changes)
        if self.git and self.git.is_clean():
            score += 30
        
        # +20 points: README/ROADMAP present
        if (self.path / "README.md").exists() or (self.path / "ROADMAP.md").exists():
            score += 20
        
        # +10 points: All TODOs are tagged with a priority
        try:
            todos_tagged = self._check_todo_priorities()
            if todos_tagged:
                score += 10
        except Exception:
            # Don't fail health check for TODO scanning issues
            pass
        
        # Update the health_score field
        self.health_score = min(score, 100)  # Cap at 100
        return self.health_score
    
    def _check_todo_priorities(self) -> bool:
        """Check if all TODOs are tagged with a priority.
        
        Returns:
            True if all TODOs have priority tags, False otherwise
        """
        todo_pattern = re.compile(r'#\s*TODO\s*[:#]?\s*(high|medium|low)', re.IGNORECASE)
        untagged_todo_pattern = re.compile(r'#\s*TODO\s*(?![:#]?\s*(high|medium|low))', re.IGNORECASE)
        
        for file_path in self.path.rglob("*.py"):
            if file_path.is_file():
                try:
                    content = file_path.read_text(encoding='utf-8')
                    
                    # Check for untagged TODOs
                    if untagged_todo_pattern.search(content):
                        return False
                        
                except Exception:
                    # Skip files that can't be read
                    continue
        
        return True