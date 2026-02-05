"""Git data models for DuggerLinkTools."""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class GitState(BaseModel):
    """Git repository state information."""
    
    is_repo: bool = False
    current_branch: Optional[str] = None
    has_uncommitted_changes: bool = False
    last_commit_hash: Optional[str] = None
    last_commit_date: Optional[datetime] = None
    remote_url: Optional[str] = None
    ahead_count: int = 0
    behind_count: int = 0
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }