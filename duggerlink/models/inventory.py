"""
Project Inventory Models for DuggerLinkTools ecosystem tracking.

Pydantic models for cross-project analysis and harvesting intelligence.
"""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set

from pydantic import BaseModel, Field, validator


class ProjectStack(str, Enum):
    """Supported technology stacks."""
    PYTHON = "python"
    CHROME_EXTENSION = "chrome_extension"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    UNKNOWN = "unknown"


class ProjectFamily(str, Enum):
    """Project family classifications."""
    AUTOMATION = "automation"
    DATA_ANALYTICS = "data_analytics"
    EXTENSIONS = "extensions"
    TRADING = "trading"
    WEB_TOOLS = "web_tools"
    UTILITIES = "utilities"
    UNKNOWN = "unknown"


class DNAStatus(str, Enum):
    """DLT DNA validation status."""
    VALID = "valid"
    INVALID = "invalid"
    MISSING = "missing"
    LEGACY = "legacy"


class HarvestCandidate(BaseModel):
    """A file or component identified for harvesting."""
    file_path: Path
    file_type: str
    complexity_score: float = Field(ge=0.0, le=1.0)
    utility_score: float = Field(ge=0.0, le=1.0)
    uniqueness_score: float = Field(ge=0.0, le=1.0)
    harvest_score: float = Field(ge=0.0, le=1.0)
    tags: Set[str] = Field(default_factory=set)
    dependencies: List[str] = Field(default_factory=list)
    description: Optional[str] = None


class ProjectMetrics(BaseModel):
    """Quantitative project analysis metrics."""
    total_files: int
    code_files: int
    test_files: int
    config_files: int
    documentation_files: int
    lines_of_code: int
    complexity_score: float = Field(ge=0.0, le=1.0)
    test_coverage: Optional[float] = Field(None, ge=0.0, le=1.0)
    last_modified: datetime
    git_commits: int
    active_development: bool


class ProjectInventory(BaseModel):
    """Complete inventory analysis for a single project."""
    
    name: str
    path: Path
    stack: ProjectStack
    family: ProjectFamily
    dna_status: DNAStatus
    metrics: ProjectMetrics
    harvest_candidates: List[HarvestCandidate] = Field(default_factory=list)
    dependencies: Dict[str, str] = Field(default_factory=dict)
    quality_indicators: Dict[str, bool] = Field(default_factory=dict)
    retrofit_suggested: bool = False
    retrofit_priority: float = Field(ge=0.0, le=1.0, default=0.0)
    
    @validator('retrofit_suggested', always=True)
    def suggest_retrofit_based_on_dna(cls, v, values):
        """Auto-suggest retrofit based on DNA status."""
        if 'dna_status' in values and values['dna_status'] != DNAStatus.VALID:
            return True
        return v
    
    @validator('retrofit_priority', always=True)
    def calculate_retrofit_priority(cls, v, values):
        """Calculate retrofit priority based on multiple factors."""
        priority = 0.0
        
        # DNA status weight (40%)
        if 'dna_status' in values:
            dna_weights = {
                DNAStatus.MISSING: 1.0,
                DNAStatus.LEGACY: 0.8,
                DNAStatus.INVALID: 0.6,
                DNAStatus.VALID: 0.0,
            }
            priority += dna_weights.get(values['dna_status'], 0.0) * 0.4
        
        # Harvest potential weight (30%)
        if 'harvest_candidates' in values and values['harvest_candidates']:
            avg_harvest_score = sum(
                hc.harvest_score for hc in values['harvest_candidates']
            ) / len(values['harvest_candidates'])
            priority += avg_harvest_score * 0.3
        
        # Project activity weight (20%)
        if 'metrics' in values:
            metrics = values['metrics']
            if not metrics.active_development:
                priority += 0.2
            elif metrics.git_commits < 10:
                priority += 0.1
        
        # Stack relevance weight (10%)
        if 'stack' in values:
            stack_weights = {
                ProjectStack.PYTHON: 0.8,
                ProjectStack.CHROME_EXTENSION: 0.9,
                ProjectStack.JAVASCRIPT: 0.6,
                ProjectStack.TYPESCRIPT: 0.7,
                ProjectStack.UNKNOWN: 0.2,
            }
            priority += stack_weights.get(values['stack'], 0.0) * 0.1
        
        return min(priority, 1.0)


class EcosystemInventory(BaseModel):
    """Complete ecosystem-wide inventory analysis."""
    
    scan_date: datetime = Field(default_factory=datetime.now)
    total_projects: int
    projects: List[ProjectInventory]
    stack_distribution: Dict[ProjectStack, int] = Field(default_factory=dict)
    family_distribution: Dict[ProjectFamily, int] = Field(default_factory=dict)
    dna_status_distribution: Dict[DNAStatus, int] = Field(default_factory=dict)
    top_harvest_candidates: List[HarvestCandidate] = Field(default_factory=list)
    retrofit_candidates: List[ProjectInventory] = Field(default_factory=list)
    
    @validator('stack_distribution', always=True)
    def calculate_stack_distribution(cls, v, values):
        """Calculate distribution of projects by stack."""
        if 'projects' in values:
            distribution = {}
            for project in values['projects']:
                distribution[project.stack] = distribution.get(project.stack, 0) + 1
            return distribution
        return v
    
    @validator('family_distribution', always=True)
    def calculate_family_distribution(cls, v, values):
        """Calculate distribution of projects by family."""
        if 'projects' in values:
            distribution = {}
            for project in values['projects']:
                distribution[project.family] = distribution.get(project.family, 0) + 1
            return distribution
        return v
    
    @validator('dna_status_distribution', always=True)
    def calculate_dna_distribution(cls, v, values):
        """Calculate distribution of DNA validation status."""
        if 'projects' in values:
            distribution = {}
            for project in values['projects']:
                distribution[project.dna_status] = distribution.get(project.dna_status, 0) + 1
            return distribution
        return v
    
    @validator('top_harvest_candidates', always=True)
    def extract_top_harvest_candidates(cls, v, values):
        """Extract top harvest candidates across all projects."""
        if 'projects' in values:
            all_candidates = []
            for project in values['projects']:
                all_candidates.extend(project.harvest_candidates)
            
            # Sort by harvest score and take top 20
            sorted_candidates = sorted(
                all_candidates, 
                key=lambda hc: hc.harvest_score, 
                reverse=True
            )
            return sorted_candidates[:20]
        return v
    
    @validator('retrofit_candidates', always=True)
    def extract_retrofit_candidates(cls, v, values):
        """Extract projects that need retrofitting, sorted by priority."""
        if 'projects' in values:
            retrofit_projects = [
                p for p in values['projects'] 
                if p.retrofit_suggested
            ]
            
            # Sort by retrofit priority
            sorted_projects = sorted(
                retrofit_projects,
                key=lambda p: p.retrofit_priority,
                reverse=True
            )
            return sorted_projects
        return v