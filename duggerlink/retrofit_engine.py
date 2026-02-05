"""
Retrofit Engine - Project assimilation logic promoted to DuggerLinkTools

Allows upgrading existing projects to DLT standards without full recreation.
Injects missing DLT DNA into existing directories.
"""

from pathlib import Path
from typing import Dict, Any
import shutil
import subprocess

from loguru import logger

from .models.project import DuggerProject
from .ide_sync import IDESync
from .task_extractor import TaskExtractor


class RetrofitEngine:
    """Engine for retrofitting existing projects with DLT DNA.
    
    Upgrades existing directories to full DLT compliance:
    - Injects missing pyproject.toml
    - Creates/validates dugger.yaml
    - Adds standardized .gitignore
    - Sets up IDE sync
    - Initializes Git if needed
    """

    def __init__(self, project_path: Path):
        """Initialize RetrofitEngine.
        
        Args:
            project_path: Path to existing project directory
        """
        self.project_path = project_path
        self.logger = logger.bind(component="RetrofitEngine")
        self.ide_sync = IDESync(project_path)
        self.task_extractor = TaskExtractor(project_path)

    def assess_project(self) -> Dict[str, Any]:
        """Assess current project state and missing components.
        
        Returns:
            Assessment dictionary with missing items
        """
        assessment = {
            "project_path": self.project_path,
            "has_git": False,
            "has_pyproject": False,
            "has_dugger_yaml": False,
            "has_gitignore": False,
            "has_ide_sync": False,
            "missing_components": [],
            "existing_components": [],
        }

        # Check Git
        if (self.project_path / ".git").exists():
            assessment["has_git"] = True
            assessment["existing_components"].append("git")
        else:
            assessment["missing_components"].append("git")

        # Check pyproject.toml
        if (self.project_path / "pyproject.toml").exists():
            assessment["has_pyproject"] = True
            assessment["existing_components"].append("pyproject.toml")
        else:
            assessment["missing_components"].append("pyproject.toml")

        # Check dugger.yaml
        if (self.project_path / "dugger.yaml").exists():
            assessment["has_dugger_yaml"] = True
            assessment["existing_components"].append("dugger.yaml")
        else:
            assessment["missing_components"].append("dugger.yaml")

        # Check .gitignore
        if (self.project_path / ".gitignore").exists():
            assessment["has_gitignore"] = True
            assessment["existing_components"].append(".gitignore")
        else:
            assessment["missing_components"].append(".gitignore")

        # Check IDE sync files
        ide_files = [".cursorrules", ".windsurfrules", ".ai-rules"]
        has_any_ide = any((self.project_path / f).exists() for f in ide_files)
        if has_any_ide:
            assessment["has_ide_sync"] = True
            assessment["existing_components"].append("ide_sync")
        else:
            assessment["missing_components"].append("ide_sync")

        self.logger.info(f"Project assessment: {len(assessment['existing_components'])} existing, {len(assessment['missing_components'])} missing")
        return assessment

    def inject_pyproject_toml(self, project_name: str = None) -> bool:
        """Inject pyproject.toml if missing.
        
        Args:
            project_name: Optional project name (defaults to directory name)
            
        Returns:
            True if injected/updated, False if skipped
        """
        target_path = self.project_path / "pyproject.toml"
        
        if target_path.exists():
            self.logger.info("pyproject.toml already exists, skipping injection")
            return False

        if project_name is None:
            project_name = self.project_path.name

        # Generate basic pyproject.toml
        content = f"""[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "{project_name}"
version = "0.1.0"
description = "{project_name} - Upgraded to DuggerLinkTools standards"
authors = [{{name = "PyPro", email = "pypro@dugger.com"}}]
license = {{text = "MIT"}}
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "duggerlink-tools",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
]

[tool.black]
line-length = 88
target-version = ['py311']

[tool.ruff]
target-version = "py311"
line-length = 88
select = ["E", "F", "W", "I", "N", "UP", "B", "A", "C4", "DTZ", "T10", "EM", "ISC", "ICN", "G", "PIE", "T20", "PYI", "PT", "Q", "RSE", "RET", "SIM", "TID", "TCH", "ARG", "PTH", "ERA", "PGH", "PL", "TRY", "NPY", "RUF"]
ignore = ["E501"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "--cov=src --cov-report=html --cov-report=term-missing"
"""

        target_path.write_text(content)
        self.logger.info(f"Injected pyproject.toml for {project_name}")
        return True

    def inject_dugger_yaml(self, project_name: str = None) -> bool:
        """Inject/validate dugger.yaml.
        
        Args:
            project_name: Optional project name
            
        Returns:
            True if injected/updated, False if validated existing
        """
        target_path = self.project_path / "dugger.yaml"
        
        if project_name is None:
            project_name = self.project_path.name

        if target_path.exists():
            # Validate existing file
            try:
                project_data = DuggerProject.from_file(target_path)
                self.logger.info(f"Existing dugger.yaml validated for {project_data.name}")
                return False
            except Exception as e:
                self.logger.warning(f"Existing dugger.yaml invalid, recreating: {e}")
                # Backup and recreate
                backup_path = target_path.with_suffix(".yaml.backup")
                shutil.move(target_path, backup_path)
                self.logger.info(f"Backed up invalid dugger.yaml to {backup_path}")

        # Generate new dugger.yaml
        content = f"""# DuggerLinkTools Project Configuration
# Generated by RetrofitEngine

project:
  name: "{project_name}"
  version: "0.1.0"
  description: "{project_name} - Upgraded to DuggerLinkTools standards"
  template_type: "retrofit"
  retrofitted_at: "{{ ansible_date_time.iso8601 if ansible_date_time is defined else 'TBD' }}"
  
metadata:
  author: "PyPro"
  email: "pypro@dugger.com"
  license: "MIT"
  python_version: ">=3.11"
  
dependencies:
  core:
    - "duggerlink-tools"
  
structure:
  src_dir: "src"
  tests_dir: "tests"
  docs_dir: "docs"
  
git:
  auto_init: true
  initial_commit_message: "chore: retrofit {project_name} to DLT standards"
  
quality:
  formatter: "black"
  linter: "ruff"
  test_runner: "pytest"
"""

        target_path.write_text(content)
        self.logger.info(f"Injected dugger.yaml for {project_name}")
        return True

    def inject_gitignore(self) -> bool:
        """Inject standardized .gitignore if missing.
        
        Returns:
            True if injected, False if skipped
        """
        target_path = self.project_path / ".gitignore"
        
        if target_path.exists():
            self.logger.info(".gitignore already exists, skipping injection")
            return False

        content = """# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/
cover/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
.pybuilder/
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
.python-version

# pipenv
Pipfile.lock

# poetry
poetry.lock

# pdm
.pdm.toml

# PEP 582
__pypackages__/

# Celery stuff
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# pytype static type analyzer
.pytype/

# Cython debug symbols
cython_debug/

# PyCharm
.idea/

# VS Code
.vscode/

# macOS
.DS_Store

# Windows
Thumbs.db
ehthumbs.db
Desktop.ini

# DuggerLinkTools specific
.dugger_cache/
.dlt_temp/
"""

        target_path.write_text(content)
        self.logger.info("Injected standardized .gitignore")
        return True

    def initialize_git_if_needed(self) -> bool:
        """Initialize Git repository if missing.
        
        Returns:
            True if initialized, False if skipped
        """
        if (self.project_path / ".git").exists():
            self.logger.info("Git repository already exists, skipping initialization")
            return False

        try:
            subprocess.run(
                ["git", "init"],
                cwd=self.project_path,
                check=True,
                capture_output=True,
            )
            self.logger.info("Initialized Git repository")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize Git: {e}")
            return False

    def sync_ide_configurations(self, overwrite: bool = False) -> bool:
        """Sync IDE configurations.
        
        Args:
            overwrite: Whether to overwrite existing IDE files
            
        Returns:
            True if any sync occurred, False if all skipped
        """
        results = self.ide_sync.sync_all_ides(overwrite=overwrite)
        
        # Check if any actual changes occurred
        any_changes = any(r.created or r.updated for r in results)
        
        if any_changes:
            self.logger.info("IDE configurations synced")
        else:
            self.logger.info("All IDE configurations already exist, skipping sync")
        
        return any_changes

    def generate_roadmap_seed(self) -> bool:
        """Generate initial ROADMAP.md with extracted TODOs.
        
        Returns:
            True if generated, False if skipped
        """
        roadmap_path = self.project_path / "docs" / "ROADMAP.md"
        
        # Create docs directory if needed
        roadmap_path.parent.mkdir(exist_ok=True)
        
        if roadmap_path.exists():
            self.logger.info("ROADMAP.md already exists, skipping generation")
            return False

        # Extract existing TODOs
        annotations = self.task_extractor.scan_project()
        
        # Generate roadmap content
        content = f"""# {self.project_path.name} Roadmap

**Generated by DuggerLinkTools RetrofitEngine**

## Project Overview

This project has been retrofitted to DuggerLinkTools standards. The roadmap below captures the current state and next steps based on extracted TODOs.

## Current State

- **Total Annotations**: {len(annotations)}
- **DLT Compliance**: [✓] Upgraded
- **Git Integration**: [✓] Initialized
- **IDE Sync**: [✓] Configured

## Immediate Tasks

"""
        
        # Group TODOs by type
        by_tag = {}
        for ann in annotations:
            if ann.tag_type not in by_tag:
                by_tag[ann.tag_type] = []
            by_tag[ann.tag_type].append(ann)

        # Add FIXME items first (highest priority)
        if "FIXME" in by_tag:
            content += "### 🔥 Critical Fixes\n\n"
            for ann in by_tag["FIXME"]:
                rel_path = ann.file_path.relative_to(self.project_path)
                content += f"- [ ] {ann.message} (`{rel_path}:{ann.line_number}`)\n"
            content += "\n"

        # Add TODO items
        if "TODO" in by_tag:
            content += "### 📋 Development Tasks\n\n"
            for ann in by_tag["TODO"]:
                rel_path = ann.file_path.relative_to(self.project_path)
                content += f"- [ ] {ann.message} (`{rel_path}:{ann.line_number}`)\n"
            content += "\n"

        # Add other items
        other_tags = [tag for tag in by_tag.keys() if tag not in ["FIXME", "TODO"]]
        if other_tags:
            content += "### 📝 Other Notes\n\n"
            for tag in sorted(other_tags):
                content += f"#### {tag}\n\n"
                for ann in by_tag[tag]:
                    rel_path = ann.file_path.relative_to(self.project_path)
                    content += f"- {ann.message} (`{rel_path}:{ann.line_number}`)\n"
                content += "\n"

        content += """## Next Steps

1. Address all critical FIXME items
2. Implement high-priority TODO tasks
3. Set up development environment
4. Run initial test suite
5. Configure CI/CD pipeline

## DuggerLinkTools Integration

This project now supports:
- `dgt status` - Check ecosystem health
- `dgt commit` - Semantic commits with auto-formatting
- `dgt-add scan` - Extract and track TODOs
- `dgt-add audit` - Security and quality audits

---

*Last updated: Retrofit process completion*
"""

        roadmap_path.write_text(content)
        self.logger.info(f"Generated ROADMAP.md with {len(annotations)} annotations")
        return True

    def retrofit_project(self, project_name: str = None, overwrite_ide: bool = False) -> Dict[str, bool]:
        """Perform complete project retrofit.
        
        Args:
            project_name: Optional project name
            overwrite_ide: Whether to overwrite existing IDE files
            
        Returns:
            Dictionary of actions performed
        """
        self.logger.info(f"Starting retrofit of {self.project_path}")
        
        # Assess current state
        assessment = self.assess_project()
        
        actions_performed = {}
        
        # Inject missing components
        if not assessment["has_pyproject"]:
            actions_performed["pyproject_injected"] = self.inject_pyproject_toml(project_name)
        
        if not assessment["has_dugger_yaml"] or not assessment["has_dugger_yaml"]:
            actions_performed["dugger_yaml_injected"] = self.inject_dugger_yaml(project_name)
        
        if not assessment["has_gitignore"]:
            actions_performed["gitignore_injected"] = self.inject_gitignore()
        
        if not assessment["has_git"]:
            actions_performed["git_initialized"] = self.initialize_git_if_needed()
        
        # Always attempt IDE sync (with user preference on overwrite)
        actions_performed["ide_synced"] = self.sync_ide_configurations(overwrite=overwrite_ide)
        
        # Generate roadmap seed
        actions_performed["roadmap_generated"] = self.generate_roadmap_seed()
        
        # Log summary
        performed_count = sum(1 for performed in actions_performed.values() if performed)
        self.logger.info(f"Retrofit complete: {performed_count} actions performed")
        
        return actions_performed