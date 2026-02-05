#!/usr/bin/env python3
"""Git integration validation script for DuggerLinkTools."""

from pathlib import Path
from duggerlink import DuggerProject, GitState, GitOperations


def main() -> None:
    """Validate Git integration in DuggerLinkTools."""
    project_root = Path(__file__).parent
    
    print("=== DuggerLinkTools Git Integration Validation ===")
    print(f"Project Root: {project_root}")
    
    # Initialize Git operations
    git_ops = GitOperations(project_root)
    
    # Check if this is a Git repository
    is_git_repo = git_ops.is_git_repository()
    print(f"Is Git Repository: {is_git_repo}")
    
    if not is_git_repo:
        print("❌ Not a Git repository - skipping Git state validation")
        return
    
    # Get Git summary
    git_summary = git_ops.get_git_summary()
    print(f"\n=== Git Repository Summary ===")
    for key, value in git_summary.items():
        print(f"{key.replace('_', ' ').title()}: {value}")
    
    # Create GitState model
    git_state = GitState(**git_summary)
    print(f"\n=== GitState Model Validation ===")
    print(f"Branch: {git_state.branch}")
    print(f"Is Dirty: {git_state.is_dirty}")
    print(f"Commit Hash: {git_state.commit_hash[:8] if git_state.commit_hash else 'None'}")
    print(f"Untracked Files: {len(git_state.untracked_files)}")
    print(f"Commit Count: {git_state.commit_count}")
    
    # Test GitState methods
    print(f"\n=== GitState Methods Test ===")
    print(f"Has Changes: {git_state.has_changes()}")
    print(f"Is Clean: {git_state.is_clean()}")
    
    status_summary = git_state.get_status_summary()
    print(f"Status Summary: {status_summary}")
    
    branch_info = git_state.get_branch_info()
    print(f"Branch Info: {branch_info}")
    
    remote_info = git_state.get_remote_info()
    print(f"Remote Info: {remote_info}")
    
    # Create DuggerProject with Git state
    print(f"\n=== DuggerProject with Git Integration ===")
    project = DuggerProject(
        name="DuggerLinkTools",
        path=project_root,
        capabilities=["python", "pydantic", "library", "ecosystem", "git"],
        health_score=100,
        metadata={
            "version": "0.1.0",
            "description": "Pydantic-powered standard library for the Dugger ecosystem",
            "python_requires": ">=3.11",
        },
        git=git_state
    )
    
    # Validate project with Git state
    print(f"Project Name: {project.name}")
    print(f"Has Git Capability: {project.has_capability('git')}")
    print(f"Git State Available: {project.git is not None}")
    
    if project.git:
        print(f"Git Branch: {project.git.branch}")
        print(f"Git Is Clean: {project.git.is_clean()}")
    
    # Get comprehensive status summary
    full_summary = project.get_status_summary()
    print(f"\n=== Full Project Status Summary ===")
    for key, value in full_summary.items():
        print(f"{key}: {value}")
    
    # Test caching performance
    print(f"\n=== Caching Performance Test ===")
    import time
    
    # First call (cache miss)
    start_time = time.time()
    branch1 = git_ops.get_current_branch()
    first_call_time = time.time() - start_time
    
    # Second call (cache hit)
    start_time = time.time()
    branch2 = git_ops.get_current_branch()
    second_call_time = time.time() - start_time
    
    print(f"First call (cache miss): {first_call_time:.4f}s")
    print(f"Second call (cache hit): {second_call_time:.4f}s")
    
    if second_call_time > 0:
        print(f"Speed improvement: {first_call_time / second_call_time:.1f}x")
    else:
        print("Speed improvement: Too fast to measure (both calls < 1ms)")
    
    print(f"Results consistent: {branch1 == branch2}")
    
    # Test cache management
    print(f"\n=== Cache Management Test ===")
    cache_info = git_ops.get_current_branch.cache_info()  # type: attr
    print(f"Cache size: {cache_info['size']}")
    print(f"Cache TTL: {cache_info['ttl_seconds']}s")
    
    # Clear cache and test
    git_ops.get_current_branch.cache_clear()  # type: attr
    cache_info_after = git_ops.get_current_branch.cache_info()  # type: attr
    print(f"Cache size after clear: {cache_info_after['size']}")
    
    print(f"\n🎉 Git integration validation complete!")


if __name__ == "__main__":
    main()