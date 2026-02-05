# Conventional Commit Guide for Dugger Ecosystem

## Quick Reference

### Commit Types

| Type | Purpose | Example |
|-------|---------|---------|
| `feat` | New feature | `feat(trading): add moving average indicator` |
| `fix` | Bug fix | `fix(dlt): resolve Git state validation error` |
| `docs` | Documentation | `docs(readme): update installation instructions` |
| `style` | Formatting/linting | `style(dgt): fix code formatting with ruff` |
| `refactor` | Code restructuring | `refactor(core): simplify Git operations` |
| `perf` | Performance improvements | `perf(cache): optimize TTL cache strategy` |
| `test` | Test additions/fixes | `test(git): add GitState model validation` |
| `chore` | Maintenance tasks | `chore(deps): update pydantic to v2.12.0` |
| `ci` | CI/CD changes | `ci(github): add automated testing workflow` |
| `build` | Build system changes | `build(pyproject): update hatchling configuration` |
| `revert` | Revert previous commit | `revert: undo previous trading indicator changes` |
| `sys` | **Systemic fixes** | `sys(dlt): promote Git framework to ecosystem standard` |

### Common Scopes

| Scope | Description |
|-------|-------------|
| `dlt` | DuggerLinkTools (core library) |
| `dgt` | DuggerGitTools (Git operations) |
| `dbt` | DuggerBuildTools (build automation) |
| `phantom` | Phantom trading bot |
| `trading` | Trading-related components |
| `core` | Core functionality |
| `cli` | Command-line interfaces |
| `models` | Pydantic models |
| `utils` | Utility functions |
| `git` | Git operations |
| `docs` | Documentation |
| `tests` | Test suite |
| `config` | Configuration files |
| `deploy` | Deployment scripts |
| `infra` | Infrastructure |

### Format

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

## Examples

### Basic Commits
```
feat(trading): add RSI indicator for momentum trading
fix(dlt): resolve GitState validation for empty repositories
docs(readme): update quick start guide
chore(deps): update typer to v0.20.0
```

### Systemic Fixes (Special)
```
sys(dlt): promote Git framework to ecosystem standard
sys(core): implement universal caching strategy
sys(arch): migrate from scripts to Pydantic models
```

### Breaking Changes
```
feat(api)!: change GitState.commit_hash to full_hash

BREAKING CHANGE: The commit_hash field has been renamed to full_hash
to better reflect that it contains the complete commit hash.
```

### Complex Commits
```
perf(trading): optimize indicator calculations by 40%

Previously, each indicator was calculated independently, leading to
redundant data processing. This change implements a shared data
pipeline that processes market data once and distributes it to all
indicators.

Closes #123
```

## Usage with dlt-commit

The `dlt-commit` tool guides you through the process:

1. **Run the command**: `dlt-commit` or `python commit.py`
2. **Select type**: Choose from numbered list or enter type directly
3. **Enter scope**: Optional, use common scopes when appropriate
4. **Write description**: Imperative mood, max 50 characters
5. **Confirm**: Review and confirm the commit

## Best Practices

### 1. Use Imperative Mood
- ✅ `add feature` not `added feature`
- ✅ `fix bug` not `fixed bug`
- ✅ `update docs` not `updated docs`

### 2. Keep Description Concise
- ✅ `add RSI indicator` (19 chars)
- ❌ `add RSI indicator for momentum trading strategy` (47 chars)

### 3. Use Appropriate Scopes
- ✅ `feat(trading):` for trading features
- ✅ `fix(dlt):` for DuggerLinkTools fixes
- ✅ `chore(deps):` for dependency updates

### 4. Systemic Fixes Use `sys`
The `sys` type is reserved for changes that affect the entire ecosystem:
- Architecture changes
- Cross-project standardization
- Framework promotions
- Ecosystem-wide improvements

### 5. Link Issues When Relevant
```
fix(trading): resolve order execution timeout

Closes #45
```

## Station Quick Reference

Print this for your desk:

```
TYPES: feat, fix, docs, style, refactor, perf, test, chore, ci, build, revert, sys
SCOPES: dlt, dgt, dbt, phantom, trading, core, cli, models, utils, git
FORMAT: <type>[scope]: <imperative description>
SYSTEMIC: Use 'sys' for ecosystem-wide changes
```

## Migration from Legacy Messages

| Before | After |
|--------|-------|
| "Updated git operations" | `refactor(git): improve error handling` |
| "Fixed bug in trading" | `fix(trading): resolve order validation` |
| "Added new feature" | `feat(trading): add stop-loss functionality` |
| "System fix" | `sys(dlt): standardize Git state across ecosystem` |

## Automation Rules

The `dlt-commit` tool enforces:
- ✅ Conventional commit format
- ✅ Valid commit types
- ✅ Description length ≤ 50 characters
- ✅ Imperative mood in description
- ✅ Clean working directory before commit

This ensures consistent, professional commit messages across all 19+ projects in the Dugger ecosystem.