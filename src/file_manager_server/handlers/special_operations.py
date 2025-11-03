"""
Special file operation handlers (compression, hashing, etc.)
"""

import os
import hashlib
import zipfile
from typing import Any, Dict
from pathlib import Path

from ..config import ServerConfig
from ..utils import (
    validate_file_path,
    validate_directory_path,
    validate_path,
    validate_hash_algorithm,
    get_security_warnings,
    format_file_size,
)


async def handle_compress_file(arguments: Dict[str, Any], config: ServerConfig) -> str:
    """
    Compress file or directory to ZIP
    
    Args:
        arguments: {
            "source_path": str,
            "output_path": str,
            "compression_level": int (optional, 0-9, default: 6)
        }
        config: Server configuration
        
    Returns:
        Success message
    """
    source_path = validate_path(arguments["source_path"], must_exist=True)
    output_path = validate_path(arguments["output_path"])
    compression_level = arguments.get("compression_level", 6)
    
    # Validate compression level
    if not 0 <= compression_level <= 9:
        return "❌ Compression level must be between 0 and 9"
    
    # Security warnings
    warnings = []
    warnings.extend(get_security_warnings(source_path, config))
    warnings.extend(get_security_warnings(output_path, config))
    warning_text = "\n".join(warnings) + "\n\n" if warnings else ""
    
    # Create parent directory for output
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    # Compress
    files_added = 0
    
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=compression_level) as zipf:
        if os.path.isfile(source_path):
            # Single file
            zipf.write(source_path, os.path.basename(source_path))
            files_added = 1
        else:
            # Directory
            for root, dirs, files in os.walk(source_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, source_path)
                    zipf.write(file_path, arcname)
                    files_added += 1
    
    # Get sizes
    original_size = 0
    if os.path.isfile(source_path):
        original_size = os.path.getsize(source_path)
    else:
        for root, dirs, files in os.walk(source_path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    original_size += os.path.getsize(file_path)
                except:
                    pass
    
    compressed_size = os.path.getsize(output_path)
    compression_ratio = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0
    
    return (
        f"{warning_text}"
        f"✅ Compression successful\n"
        f"Source: {source_path}\n"
        f"Output: {output_path}\n"
        f"Files compressed: {files_added}\n"
        f"Original size: {format_file_size(original_size)}\n"
        f"Compressed size: {format_file_size(compressed_size)}\n"
        f"Compression ratio: {compression_ratio:.1f}%"
    )


async def handle_decompress_file(arguments: Dict[str, Any], config: ServerConfig) -> str:
    """
    Decompress ZIP archive
    
    Args:
        arguments: {
            "archive_path": str,
            "output_directory": str
        }
        config: Server configuration
        
    Returns:
        Success message
    """
    archive_path = validate_file_path(arguments["archive_path"], must_exist=True)
    output_dir = validate_path(arguments["output_directory"])
    
    # Security warnings
    warnings = []
    warnings.extend(get_security_warnings(archive_path, config))
    warnings.extend(get_security_warnings(output_dir, config))
    warning_text = "\n".join(warnings) + "\n\n" if warnings else ""
    
    # Check if it's a ZIP file
    if not zipfile.is_zipfile(archive_path):
        return f"❌ Not a valid ZIP file: {archive_path}"
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Extract
    files_extracted = 0
    
    with zipfile.ZipFile(archive_path, 'r') as zipf:
        # Security check: prevent path traversal
        for member in zipf.namelist():
            member_path = os.path.join(output_dir, member)
            if not member_path.startswith(os.path.abspath(output_dir)):
                return (
                    f"❌ Security error: Archive contains files with unsafe paths\n"
                    f"Extraction cancelled to prevent directory traversal attack."
                )
        
        # Extract all
        zipf.extractall(output_dir)
        files_extracted = len(zipf.namelist())
    
    archive_size = os.path.getsize(archive_path)
    
    # Calculate extracted size
    extracted_size = 0
    for root, dirs, files in os.walk(output_dir):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                extracted_size += os.path.getsize(file_path)
            except:
                pass
    
    return (
        f"{warning_text}"
        f"✅ Extraction successful\n"
        f"Archive: {archive_path}\n"
        f"Output directory: {output_dir}\n"
        f"Files extracted: {files_extracted}\n"
        f"Archive size: {format_file_size(archive_size)}\n"
        f"Extracted size: {format_file_size(extracted_size)}"
    )


async def handle_get_file_hash(arguments: Dict[str, Any], config: ServerConfig) -> str:
    """
    Calculate file hash
    
    Args:
        arguments: {
            "file_path": str,
            "algorithm": str (optional, default: sha256)
        }
        config: Server configuration
        
    Returns:
        File hash
    """
    file_path = validate_file_path(arguments["file_path"], must_exist=True)
    algorithm = validate_hash_algorithm(arguments.get("algorithm", "sha256"))
    
    # Get hash function
    if algorithm == "md5":
        hasher = hashlib.md5()
    elif algorithm == "sha1":
        hasher = hashlib.sha1()
    elif algorithm == "sha256":
        hasher = hashlib.sha256()
    elif algorithm == "sha512":
        hasher = hashlib.sha512()
    else:
        return f"❌ Unsupported algorithm: {algorithm}"
    
    # Calculate hash
    file_size = os.path.getsize(file_path)
    
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    
    hash_value = hasher.hexdigest()
    
    return (
        f"🔐 File Hash\n"
        f"{'=' * 50}\n"
        f"File: {file_path}\n"
        f"Size: {format_file_size(file_size)}\n"
        f"Algorithm: {algorithm.upper()}\n"
        f"Hash: {hash_value}"
    )

