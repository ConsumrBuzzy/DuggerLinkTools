#!/usr/bin/env python3
"""Self-validation script for DuggerLinkTools using its own DuggerProject model."""

from pathlib import Path
from duggerlink import DuggerProject


def main() -> None:
    """Validate DuggerLinkTools project structure."""
    project_root = Path(__file__).parent
    
    # Create DuggerProject model for DLT itself
    dlt_project = DuggerProject(
        name="DuggerLinkTools",
        path=project_root,
        capabilities=["python", "pydantic", "library", "ecosystem"],
        health_score=100,
        metadata={
            "version": "0.1.0",
            "description": "Pydantic-powered standard library for the Dugger ecosystem",
            "python_requires": ">=3.11",
        }
    )
    
    # Validate project structure
    print("=== DuggerLinkTools Self-Validation ===")
    print(f"Project: {dlt_project.name}")
    print(f"Path: {dlt_project.path}")
    print(f"Health Score: {dlt_project.health_score}")
    print(f"Capabilities: {', '.join(dlt_project.capabilities)}")
    
    # Check required directories
    required_dirs = ["duggerlink", "tests"]
    missing_dirs = []
    
    for dir_name in required_dirs:
        dir_path = project_root / dir_name
        if not dir_path.exists():
            missing_dirs.append(dir_name)
            dlt_project.health_score -= 10
    
    # Check required files
    required_files = ["pyproject.toml", "README.md"]
    missing_files = []
    
    for file_name in required_files:
        file_path = project_root / file_name
        if not file_path.exists():
            missing_files.append(file_name)
            dlt_project.health_score -= 15
    
    # Check core modules
    core_modules = [
        "duggerlink/__init__.py",
        "duggerlink/core/__init__.py",
        "duggerlink/core/exceptions.py",
        "duggerlink/utils/__init__.py",
        "duggerlink/utils/caching.py",
        "duggerlink/models/__init__.py",
        "duggerlink/models/project.py",
    ]
    missing_modules = []
    
    for module_path in core_modules:
        full_path = project_root / module_path
        if not full_path.exists():
            missing_modules.append(module_path)
            dlt_project.health_score -= 5
    
    # Report results
    print(f"\n=== Validation Results ===")
    print(f"Final Health Score: {dlt_project.health_score}")
    print(f"Status: {'✅ Healthy' if dlt_project.is_healthy() else '⚠️ Needs Attention'}")
    
    if missing_dirs:
        print(f"\n❌ Missing Directories: {', '.join(missing_dirs)}")
    
    if missing_files:
        print(f"\n❌ Missing Files: {', '.join(missing_files)}")
    
    if missing_modules:
        print(f"\n❌ Missing Modules: {', '.join(missing_modules)}")
    
    if not missing_dirs and not missing_files and not missing_modules:
        print("\n✅ All required components present!")
    
    # Display project summary
    print(f"\n=== Project Summary ===")
    summary = dlt_project.get_status_summary()
    for key, value in summary.items():
        print(f"{key.replace('_', ' ').title()}: {value}")
    
    # Test model functionality
    print(f"\n=== Model Functionality Test ===")
    print(f"Has 'python' capability: {dlt_project.has_capability('python')}")
    print(f"Has 'rust' capability: {dlt_project.has_capability('rust')}")
    
    dlt_project.add_capability("validation")
    print(f"Added 'validation' capability: {dlt_project.capabilities}")
    
    dlt_project.remove_capability("validation")
    print(f"Removed 'validation' capability: {dlt_project.capabilities}")
    
    print(f"\n🎉 Self-validation complete!")


if __name__ == "__main__":
    main()