"""
Configuration management for MCP File Manager Server
"""

import os
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ServerConfig:
    """Server configuration settings"""
    
    # Logging
    log_level: str = "INFO"
    log_file: Optional[str] = None
    
    # File size limits (in MB)
    max_file_size_mb: int = 100
    max_batch_files: int = 50
    max_search_results: int = 1000
    
    # Image settings (GPT Vision improvements)
    max_image_size_mb: int = 15  # Max image size for GPT Vision
    enable_image_compression: bool = True  # Auto-compress large images
    max_image_dimension: int = 1920  # Max width/height for auto-resize
    
    # Security
    enable_dangerous_operations: bool = False
    allowed_directories: Optional[List[str]] = None
    blocked_directories: Optional[List[str]] = None
    
    # Performance
    chunk_size: int = 8192  # For file reading/writing
    max_tree_depth: int = 10
    
    # Features
    enable_compression: bool = True
    enable_hashing: bool = True
    enable_watching: bool = True
    
    @classmethod
    def from_env(cls) -> "ServerConfig":
        """Create configuration from environment variables"""
        return cls(
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            log_file=os.getenv("LOG_FILE"),
            max_file_size_mb=int(os.getenv("MAX_FILE_SIZE_MB", "100")),
            max_batch_files=int(os.getenv("MAX_BATCH_FILES", "50")),
            max_search_results=int(os.getenv("MAX_SEARCH_RESULTS", "1000")),
            enable_dangerous_operations=os.getenv("ENABLE_DANGEROUS_OPERATIONS", "false").lower() == "true",
            chunk_size=int(os.getenv("CHUNK_SIZE", "8192")),
            max_tree_depth=int(os.getenv("MAX_TREE_DEPTH", "10")),
            enable_compression=os.getenv("ENABLE_COMPRESSION", "true").lower() == "true",
            enable_hashing=os.getenv("ENABLE_HASHING", "true").lower() == "true",
            enable_watching=os.getenv("ENABLE_WATCHING", "true").lower() == "true",
        )


# System-critical paths that should trigger warnings
SYSTEM_CRITICAL_PATHS = [
    # Windows
    "C:\\Windows\\System32",
    "C:\\Windows\\SysWOW64",
    "C:\\Program Files",
    "C:\\Program Files (x86)",
    # Unix/Linux
    "/etc",
    "/bin",
    "/sbin",
    "/usr/bin",
    "/usr/sbin",
    "/boot",
    "/sys",
    "/proc",
    # macOS
    "/System",
    "/Library/System",
]

# File extensions considered dangerous for execution
DANGEROUS_EXTENSIONS = [
    ".exe", ".bat", ".cmd", ".com", ".scr", ".vbs", ".js", ".jar",
    ".dll", ".sys", ".drv", ".ocx", ".cpl", ".msi", ".ps1", ".sh",
]

# Binary file extensions
BINARY_EXTENSIONS = [
    ".exe", ".dll", ".so", ".dylib", ".bin", ".dat", ".db", ".sqlite",
    ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".ico", ".webp", ".svg",
    ".mp3", ".mp4", ".avi", ".mov", ".wav", ".flac", ".mkv", ".wmv",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz",
]

# Image file extensions (GPT Vision support)
IMAGE_EXTENSIONS = [
    ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg", ".ico", ".tiff", ".tif"
]

# OneDrive and user directories (allowed for image access)
ONEDRIVE_PATHS = [
    "OneDrive",  # Will match any OneDrive path
    "Desktop",
    "Pictures",
    "Downloads",
    "Documents",
]

# Text file encodings to try
TEXT_ENCODINGS = ["utf-8", "utf-16", "latin-1", "cp1252", "ascii"]

