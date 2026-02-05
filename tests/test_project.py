"""Tests for DuggerProject model."""

from pathlib import Path
import pytest

from duggerlink import DuggerProject, DuggerToolError


class TestDuggerProject:
    """Test cases for DuggerProject model."""
    
    def test_project_creation(self) -> None:
        """Test basic project creation."""
        project = DuggerProject(
            name="TestProject",
            path=Path("/tmp/test"),
            capabilities=["python", "git"],
            health_score=95
        )
        
        assert project.name == "TestProject"
        assert project.path == Path("/tmp/test").resolve()
        assert project.capabilities == ["python", "git"]
        assert project.health_score == 95
    
    def test_capability_normalization(self) -> None:
        """Test capability normalization to lowercase."""
        project = DuggerProject(
            name="TestProject",
            path=Path("/tmp/test"),
            capabilities=["Python", "GIT", "Trading"]
        )
        
        assert project.capabilities == ["python", "git", "trading"]
    
    def test_path_validation(self) -> None:
        """Test path validation requires absolute path."""
        with pytest.raises(ValueError, match="Project path must be absolute"):
            DuggerProject(
                name="TestProject",
                path=Path("relative/path"),
                capabilities=["python"]
            )
    
    def test_health_score_validation(self) -> None:
        """Test health score validation."""
        # Valid scores
        DuggerProject(name="Test", path=Path("/tmp"), health_score=0)
        DuggerProject(name="Test", path=Path("/tmp"), health_score=100)
        
        # Invalid scores
        with pytest.raises(ValueError, match="Health score must be between 0 and 100"):
            DuggerProject(name="Test", path=Path("/tmp"), health_score=-1)
        
        with pytest.raises(ValueError, match="Health score must be between 0 and 100"):
            DuggerProject(name="Test", path=Path("/tmp"), health_score=101)
    
    def test_has_capability(self) -> None:
        """Test capability checking."""
        project = DuggerProject(
            name="TestProject",
            path=Path("/tmp/test"),
            capabilities=["python", "git"]
        )
        
        assert project.has_capability("python") is True
        assert project.has_capability("PYTHON") is True  # Case insensitive
        assert project.has_capability("rust") is False
    
    def test_add_capability(self) -> None:
        """Test adding capabilities."""
        project = DuggerProject(
            name="TestProject",
            path=Path("/tmp/test"),
            capabilities=["python"]
        )
        
        project.add_capability("git")
        assert "git" in project.capabilities
        
        # Test case normalization
        project.add_capability("RUST")
        assert "rust" in project.capabilities
        
        # Test duplicate handling
        project.add_capability("python")
        assert project.capabilities.count("python") == 1
    
    def test_remove_capability(self) -> None:
        """Test removing capabilities."""
        project = DuggerProject(
            name="TestProject",
            path=Path("/tmp/test"),
            capabilities=["python", "git", "rust"]
        )
        
        project.remove_capability("git")
        assert "git" not in project.capabilities
        assert "python" in project.capabilities
        assert "rust" in project.capabilities
        
        # Test case insensitive removal
        project.remove_capability("PYTHON")
        assert "python" not in project.capabilities
    
    def test_is_healthy(self) -> None:
        """Test health checking."""
        project = DuggerProject(
            name="TestProject",
            path=Path("/tmp/test"),
            health_score=85
        )
        
        assert project.is_healthy() is True  # Default threshold 80
        assert project.is_healthy(threshold=85) is True
        assert project.is_healthy(threshold=90) is False
        
        # Edge cases
        project.health_score = 80
        assert project.is_healthy(threshold=80) is True
        
        project.health_score = 79
        assert project.is_healthy(threshold=80) is False
    
    def test_get_status_summary(self) -> None:
        """Test status summary generation."""
        project = DuggerProject(
            name="TestProject",
            path=Path("/tmp/test"),
            capabilities=["python", "git"],
            health_score=90
        )
        
        summary = project.get_status_summary()
        
        assert summary["name"] == "TestProject"
        assert summary["path"] == str(Path("/tmp/test").resolve())
        assert summary["capabilities"] == ["python", "git"]
        assert summary["health_score"] == 90
        assert summary["is_healthy"] is True
        assert summary["capability_count"] == 2
    
    def test_metadata_handling(self) -> None:
        """Test metadata field handling."""
        metadata = {"version": "1.0.0", "author": "Test Author"}
        project = DuggerProject(
            name="TestProject",
            path=Path("/tmp/test"),
            metadata=metadata
        )
        
        assert project.metadata == metadata
        assert project.metadata["version"] == "1.0.0"


class TestDuggerToolError:
    """Test cases for DuggerToolError."""
    
    def test_error_creation(self) -> None:
        """Test basic error creation."""
        error = DuggerToolError(
            tool_name="git",
            command=["git", "push"],
            message="Failed to push"
        )
        
        assert error.tool_name == "git"
        assert error.command == ["git", "push"]
        assert error.message == "Failed to push"
        assert str(error) == "git: Failed to push"
    
    def test_error_repr(self) -> None:
        """Test error representation."""
        error = DuggerToolError(
            tool_name="git",
            command=["git", "push"],
            message="Failed to push"
        )
        
        expected = "DuggerToolError(tool_name='git', command=['git', 'push'], message='Failed to push')"
        assert repr(error) == expected