"""
Security utilities for file operations
"""

import os
from pathlib import Path
from typing import Optional, Tuple
from ..config import SYSTEM_CRITICAL_PATHS, DANGEROUS_EXTENSIONS, ServerConfig


class SecurityWarning(Exception):
    """Raised when a security warning needs to be communicated"""
    pass


def is_safe_path(path: str, config: Optional[ServerConfig] = None) -> Tuple[bool, Optional[str]]:
    """
    Check if a path is safe to access
    
    Args:
        path: Path to check
        config: Server configuration
        
    Returns:
        Tuple of (is_safe, warning_message)
    """
    abs_path = os.path.abspath(path)
    
    # Check allowed directories
    if config and config.allowed_directories:
        allowed = any(
            abs_path.startswith(os.path.abspath(allowed_dir))
            for allowed_dir in config.allowed_directories
        )
        if not allowed:
            return False, f"Path {path} is outside allowed directories"
    
    # Check blocked directories
    if config and config.blocked_directories:
        blocked = any(
            abs_path.startswith(os.path.abspath(blocked_dir))
            for blocked_dir in config.blocked_directories
        )
        if blocked:
            return False, f"Path {path} is in a blocked directory"
    
    return True, None


def is_system_critical_path(path: str) -> Tuple[bool, Optional[str]]:
    """
    Check if path is in a system-critical location
    
    Args:
        path: Path to check
        
    Returns:
        Tuple of (is_critical, warning_message)
    """
    abs_path = os.path.abspath(path)
    
    for critical_path in SYSTEM_CRITICAL_PATHS:
        if abs_path.startswith(critical_path):
            return True, (
                f"⚠️  WARNING: This path ({path}) is in a system-critical location "
                f"({critical_path}). Modifying files here could damage your system."
            )
    
    return False, None


def is_dangerous_file(path: str) -> Tuple[bool, Optional[str]]:
    """
    Check if file has a potentially dangerous extension
    
    Args:
        path: File path to check
        
    Returns:
        Tuple of (is_dangerous, warning_message)
    """
    ext = os.path.splitext(path)[1].lower()
    
    if ext in DANGEROUS_EXTENSIONS:
        return True, (
            f"⚠️  WARNING: This file ({path}) has a potentially dangerous extension "
            f"({ext}). Exercise caution when modifying executable files."
        )
    
    return False, None


def check_file_size(path: str, config: ServerConfig) -> Tuple[bool, Optional[str]]:
    """
    Check if file size is within limits
    
    Args:
        path: File path to check
        config: Server configuration
        
    Returns:
        Tuple of (is_within_limit, warning_message)
    """
    if not os.path.exists(path):
        return True, None
    
    size_mb = os.path.getsize(path) / (1024 * 1024)
    
    if size_mb > config.max_file_size_mb:
        return False, (
            f"⚠️  WARNING: File {path} is {size_mb:.2f} MB, which exceeds the "
            f"configured limit of {config.max_file_size_mb} MB. Operation cancelled."
        )
    
    # Soft warning at 50% of limit
    if size_mb > config.max_file_size_mb * 0.5:
        return True, (
            f"ℹ️  INFO: File {path} is {size_mb:.2f} MB, which is large. "
            f"This operation may take some time."
        )
    
    return True, None


def get_security_warnings(path: str, config: ServerConfig) -> list[str]:
    """
    Get all security warnings for a path
    
    Args:
        path: Path to check
        config: Server configuration
        
    Returns:
        List of warning messages
    """
    warnings = []
    
    # Check if path is safe
    is_safe, msg = is_safe_path(path, config)
    if not is_safe:
        warnings.append(msg)
    
    # Check if system critical
    is_critical, msg = is_system_critical_path(path)
    if is_critical:
        warnings.append(msg)
    
    # Check if dangerous file
    is_dangerous, msg = is_dangerous_file(path)
    if is_dangerous:
        warnings.append(msg)
    
    # Check file size if exists
    if os.path.exists(path) and os.path.isfile(path):
        _, msg = check_file_size(path, config)
        if msg:
            warnings.append(msg)
    
    return warnings


def require_dangerous_operations(config: ServerConfig, operation: str) -> None:
    """
    Check if dangerous operations are enabled
    
    Args:
        config: Server configuration
        operation: Name of the operation
        
    Raises:
        SecurityWarning: If dangerous operations are not enabled
    """
    if not config.enable_dangerous_operations:
        raise SecurityWarning(
            f"Operation '{operation}' requires ENABLE_DANGEROUS_OPERATIONS=true. "
            f"This is a safety measure to prevent accidental data loss."
        )

