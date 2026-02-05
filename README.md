# DuggerLinkTools

Pydantic-powered standard library for the Dugger ecosystem.

## Overview

DuggerLinkTools (DLT) serves as the central DNA for the entire C:\GitHub ecosystem, providing:

- **Pydantic Models**: Standardized data validation across all projects
- **Core Utilities**: Caching, error handling, and common functionality
- **Project Schema**: Canonical representation of project metadata
- **Type Safety**: Full Python 3.11+ native type support

## Architecture

```
duggerlink/
├── core/           # Core exceptions and base classes
├── models/         # Pydantic data models
├── utils/          # Utility functions (caching, etc.)
└── __init__.py     # Public API exports
```

## Quick Start

### Installation

```bash
# Development installation
pip install -e .

# From local path (for linking)
pip install -e C:\Github\DuggerLinkTools
```

### Basic Usage

```python
from pathlib import Path
from duggerlink import DuggerProject, DuggerToolError, ttl_cache

# Create a project model
project = DuggerProject(
    name="MyProject",
    path=Path("/path/to/project"),
    capabilities=["python", "git"],
    health_score=95
)

# Use caching
@ttl_cache(ttl_seconds=60)
def get_project_status(path: str) -> str:
    # Expensive operation
    return "healthy"

# Handle errors
try:
    # Some tool operation
    pass
except DuggerToolError as e:
    print(f"Tool {e.tool_name} failed: {e.message}")
```

## Core Components

### DuggerProject Model

The canonical schema for project metadata:

```python
project = DuggerProject(
    name="MyProject",
    path=Path("/path/to/project"),
    capabilities=["python", "git", "trading"],
    health_score=100
)

# Check capabilities
if project.has_capability("git"):
    print("Project supports git")

# Health monitoring
if project.is_healthy(threshold=80):
    print("Project is healthy")
```

### TTL Caching

Simple time-to-live caching for expensive operations:

```python
from duggerlink import ttl_cache

@ttl_cache(ttl_seconds=30)
def get_git_status(path: str) -> str:
    # Expensive git operation
    return subprocess.check_output(["git", "status"], cwd=path)
```

### Error Handling

Standardized error reporting:

```python
from duggerlink import DuggerToolError

raise DuggerToolError(
    tool_name="git",
    command=["git", "push"],
    message="Failed to push to remote"
)
```

## Development

### Setup

```bash
# Clone and install
git clone <repository>
cd DuggerLinkTools
pip install -e ".[dev]"
```

### Testing

```bash
# Run tests
pytest

# Self-validation
python validate_self.py
```

### Code Quality

```bash
# Linting
ruff check .

# Type checking
mypy duggerlink/

# Format
ruff format .
```

## Integration Strategy

### Linking Projects

Use the `dlt-link` command to automatically install DuggerLinkTools in editable mode:

```bash
# From any project in C:\GitHub
dlt-link
```

This creates a local dependency without requiring PyPI publication.

### Migration Path

1. **Headlong Core Extraction**: Move `@ttl_cache` and `DuggerToolError` immediately
2. **Pydantic Schema First**: Define models before moving logic
3. **Gradual Migration**: Replace ad-hoc validation with Pydantic models
4. **Self-Validation**: Use DLT to validate DLT itself

## Design Principles

- **SOLID Architecture**: Single responsibility, open/closed, Liskov substitution
- **Bottom of Stack**: DLT never imports from DGT, DBT, or other ecosystem tools
- **Type Safety**: Native Python 3.11+ types throughout
- **Minimal Dependencies**: Only Pydantic and PyYAML as core dependencies
- **Office Portable**: Works across C:\GitHub without private PyPI

## Versioning

- Follows Semantic Versioning (SemVer)
- Python >=3.11 required
- Dynamic versioning via `pyproject.toml`

## License

MIT License - see LICENSE file for details.