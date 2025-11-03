"""
Input validation utilities
"""

import os
import re
from pathlib import Path
from typing import Optional


class ValidationError(Exception):
    """Raised when validation fails"""
    pass


def validate_path(path: str, must_exist: bool = False) -> str:
    """
    Validate and normalize a path
    
    Args:
        path: Path to validate
        must_exist: Whether path must exist
        
    Returns:
        Normalized absolute path
        
    Raises:
        ValidationError: If validation fails
    """
    if not path:
        raise ValidationError("Path cannot be empty")
    
    if not isinstance(path, str):
        raise ValidationError(f"Path must be a string, got {type(path)}")
    
    # Check for null bytes
    if "\x00" in path:
        raise ValidationError("Path cannot contain null bytes")
    
    try:
        abs_path = os.path.abspath(path)
    except Exception as e:
        raise ValidationError(f"Invalid path format: {e}")
    
    if must_exist and not os.path.exists(abs_path):
        raise ValidationError(f"Path does not exist: {path}")
    
    return abs_path


def validate_file_path(path: str, must_exist: bool = False) -> str:
    """
    Validate a file path
    
    Args:
        path: File path to validate
        must_exist: Whether file must exist
        
    Returns:
        Normalized absolute path
        
    Raises:
        ValidationError: If validation fails
    """
    abs_path = validate_path(path, must_exist=must_exist)
    
    if must_exist and not os.path.isfile(abs_path):
        raise ValidationError(f"Path is not a file: {path}")
    
    return abs_path


def validate_directory_path(path: str, must_exist: bool = False) -> str:
    """
    Validate a directory path
    
    Args:
        path: Directory path to validate
        must_exist: Whether directory must exist
        
    Returns:
        Normalized absolute path
        
    Raises:
        ValidationError: If validation fails
    """
    abs_path = validate_path(path, must_exist=must_exist)
    
    if must_exist and not os.path.isdir(abs_path):
        raise ValidationError(f"Path is not a directory: {path}")
    
    return abs_path


def validate_filename(filename: str) -> str:
    """
    Validate a filename (no path separators)
    
    Args:
        filename: Filename to validate
        
    Returns:
        Validated filename
        
    Raises:
        ValidationError: If validation fails
    """
    if not filename:
        raise ValidationError("Filename cannot be empty")
    
    if os.sep in filename or "/" in filename or "\\" in filename:
        raise ValidationError(f"Filename cannot contain path separators: {filename}")
    
    # Check for reserved names on Windows
    if os.name == "nt":
        reserved_names = [
            "CON", "PRN", "AUX", "NUL",
            "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
            "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9",
        ]
        if filename.upper() in reserved_names:
            raise ValidationError(f"Filename uses reserved name: {filename}")
    
    return filename


def validate_encoding(encoding: str) -> str:
    """
    Validate an encoding name
    
    Args:
        encoding: Encoding to validate
        
    Returns:
        Validated encoding
        
    Raises:
        ValidationError: If encoding is invalid
    """
    import codecs
    
    try:
        codecs.lookup(encoding)
        return encoding
    except LookupError:
        raise ValidationError(f"Unknown encoding: {encoding}")


def validate_hash_algorithm(algorithm: str) -> str:
    """
    Validate a hash algorithm name
    
    Args:
        algorithm: Algorithm to validate
        
    Returns:
        Validated algorithm (lowercase)
        
    Raises:
        ValidationError: If algorithm is invalid
    """
    valid_algorithms = ["md5", "sha1", "sha256", "sha512"]
    algorithm_lower = algorithm.lower()
    
    if algorithm_lower not in valid_algorithms:
        raise ValidationError(
            f"Invalid hash algorithm: {algorithm}. "
            f"Valid algorithms: {', '.join(valid_algorithms)}"
        )
    
    return algorithm_lower


def validate_search_pattern(pattern: str) -> str:
    """
    Validate a search pattern
    
    Args:
        pattern: Pattern to validate
        
    Returns:
        Validated pattern
        
    Raises:
        ValidationError: If pattern is invalid
    """
    if not pattern:
        raise ValidationError("Search pattern cannot be empty")
    
    # Try to compile as regex to check validity
    try:
        re.compile(pattern)
    except re.error as e:
        raise ValidationError(f"Invalid regex pattern: {e}")
    
    return pattern


def validate_positive_int(value: int, name: str, max_value: Optional[int] = None) -> int:
    """
    Validate a positive integer
    
    Args:
        value: Value to validate
        name: Name of the parameter
        max_value: Maximum allowed value
        
    Returns:
        Validated value
        
    Raises:
        ValidationError: If validation fails
    """
    if not isinstance(value, int):
        raise ValidationError(f"{name} must be an integer, got {type(value)}")
    
    if value < 0:
        raise ValidationError(f"{name} must be non-negative, got {value}")
    
    if max_value is not None and value > max_value:
        raise ValidationError(f"{name} must be at most {max_value}, got {value}")
    
    return value

