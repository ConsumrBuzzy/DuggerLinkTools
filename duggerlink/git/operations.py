"""Git operations for DuggerLinkTools ecosystem - Read-Only by default."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from ..core.exceptions import DuggerToolError
from ..utils.caching import ttl_cache


class GitOperations:
    """Read-First Git operations wrapper with caching for ecosystem-wide use.
    
    This class provides read-only Git operations that are safe to use
    across any project in the Dugger ecosystem. Write operations should
    be handled by DuggerGitTools (DGT) which is the designated operator.
    """
    
    def __init__(self, repo_path: Path) -> None:
        """Initialize Git operations for a specific repository.
        
        Args:
            repo_path: Path to the Git repository.
        """
        self.repo_path = repo_path
    
    @ttl_cache(ttl_seconds=30)
    def get_status(self) -> str:
        """Get git status in porcelain format.
        
        Returns:
            Git status output or empty string if not a git repo.
        """
        try:
            result = self._run_command(["status", "--porcelain"])
            return result.stdout.strip() if result.stdout.strip() else ""
        except Exception:
            return ""
    
    @ttl_cache(ttl_seconds=60)
    def get_current_branch(self) -> str:
        """Get current branch name.
        
        Returns:
            Current branch name or "unknown" if not a git repo.
        """
        try:
            result = self._run_command(["rev-parse", "--abbrev-ref", "HEAD"])
            return result.stdout.strip()
        except Exception:
            return "unknown"
    
    @ttl_cache(ttl_seconds=60)
    def get_last_commit_hash(self) -> str:
        """Get the hash of the last commit.
        
        Returns:
            Last commit hash or empty string if not a git repo.
        """
        try:
            result = self._run_command(["rev-parse", "HEAD"])
            return result.stdout.strip()
        except Exception:
            return ""
    
    @ttl_cache(ttl_seconds=30)
    def is_dirty(self, untracked_files: bool = True) -> bool:
        """Check if working directory is dirty.
        
        Args:
            untracked_files: Whether to consider untracked files.
            
        Returns:
            True if repository has changes, False otherwise.
        """
        try:
            cmd = ["status", "--porcelain"]
            if not untracked_files:
                cmd.append("--untracked-files=no")
            
            result = self._run_command(cmd)
            return bool(result.stdout.strip())
        except Exception:
            return False
    
    @ttl_cache(ttl_seconds=30)
    def get_untracked_files(self) -> list[str]:
        """Get list of untracked files.
        
        Returns:
            List of untracked file paths.
        """
        try:
            result = self._run_command(["status", "--porcelain", "--untracked-files=normal"])
            untracked = []
            
            for line in result.stdout.splitlines():
                if line.strip() and line.strip().startswith("??"):
                    untracked.append(line.strip()[3:].strip())
            
            return untracked
        except Exception:
            return []
    
    @ttl_cache(ttl_seconds=60)
    def get_changed_files(self, staged: bool = True) -> list[str]:
        """Get list of changed files.
        
        Args:
            staged: Whether to get staged (True) or unstaged (False) changes.
            
        Returns:
            List of changed file paths.
        """
        try:
            if staged:
                result = self._run_command(["diff", "--cached", "--name-only"])
            else:
                result = self._run_command(["diff", "--name-only"])
            
            if result.stdout.strip():
                return [f.strip() for f in result.stdout.splitlines() if f.strip()]
            
            # Fallback to unstaged if no staged changes
            if staged:
                return self.get_changed_files(staged=False)
            
            return []
        except Exception:
            return []
    
    @ttl_cache(ttl_seconds=60)
    def get_commit_count(self) -> int:
        """Get total commit count.
        
        Returns:
            Number of commits in repository or 0 if not a git repo.
        """
        try:
            result = self._run_command(["rev-list", "HEAD", "--count"])
            return int(result.stdout.strip() or 0)
        except Exception:
            return 0
    
    @ttl_cache(ttl_seconds=120)
    def get_remote_url(self, remote: str = "origin") -> str | None:
        """Get the URL of a remote repository.
        
        Args:
            remote: Name of the remote (default: "origin").
            
        Returns:
            Remote URL or None if not found.
        """
        try:
            result = self._run_command(["remote", "get-url", remote])
            return result.stdout.strip() if result.returncode == 0 else None
        except Exception:
            return None
    
    def is_git_repository(self) -> bool:
        """Check if the path is a Git repository.
        
        Returns:
            True if path is a Git repository, False otherwise.
        """
        try:
            self._run_command(["rev-parse", "--git-dir"])
            return True
        except Exception:
            return False
    
    def get_git_summary(self) -> dict[str, Any]:
        """Get a comprehensive summary of Git repository state.
        
        Returns:
            Dictionary with repository information.
        """
        if not self.is_git_repository():
            return {
                "is_git_repo": False,
                "branch": "none",
                "is_dirty": False,
                "commit_hash": "",
                "untracked_files": [],
                "commit_count": 0,
                "remote_url": None,
            }
        
        return {
            "is_git_repo": True,
            "branch": self.get_current_branch(),
            "is_dirty": self.is_dirty(),
            "commit_hash": self.get_last_commit_hash(),
            "untracked_files": self.get_untracked_files(),
            "commit_count": self.get_commit_count(),
            "remote_url": self.get_remote_url(),
        }
    
    def _run_command(
        self,
        args: list[str],
        check: bool = False,
        capture_output: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        """Run a git command in the repository directory.
        
        Args:
            args: Git command arguments.
            check: Whether to raise exception on non-zero exit.
            capture_output: Whether to capture stdout/stderr.
            
        Returns:
            Completed process result.
            
        Raises:
            DuggerToolError: If git command fails.
        """
        try:
            return subprocess.run(
                ["git"] + args,
                cwd=self.repo_path,
                check=check,
                capture_output=capture_output,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
        except subprocess.CalledProcessError as e:
            raise DuggerToolError(
                tool_name="git",
                command=["git"] + args,
                message=f"Git command failed: {e.stderr or str(e)}"
            )
        except FileNotFoundError:
            raise DuggerToolError(
                tool_name="git",
                command=["git"] + args,
                message="Git executable not found. Is Git installed?"
            )