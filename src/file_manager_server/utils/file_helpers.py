"""
File helper utilities
"""

import os
import mimetypes
from pathlib import Path
from typing import Optional, List
from ..config import BINARY_EXTENSIONS, TEXT_ENCODINGS


def detect_encoding(file_path: str) -> str:
    """
    Detect file encoding
    
    Args:
        file_path: Path to file
        
    Returns:
        Detected encoding name
    """
    # Try chardet if available
    try:
        import chardet
        with open(file_path, 'rb') as f:
            raw_data = f.read(10000)  # Read first 10KB
            result = chardet.detect(raw_data)
            if result['encoding'] and result['confidence'] > 0.7:
                return result['encoding']
    except ImportError:
        pass
    except Exception:
        pass
    
    # Try common encodings
    for encoding in TEXT_ENCODINGS:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                f.read(1024)  # Try to read first 1KB
            return encoding
        except (UnicodeDecodeError, UnicodeError):
            continue
    
    # Default to utf-8
    return 'utf-8'


def is_binary_file(file_path: str) -> bool:
    """
    Check if file is binary
    
    Args:
        file_path: Path to file
        
    Returns:
        True if binary, False otherwise
    """
    # Check extension first
    ext = os.path.splitext(file_path)[1].lower()
    if ext in BINARY_EXTENSIONS:
        return True
    
    # Check MIME type
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type and not mime_type.startswith('text/'):
        return True
    
    # Check file content
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(8192)
            # Check for null bytes (common in binary files)
            if b'\x00' in chunk:
                return True
            # Check for high ratio of non-text bytes
            text_chars = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)))
            non_text = sum(1 for byte in chunk if byte not in text_chars)
            return non_text / len(chunk) > 0.3 if chunk else False
    except Exception:
        return False


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def get_file_type(file_path: str) -> str:
    """
    Get file type description
    
    Args:
        file_path: Path to file
        
    Returns:
        File type description
    """
    if not os.path.exists(file_path):
        return "unknown"
    
    if os.path.isdir(file_path):
        return "directory"
    
    if os.path.islink(file_path):
        return "symlink"
    
    if is_binary_file(file_path):
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type:
            return mime_type
        return "binary"
    
    return "text"


def safe_join_path(*parts: str) -> str:
    """
    Safely join path parts, preventing directory traversal
    
    Args:
        *parts: Path parts to join
        
    Returns:
        Joined path
        
    Raises:
        ValueError: If resulting path would escape base directory
    """
    if not parts:
        raise ValueError("No path parts provided")
    
    base = os.path.abspath(parts[0])
    result = base
    
    for part in parts[1:]:
        # Remove any leading slashes or drive letters
        part = part.lstrip('/\\')
        if ':' in part:
            part = part.split(':', 1)[1].lstrip('/\\')
        
        result = os.path.normpath(os.path.join(result, part))
        
        # Ensure result is still under base directory
        if not result.startswith(base):
            raise ValueError(f"Path traversal detected: {parts}")
    
    return result


def get_relative_path(path: str, base: str) -> str:
    """
    Get relative path from base
    
    Args:
        path: Target path
        base: Base path
        
    Returns:
        Relative path
    """
    try:
        return os.path.relpath(path, base)
    except ValueError:
        # Different drives on Windows
        return path


def list_files_recursive(directory: str, pattern: Optional[str] = None, max_depth: int = -1) -> List[str]:
    """
    List files recursively
    
    Args:
        directory: Directory to search
        pattern: Optional glob pattern
        max_depth: Maximum depth (-1 for unlimited)
        
    Returns:
        List of file paths
    """
    import fnmatch
    
    results = []
    
    def _walk(current_dir: str, current_depth: int) -> None:
        if max_depth >= 0 and current_depth > max_depth:
            return
        
        try:
            for entry in os.scandir(current_dir):
                if entry.is_file():
                    if pattern is None or fnmatch.fnmatch(entry.name, pattern):
                        results.append(entry.path)
                elif entry.is_dir():
                    _walk(entry.path, current_depth + 1)
        except PermissionError:
            pass  # Skip directories we can't access
    
    _walk(directory, 0)
    return results

