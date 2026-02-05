"""
Safe I/O utilities for DuggerLinkTools.

Provides UTF-8 enforced file operations with cross-platform compatibility.
"""

import shutil
from pathlib import Path
from typing import Union, Optional

from loguru import logger


def safe_read(file_path: Union[str, Path], encoding: str = "utf-8") -> str:
    """Safely read a file with enforced UTF-8 encoding.
    
    Args:
        file_path: Path to file to read
        encoding: File encoding (defaults to utf-8)
        
    Returns:
        File content as string
        
    Raises:
        OSError: If file cannot be read
        UnicodeDecodeError: If file cannot be decoded with specified encoding
    """
    path = Path(file_path)
    
    if not path.exists():
        raise OSError(f"File not found: {path}")
    
    try:
        return path.read_text(encoding=encoding)
    except UnicodeDecodeError as e:
        logger.error(f"Failed to decode {path} with {encoding}: {e}")
        # Try fallback encodings for Windows compatibility
        fallback_encodings = ["utf-8-sig", "cp1252", "latin1"]
        
        for fallback in fallback_encodings:
            try:
                content = path.read_text(encoding=fallback)
                logger.warning(f"Successfully read {path} using fallback encoding: {fallback}")
                return content
            except UnicodeDecodeError:
                continue
        
        raise UnicodeDecodeError(
            f"Could not read {path} with any supported encoding",
            e.object,
            e.start,
            e.end,
            e.reason
        ) from e


def safe_write(
    file_path: Union[str, Path], 
    content: str, 
    encoding: str = "utf-8",
    create_dirs: bool = True
) -> None:
    """Safely write content to a file with enforced UTF-8 encoding.
    
    Args:
        file_path: Path to file to write
        content: Content to write
        encoding: File encoding (defaults to utf-8)
        create_dirs: Whether to create parent directories
        
    Raises:
        OSError: If file cannot be written
    """
    path = Path(file_path)
    
    # Create parent directories if needed
    if create_dirs:
        path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        path.write_text(content, encoding=encoding)
        logger.debug(f"Successfully wrote {path} with {encoding}")
    except UnicodeEncodeError as e:
        logger.error(f"Failed to encode content for {path} with {encoding}: {e}")
        
        # Try to remove problematic characters for Windows compatibility
        try:
            # Replace problematic Unicode characters with ASCII equivalents
            safe_content = content.encode("ascii", errors="replace").decode("ascii")
            path.write_text(safe_content, encoding="ascii")
            logger.warning(f"Wrote {path} with ASCII fallback (some characters replaced)")
        except Exception as fallback_error:
            raise OSError(f"Could not write {path} with any encoding: {fallback_error}") from e


def safe_copy(
    source: Union[str, Path], 
    destination: Union[str, Path],
    create_dirs: bool = True
) -> None:
    """Safely copy a file or directory.
    
    Args:
        source: Source path
        destination: Destination path
        create_dirs: Whether to create parent directories
        
    Raises:
        OSError: If copy operation fails
    """
    src_path = Path(source)
    dst_path = Path(destination)
    
    if not src_path.exists():
        raise OSError(f"Source not found: {src_path}")
    
    # Create parent directories if needed
    if create_dirs:
        dst_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        if src_path.is_file():
            shutil.copy2(src_path, dst_path)
        else:
            if dst_path.exists():
                shutil.rmtree(dst_path)
            shutil.copytree(src_path, dst_path)
        
        logger.debug(f"Successfully copied {src_path} to {dst_path}")
    except Exception as e:
        raise OSError(f"Failed to copy {src_path} to {dst_path}: {e}") from e


def safe_read_binary(file_path: Union[str, Path]) -> bytes:
    """Safely read a file in binary mode.
    
    Args:
        file_path: Path to file to read
        
    Returns:
        File content as bytes
        
    Raises:
        OSError: If file cannot be read
    """
    path = Path(file_path)
    
    if not path.exists():
        raise OSError(f"File not found: {path}")
    
    return path.read_bytes()


def safe_write_binary(
    file_path: Union[str, Path], 
    content: bytes,
    create_dirs: bool = True
) -> None:
    """Safely write binary content to a file.
    
    Args:
        file_path: Path to file to write
        content: Binary content to write
        create_dirs: Whether to create parent directories
        
    Raises:
        OSError: If file cannot be written
    """
    path = Path(file_path)
    
    # Create parent directories if needed
    if create_dirs:
        path.parent.mkdir(parents=True, exist_ok=True)
    
    path.write_bytes(content)
    logger.debug(f"Successfully wrote binary content to {path}")


def ensure_utf8_encoding(file_path: Union[str, Path]) -> bool:
    """Check if a file can be read with UTF-8 encoding.
    
    Args:
        file_path: Path to file to check
        
    Returns:
        True if file can be read with UTF-8, False otherwise
    """
    try:
        safe_read(file_path, encoding="utf-8")
        return True
    except UnicodeDecodeError:
        return False