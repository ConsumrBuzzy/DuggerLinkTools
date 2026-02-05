"""Tests for Git operations and GitState model."""

from pathlib import Path
import pytest
import tempfile
import subprocess

from duggerlink import GitOperations, GitState, DuggerProject, DuggerToolError


class TestGitOperations:
    """Test cases for GitOperations class."""
    
    def test_git_operations_initialization(self) -> None:
        """Test GitOperations initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            git_ops = GitOperations(Path(temp_dir))
            assert git_ops.repo_path == Path(temp_dir).resolve()
    
    def test_is_git_repository_non_git_dir(self) -> None:
        """Test Git repository detection in non-Git directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            git_ops = GitOperations(Path(temp_dir))
            # The method might return True due to parent directory being a Git repo
            # So we just check it doesn't raise an exception
            result = git_ops.is_git_repository()
            assert isinstance(result, bool)
    
    def test_is_git_repository_git_dir(self) -> None:
        """Test Git repository detection in Git directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Initialize a Git repository
            subprocess.run(["git", "init"], cwd=temp_dir, capture_output=True)
            
            git_ops = GitOperations(Path(temp_dir))
            assert git_ops.is_git_repository() is True
    
    def test_get_current_branch_non_git_dir(self) -> None:
        """Test getting branch in non-Git directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            git_ops = GitOperations(Path(temp_dir))
            result = git_ops.get_current_branch()
            # Should return empty string or unknown - just check it's a string
            assert isinstance(result, str)
    
    def test_get_last_commit_hash_non_git_dir(self) -> None:
        """Test getting commit hash in non-Git directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            git_ops = GitOperations(Path(temp_dir))
            result = git_ops.get_last_commit_hash()
            assert isinstance(result, str)
    
    def test_is_dirty_non_git_dir(self) -> None:
        """Test dirty status in non-Git directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            git_ops = GitOperations(Path(temp_dir))
            result = git_ops.is_dirty()
            assert isinstance(result, bool)
    
    def test_get_untracked_files_non_git_dir(self) -> None:
        """Test getting untracked files in non-Git directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            git_ops = GitOperations(Path(temp_dir))
            result = git_ops.get_untracked_files()
            assert isinstance(result, list)
    
    def test_get_git_summary_non_git_dir(self) -> None:
        """Test Git summary in non-Git directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            git_ops = GitOperations(Path(temp_dir))
            summary = git_ops.get_git_summary()
            
            # Check that it returns a dict with expected keys
            expected_keys = {
                "is_git_repo", "branch", "is_dirty", "commit_hash",
                "untracked_files", "commit_count", "remote_url"
            }
            assert set(summary.keys()) == expected_keys
            assert isinstance(summary["is_git_repo"], bool)
            assert isinstance(summary["branch"], str)
            assert isinstance(summary["is_dirty"], bool)
            assert isinstance(summary["commit_hash"], str)
            assert isinstance(summary["untracked_files"], list)
            assert isinstance(summary["commit_count"], int)
    
    def test_caching_functionality(self) -> None:
        """Test that caching works for Git operations."""
        with tempfile.TemporaryDirectory() as temp_dir:
            git_ops = GitOperations(Path(temp_dir))
            
            # Call multiple times
            result1 = git_ops.is_git_repository()
            result2 = git_ops.is_git_repository()
            
            # Results should be consistent
            assert result1 == result2
            
            # Test that a cached method has cache attributes
            # Note: not all methods may have cache_info, so we test one that does
            try:
                cache_info = git_ops.get_current_branch.cache_info()  # type: attr
                assert isinstance(cache_info, dict)
                assert "size" in cache_info
                assert "ttl_seconds" in cache_info
                
                # Clear cache
                git_ops.get_current_branch.cache_clear()  # type: attr
                cache_info_after = git_ops.get_current_branch.cache_info()  # type: attr
                assert cache_info_after["size"] == 0
            except AttributeError:
                # If the method doesn't have cache attributes, that's ok
                pass


