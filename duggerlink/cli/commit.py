"""Universal commit CLI for DuggerLinkTools ecosystem."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any

import typer

from ..core.exceptions import DuggerToolError
from ..git.operations import GitOperations
from ..models.git import GitState
from ..models.project import DuggerProject


# Conventional commit types with descriptions
COMMIT_TYPES = {
    "feat": "A new feature",
    "fix": "A bug fix",
    "docs": "Documentation only changes",
    "style": "Changes that do not affect the meaning of the code (formatting, etc.)",
    "refactor": "A code change that neither fixes a bug nor adds a feature",
    "perf": "A code change that improves performance",
    "test": "Adding missing tests or correcting existing tests",
    "chore": "Maintenance tasks, dependency updates, etc.",
    "ci": "Changes to our CI configuration files and scripts",
    "build": "Changes that affect the build system or external dependencies",
    "revert": "Reverts a previous commit",
    "sys": "Systemic fixes affecting the entire ecosystem",
}

# Common scopes for the Dugger ecosystem
COMMON_SCOPES = [
    "dlt", "dgt", "dbt", "phantom", "trading", "core", "cli", "models", 
    "utils", "git", "docs", "tests", "config", "deploy", "infra"
]

app = typer.Typer(
    help="Universal commit tool for the Dugger ecosystem",
    no_args_is_help=True,
)


def get_project_context() -> DuggerProject:
    """Get project context for the current directory."""
    current_path = Path.cwd()
    
    # Detect project capabilities
    capabilities = []
    
    # Check for Python
    if (current_path / "pyproject.toml").exists() or (current_path / "requirements.txt").exists():
        capabilities.append("python")
    
    # Check for Git
    git_ops = GitOperations(current_path)
    if git_ops.is_git_repository():
        capabilities.append("git")
    
    # Check for trading indicators
    if any((current_path / "indicators").glob("*.py")):
        capabilities.append("trading")
    
    # Get Git state if available
    git_state = None
    if git_ops.is_git_repository():
        git_summary = git_ops.get_git_summary()
        git_state = GitState(**git_summary)
    
    # Determine project name from path
    project_name = current_path.name
    
    return DuggerProject(
        name=project_name,
        path=current_path,
        capabilities=capabilities,
        git=git_state
    )


def prompt_commit_type() -> str:
    """Prompt user for commit type."""
    print("\n🎯 Select commit type:")
    for i, (commit_type, description) in enumerate(COMMIT_TYPES.items(), 1):
        print(f"  {i:2d}. {commit_type:<8} - {description}")
    
    while True:
        try:
            choice = input("\nEnter choice (1-12): ").strip()
            if choice.isdigit():
                choice_num = int(choice)
                if 1 <= choice_num <= len(COMMIT_TYPES):
                    return list(COMMIT_TYPES.keys())[choice_num - 1]
            # Allow direct type input
            if choice in COMMIT_TYPES:
                return choice
            print(f"❌ Invalid choice. Please enter 1-{len(COMMIT_TYPES)} or a valid type.")
        except (ValueError, KeyboardInterrupt):
            print("\n❌ Invalid input. Please try again.")


def prompt_scope(project: DuggerProject) -> str:
    """Prompt user for commit scope."""
    print(f"\n📁 Enter scope (optional):")
    print(f"Common scopes: {', '.join(COMMON_SCOPES)}")
    print(f"Project name: {project.name}")
    
    while True:
        scope = input("Scope (press Enter to skip): ").strip()
        if not scope:
            return ""
        if scope.replace("-", "").replace("_", "").isalnum():
            return scope.lower()
        print("❌ Scope must contain only letters, numbers, hyphens, and underscores.")


def prompt_description() -> str:
    """Prompt user for commit description."""
    print("\n📝 Enter commit description:")
    print("Use the imperative mood (e.g., 'add feature' not 'added feature')")
    
    while True:
        description = input("Description: ").strip()
        if description:
            if len(description) <= 50:
                return description.lower()
            else:
                print("⚠️  Description too long (max 50 chars). Please shorten:")
        else:
            print("❌ Description cannot be empty.")


def format_commit_message(commit_type: str, scope: str, description: str) -> str:
    """Format conventional commit message."""
    if scope:
        return f"{commit_type}({scope}): {description}"
    return f"{commit_type}: {description}"


def stage_all_changes(git_ops: GitOperations) -> bool:
    """Stage all changes for commit."""
    try:
        # Use git add . to stage all changes
        result = subprocess.run(
            ["git", "add", "."],
            cwd=git_ops.repo_path,
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except Exception:
        return False


def create_commit(message: str) -> bool:
    """Create commit with the given message."""
    try:
        result = subprocess.run(
            ["git", "commit", "-m", message],
            cwd=Path.cwd(),
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except Exception:
        return False


def display_git_status(project: DuggerProject) -> None:
    """Display current Git status."""
    if not project.git:
        print("❌ Not a Git repository")
        return
    
    print(f"\n📊 Git Status for {project.name}")
    print(f"   Branch: {project.git.branch}")
    print(f"   Clean: {'✅' if project.git.is_clean() else '❌'}")
    print(f"   Dirty: {'✅' if project.git.is_dirty else '❌'}")
    print(f"   Untracked files: {len(project.git.untracked_files)}")
    print(f"   Commit count: {project.git.commit_count}")
    
    if project.git.remote_url:
        print(f"   Remote: {project.git.remote_url}")
    
    if project.git.untracked_files:
        print(f"\n📋 Untracked files:")
        for file in project.git.untracked_files[:5]:  # Show first 5
            print(f"   - {file}")
        if len(project.git.untracked_files) > 5:
            print(f"   ... and {len(project.git.untracked_files) - 5} more")


@app.command()
def commit(
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Show what would be committed without actually committing"),
    status: bool = typer.Option(False, "--status", "-s", help="Show current Git status only"),
) -> None:
    """Universal commit command for the Dugger ecosystem."""
    
    # Get project context
    project = get_project_context()
    
    # Show status if requested
    if status:
        display_git_status(project)
        return
    
    # Check if this is a Git repository
    if not project.git:
        print("❌ This directory is not a Git repository")
        sys.exit(1)
    
    # Display current status
    display_git_status(project)
    
    # Check if there are changes to commit
    if project.git.is_clean():
        print("\n✅ Working directory is clean - nothing to commit")
        print("💡 Use --status to see detailed information")
        sys.exit(0)
    
    if dry_run:
        print("\n🔍 Dry run mode - no changes will be made")
        return
    
    # Get commit information
    print(f"\n🚀 Creating commit for {project.name}")
    
    commit_type = prompt_commit_type()
    scope = prompt_scope(project)
    description = prompt_description()
    
    # Format commit message
    commit_message = format_commit_message(commit_type, scope, description)
    
    print(f"\n📄 Commit message: {commit_message}")
    
    # Confirm
    confirm = input("\n✅ Proceed with commit? [y/N]: ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("❌ Commit cancelled")
        sys.exit(0)
    
    # Stage all changes
    print("\n📦 Staging changes...")
    git_ops = GitOperations(project.path)
    if not stage_all_changes(git_ops):
        print("❌ Failed to stage changes")
        sys.exit(1)
    
    # Create commit
    print("📝 Creating commit...")
    if create_commit(commit_message):
        print(f"✅ Commit created successfully!")
        print(f"   Message: {commit_message}")
        
        # Verify commit was created
        git_summary = git_ops.get_git_summary()
        if git_summary["commit_hash"]:
            print(f"   Hash: {git_summary['commit_hash'][:8]}")
    else:
        print("❌ Failed to create commit")
        sys.exit(1)


@app.command()
def status() -> None:
    """Show detailed Git status for the current project."""
    project = get_project_context()
    display_git_status(project)


def main() -> None:
    """Main entry point for the commit CLI."""
    app()


def commit_main() -> None:
    """Entry point for pyproject.toml script definition."""
    main()


if __name__ == "__main__":
    main()