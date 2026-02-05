"""Core exceptions for DuggerLinkTools ecosystem."""

from __future__ import annotations

from typing import Any


class DuggerToolError(Exception):
    """Custom exception for tool-related errors in the Dugger ecosystem."""
    
    def __init__(self, tool_name: str, command: list[str], message: str) -> None:
        self.tool_name = tool_name
        self.command = command
        self.message = message
        super().__init__(f"{tool_name}: {message}")
    
    def __repr__(self) -> str:
        return f"DuggerToolError(tool_name={self.tool_name!r}, command={self.command!r}, message={self.message!r})"