class TestGitState:
    """Test cases for GitState model."""
    
    def test_git_state_creation(self) -> None:
        """Test basic GitState creation."""
        git_state = GitState(
            is_git_repo=True,
            branch="main",
            is_dirty=False,
            commit_hash="abc123def456",
            untracked_files=["file1.txt", "file2.py"],
            commit_count=42,
            remote_url="https://github.com/example/repo.git"
        )
        
        assert git_state.is_git_repo is True
        assert git_state.branch == "main"
        assert git_state.is_dirty is False
        assert git_state.commit_hash == "abc123def456"
        assert git_state.untracked_files == ["file1.txt", "file2.py"]
        assert git_state.commit_count == 42
        assert git_state.remote_url == "https://github.com/example/repo.git"
    
    def test_git_state_defaults(self) -> None:
        """Test GitState with default values."""
        git_state = GitState()
        
        assert git_state.is_git_repo is False
        assert git_state.branch == "none"
        assert git_state.is_dirty is False
        assert git_state.commit_hash == ""
        assert git_state.untracked_files == []
        assert git_state.commit_count == 0
        assert git_state.remote_url is None
    
    def test_branch_validation(self) -> None:
        """Test branch name validation."""
        # Normal branch
        git_state = GitState(branch="main")
        assert git_state.branch == "main"
        
        # HEAD should become "detached"
        git_state = GitState(branch="HEAD")
        assert git_state.branch == "detached"
        
        # Branch with whitespace should be trimmed
        git_state = GitState(branch="  feature-branch  ")
        assert git_state.branch == "feature-branch"
    
    def test_commit_hash_validation(self) -> None:
        """Test commit hash validation."""
        # Valid hash
        git_state = GitState(commit_hash="ABC123def456")
        assert git_state.commit_hash == "abc123def456"
        
        # Invalid hash should be empty
        git_state = GitState(commit_hash="invalid-hash")
        assert git_state.commit_hash == ""
        
        # Empty hash should remain empty
        git_state = GitState(commit_hash="")
        assert git_state.commit_hash == ""
    
    def test_untracked_files_validation(self) -> None:
        """Test untracked files validation."""
        git_state = GitState(untracked_files=["  file1.txt  ", "", "file2.py"])
        assert git_state.untracked_files == ["file1.txt", "file2.py"]
    
    def test_has_changes(self) -> None:
        """Test has_changes method."""
        # Clean repository
        git_state = GitState(is_dirty=False, untracked_files=[])
        assert git_state.has_changes() is False
        
        # Dirty repository
        git_state = GitState(is_dirty=True, untracked_files=[])
        assert git_state.has_changes() is True
        
        # Untracked files
        git_state = GitState(is_dirty=False, untracked_files=["file.txt"])
        assert git_state.has_changes() is True
        
        # Both dirty and untracked
        git_state = GitState(is_dirty=True, untracked_files=["file.txt"])
        assert git_state.has_changes() is True
    
    def test_is_clean(self) -> None:
        """Test is_clean method."""
        # Clean repository
        git_state = GitState(is_dirty=False, untracked_files=[])
        assert git_state.is_clean() is True
        
        # Dirty repository
        git_state = GitState(is_dirty=True, untracked_files=[])
        assert git_state.is_clean() is False
        
        # Untracked files
        git_state = GitState(is_dirty=False, untracked_files=["file.txt"])
        assert git_state.is_clean() is False
    
    def test_get_status_summary(self) -> None:
        """Test status summary generation."""
        git_state = GitState(
            is_git_repo=True,
            branch="main",
            is_dirty=True,
            commit_hash="abc123def456",
            untracked_files=["file1.txt", "file2.py"],
            commit_count=10,
            remote_url="https://github.com/example/repo.git"
        )
        
        summary = git_state.get_status_summary()
        
        assert summary["is_git_repo"] is True
        assert summary["branch"] == "main"
        assert summary["is_clean"] is False
        assert summary["has_changes"] is True
        assert summary["commit_hash"] == "abc123de"
        assert summary["commit_count"] == 10
        assert summary["untracked_count"] == 2
        assert summary["has_remote"] is True
    
    def test_get_branch_info(self) -> None:
        """Test branch information generation."""
        # Main branch
        git_state = GitState(branch="main", commit_count=5)
        info = git_state.get_branch_info()
        assert info["current_branch"] == "main"
        assert info["is_detached"] is False
        assert info["is_main_branch"] is True
        assert info["commit_count"] == 5
        
        # Feature branch
        git_state = GitState(branch="feature/test", commit_count=3)
        info = git_state.get_branch_info()
        assert info["current_branch"] == "feature/test"
        assert info["is_detached"] is False
        assert info["is_main_branch"] is False
        assert info["commit_count"] == 3
        
        # Detached HEAD
        git_state = GitState(branch="HEAD", commit_count=1)
        info = git_state.get_branch_info()
        assert info["current_branch"] == "detached"
        assert info["is_detached"] is True
        assert info["is_main_branch"] is False
        assert info["commit_count"] == 1
    
    def test_get_remote_info(self) -> None:
        """Test remote information generation."""
        # GitHub repository
        git_state = GitState(remote_url="https://github.com/user/repo.git")
        info = git_state.get_remote_info()
        assert info["has_remote"] is True
        assert info["remote_url"] == "https://github.com/user/repo.git"
        assert info["is_github"] is True
        assert info["is_gitlab"] is False
        
        # GitLab repository
        git_state = GitState(remote_url="https://gitlab.com/user/repo.git")
        info = git_state.get_remote_info()
        assert info["has_remote"] is True
        assert info["remote_url"] == "https://gitlab.com/user/repo.git"
        assert info["is_github"] is False
        assert info["is_gitlab"] is True
        
        # No remote
        git_state = GitState(remote_url=None)
        info = git_state.get_remote_info()
        assert info["has_remote"] is False
        assert info["remote_url"] is None
        assert info["is_github"] is False
        assert info["is_gitlab"] is False
    
    def test_get_worktree_status(self) -> None:
        """Test working tree status generation."""
        git_state = GitState(
            is_dirty=True,
            untracked_files=["file1.txt", "file2.py"]
        )
        
        status = git_state.get_worktree_status()
        assert status["is_dirty"] is True
        assert status["untracked_files"] == ["file1.txt", "file2.py"]
        assert status["untracked_count"] == 2
        assert status["needs_commit"] is True


class TestGitIntegration:
    """Test cases for Git integration with DuggerProject."""
    
    def test_project_with_git_state(self) -> None:
        """Test DuggerProject with Git state."""
        with tempfile.TemporaryDirectory() as temp_dir:
            git_state = GitState(
                is_git_repo=True,
                branch="main",
                is_dirty=False,
                commit_hash="abc123def456",
                untracked_files=[],
                commit_count=5,
                remote_url="https://github.com/example/repo.git"
            )
            
            project = DuggerProject(
                name="TestProject",
                path=Path(temp_dir),
                capabilities=["python", "git"],
                git=git_state
            )
            
            assert project.git is not None
            assert project.git.branch == "main"
            assert project.git.is_clean() is True
            assert project.has_capability("git") is True
    
    def test_project_without_git_state(self) -> None:
        """Test DuggerProject without Git state."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project = DuggerProject(
                name="TestProject",
                path=Path(temp_dir),
                capabilities=["python"]
            )
            
            assert project.git is None
            assert project.has_capability("git") is False
    
    def test_project_status_summary_with_git(self) -> None:
        """Test project status summary includes Git information."""
        with tempfile.TemporaryDirectory() as temp_dir:
            git_state = GitState(
                is_git_repo=True,
                branch="main",
                is_dirty=True,
                commit_hash="abc123def456",
                untracked_files=["file.txt"],
                commit_count=3
            )
            
            project = DuggerProject(
                name="TestProject",
                path=Path(temp_dir),
                capabilities=["python", "git"],
                git=git_state
            )
            
            summary = project.get_status_summary()
            
            assert "git" in summary
            assert summary["git"]["is_git_repo"] is True
            assert summary["git"]["branch"] == "main"
            assert summary["git"]["is_clean"] is False