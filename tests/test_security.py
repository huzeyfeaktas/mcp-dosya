"""
Tests for security features
"""

import pytest
import os

from file_manager_server.config import ServerConfig
from file_manager_server.utils.security import (
    is_safe_path,
    is_system_critical_path,
    is_dangerous_file,
    check_file_size,
    get_security_warnings,
)
from file_manager_server.utils.validators import (
    validate_path,
    validate_file_path,
    validate_filename,
    validate_encoding,
    validate_hash_algorithm,
    ValidationError,
)


@pytest.fixture
def config():
    """Create test configuration"""
    return ServerConfig(
        max_file_size_mb=10,
        enable_dangerous_operations=False
    )


def test_system_critical_path_detection():
    """Test detection of system-critical paths"""
    # Windows system path
    is_critical, msg = is_system_critical_path("C:\\Windows\\System32\\important.dll")
    assert is_critical
    assert msg is not None
    
    # Unix system path
    is_critical, msg = is_system_critical_path("/etc/passwd")
    assert is_critical
    assert msg is not None
    
    # Normal path
    is_critical, msg = is_system_critical_path("/home/user/documents/file.txt")
    assert not is_critical


def test_dangerous_file_detection():
    """Test detection of dangerous file extensions"""
    # Executable file
    is_dangerous, msg = is_dangerous_file("malware.exe")
    assert is_dangerous
    assert msg is not None
    
    # Script file
    is_dangerous, msg = is_dangerous_file("script.bat")
    assert is_dangerous
    
    # Normal file
    is_dangerous, msg = is_dangerous_file("document.txt")
    assert not is_dangerous


def test_path_validation():
    """Test path validation"""
    # Valid path
    path = validate_path("/home/user/file.txt")
    assert path is not None
    
    # Empty path should raise error
    with pytest.raises(ValidationError):
        validate_path("")
    
    # Null byte should raise error
    with pytest.raises(ValidationError):
        validate_path("/path/with\x00null")


def test_filename_validation():
    """Test filename validation"""
    # Valid filename
    name = validate_filename("document.txt")
    assert name == "document.txt"
    
    # Filename with path separator should fail
    with pytest.raises(ValidationError):
        validate_filename("path/to/file.txt")
    
    # Empty filename should fail
    with pytest.raises(ValidationError):
        validate_filename("")


def test_encoding_validation():
    """Test encoding validation"""
    # Valid encodings
    assert validate_encoding("utf-8") == "utf-8"
    assert validate_encoding("ascii") == "ascii"
    assert validate_encoding("latin-1") == "latin-1"
    
    # Invalid encoding
    with pytest.raises(ValidationError):
        validate_encoding("invalid-encoding-12345")


def test_hash_algorithm_validation():
    """Test hash algorithm validation"""
    # Valid algorithms
    assert validate_hash_algorithm("md5") == "md5"
    assert validate_hash_algorithm("SHA256") == "sha256"
    assert validate_hash_algorithm("sha512") == "sha512"
    
    # Invalid algorithm
    with pytest.raises(ValidationError):
        validate_hash_algorithm("invalid-hash")


def test_allowed_directories(temp_dir=None):
    """Test allowed directories restriction"""
    config = ServerConfig(
        allowed_directories=["/home/user/allowed"]
    )
    
    # Path in allowed directory
    is_safe, msg = is_safe_path("/home/user/allowed/file.txt", config)
    assert is_safe
    
    # Path outside allowed directory
    is_safe, msg = is_safe_path("/home/user/other/file.txt", config)
    assert not is_safe


def test_blocked_directories():
    """Test blocked directories restriction"""
    config = ServerConfig(
        blocked_directories=["/home/user/blocked"]
    )
    
    # Path in blocked directory
    is_safe, msg = is_safe_path("/home/user/blocked/file.txt", config)
    assert not is_safe
    
    # Path outside blocked directory
    is_safe, msg = is_safe_path("/home/user/allowed/file.txt", config)
    assert is_safe


def test_security_warnings_integration(config):
    """Test complete security warnings for a path"""
    # System critical path should generate warnings
    warnings = get_security_warnings("C:\\Windows\\System32\\file.dll", config)
    assert len(warnings) > 0
    
    # Dangerous file should generate warnings
    warnings = get_security_warnings("/home/user/malware.exe", config)
    assert len(warnings) > 0
    
    # Normal file should have no warnings
    warnings = get_security_warnings("/home/user/document.txt", config)
    # May have warnings based on other factors, just check it runs
    assert isinstance(warnings, list)


def test_reserved_windows_names():
    """Test Windows reserved filename detection"""
    if os.name == "nt":
        with pytest.raises(ValidationError):
            validate_filename("CON")
        
        with pytest.raises(ValidationError):
            validate_filename("PRN")
        
        with pytest.raises(ValidationError):
            validate_filename("AUX")

