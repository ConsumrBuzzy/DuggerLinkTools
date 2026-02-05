"""Git-related models for DuggerLinkTools ecosystem."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class GitState(BaseModel):
    """Pydantic model representing the Git state of a project.
    
    This model captures the essential Git repository information
    that any project in the Dugger ecosystem might need to understand
    about its own version control state.
    """
    
    is_git_repo: bool = Field(default=False, description="Whether the project is a Git repository")
    branch: str = Field(default="none", description="Current branch name")
    is_dirty: bool = Field(default=False, description="Whether working directory has uncommitted changes")
    commit_hash: str = Field(default="", description="Hash of the last commit")
    untracked_files: list[str] = Field(
        default_factory=list,
        description="List of untracked files in the repository"
    )
    commit_count: int = Field(default=0, ge=0, description="Total number of commits")
    remote_url: str | None = Field(default=None, description="URL of the origin remote")
    
    model_config = ConfigDict(
        extra="forbid",  # Prevent additional fields
    )
    
    @field_validator("branch")
    @classmethod
    def validate_branch(cls, value: str) -> str:
        """Normalize branch name."""
        if value == "HEAD":
            return "detached"
        return value.strip()
    
    @field_validator("commit_hash")
    @classmethod
    def validate_commit_hash(cls, value: str) -> str:
        """Normalize commit hash."""
        if not value:
            return ""
        # Ensure it's a valid-looking hash format
        if len(value) >= 7 and all(c in "0123456789abcdefABCDEF" for c in value):
            return value.lower()
        return ""
    
    @field_validator("untracked_files")
    @classmethod
    def validate_untracked_files(cls, value: list[str]) -> list[str]:
        """Normalize untracked file paths."""
        return [f.strip() for f in value if f.strip()]
    
    def has_changes(self) -> bool:
        """Check if repository has any changes (dirty or untracked files)."""
        return self.is_dirty or bool(self.untracked_files)
    
    def is_clean(self) -> bool:
        """Check if repository is clean (no changes)."""
        return not self.has_changes()
    
    def get_status_summary(self) -> dict[str, Any]:
        """Get a summary of Git repository status."""
        return {
            "is_git_repo": self.is_git_repo,
            "branch": self.branch,
            "is_clean": self.is_clean(),
            "has_changes": self.has_changes(),
            "commit_hash": self.commit_hash[:8] if self.commit_hash else "",
            "commit_count": self.commit_count,
            "untracked_count": len(self.untracked_files),
            "has_remote": self.remote_url is not None,
        }
    
    def get_branch_info(self) -> dict[str, Any]:
        """Get detailed branch information."""
        return {
            "current_branch": self.branch,
            "is_detached": self.branch == "detached",
            "is_main_branch": self.branch in ["main", "master", "develop"],
            "commit_count": self.commit_count,
        }
    
    def get_remote_info(self) -> dict[str, Any]:
        """Get remote repository information."""
        return {
            "has_remote": self.remote_url is not None,
            "remote_url": self.remote_url,
            "is_github": "github.com" in (self.remote_url or ""),
            "is_gitlab": "gitlab" in (self.remote_url or ""),
        }
    
    def get_worktree_status(self) -> dict[str, Any]:
        """Get working tree status information."""
        return {
            "is_dirty": self.is_dirty,
            "untracked_files": self.untracked_files,
            "untracked_count": len(self.untracked_files),
            "needs_commit": self.has_changes(),
        }