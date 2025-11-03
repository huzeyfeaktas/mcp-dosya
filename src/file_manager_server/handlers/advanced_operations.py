"""
Advanced file operation handlers
"""

import os
import shutil
from typing import Any, Dict, List
import aiofiles

from ..config import ServerConfig
from ..utils import (
    validate_file_path,
    validate_path,
    get_security_warnings,
    format_file_size,
    detect_encoding,
    is_binary_file,
)


async def handle_copy_file(arguments: Dict[str, Any], config: ServerConfig) -> str:
    """
    Copy a file
    
    Args:
        arguments: {
            "source_path": str,
            "destination_path": str,
            "overwrite": bool (optional, default: False)
        }
        config: Server configuration
        
    Returns:
        Success message
    """
    source_path = validate_file_path(arguments["source_path"], must_exist=True)
    dest_path = validate_path(arguments["destination_path"])
    overwrite = arguments.get("overwrite", False)
    
    # Check if destination exists
    if os.path.exists(dest_path) and not overwrite:
        return (
            f"❌ Destination already exists\n"
            f"Path: {dest_path}\n"
            f"Use overwrite=true to replace existing file"
        )
    
    # Security warnings
    warnings = []
    warnings.extend(get_security_warnings(source_path, config))
    warnings.extend(get_security_warnings(dest_path, config))
    warning_text = "\n".join(warnings) + "\n\n" if warnings else ""
    
    # Create destination directory if needed
    dest_dir = os.path.dirname(dest_path)
    if dest_dir and not os.path.exists(dest_dir):
        os.makedirs(dest_dir, exist_ok=True)
    
    # Copy file
    shutil.copy2(source_path, dest_path)
    
    file_size = format_file_size(os.path.getsize(dest_path))
    
    return (
        f"{warning_text}"
        f"✅ File copied successfully\n"
        f"Source: {source_path}\n"
        f"Destination: {dest_path}\n"
        f"Size: {file_size}"
    )


async def handle_move_file(arguments: Dict[str, Any], config: ServerConfig) -> str:
    """
    Move a file
    
    Args:
        arguments: {
            "source_path": str,
            "destination_path": str,
            "overwrite": bool (optional, default: False)
        }
        config: Server configuration
        
    Returns:
        Success message
    """
    source_path = validate_file_path(arguments["source_path"], must_exist=True)
    dest_path = validate_path(arguments["destination_path"])
    overwrite = arguments.get("overwrite", False)
    
    # Check if destination exists
    if os.path.exists(dest_path) and not overwrite:
        return (
            f"❌ Destination already exists\n"
            f"Path: {dest_path}\n"
            f"Use overwrite=true to replace existing file"
        )
    
    # Security warnings
    warnings = []
    warnings.extend(get_security_warnings(source_path, config))
    warnings.extend(get_security_warnings(dest_path, config))
    
    if warnings:
        warning_text = "\n".join(warnings)
        return (
            f"⚠️  MOVE BLOCKED\n\n"
            f"{warning_text}\n\n"
            f"File was NOT moved. If you really want to move this file, "
            f"please set ENABLE_DANGEROUS_OPERATIONS=true in the configuration."
        )
    
    # Create destination directory if needed
    dest_dir = os.path.dirname(dest_path)
    if dest_dir and not os.path.exists(dest_dir):
        os.makedirs(dest_dir, exist_ok=True)
    
    file_size = format_file_size(os.path.getsize(source_path))
    
    # Move file
    shutil.move(source_path, dest_path)
    
    return (
        f"✅ File moved successfully\n"
        f"From: {source_path}\n"
        f"To: {dest_path}\n"
        f"Size: {file_size}"
    )


async def handle_rename_file(arguments: Dict[str, Any], config: ServerConfig) -> str:
    """
    Rename a file
    
    Args:
        arguments: {
            "file_path": str,
            "new_name": str,
            "overwrite": bool (optional, default: False)
        }
        config: Server configuration
        
    Returns:
        Success message
    """
    file_path = validate_file_path(arguments["file_path"], must_exist=True)
    new_name = arguments["new_name"]
    overwrite = arguments.get("overwrite", False)
    
    # Construct new path
    parent_dir = os.path.dirname(file_path)
    new_path = os.path.join(parent_dir, new_name)
    
    # Check if destination exists
    if os.path.exists(new_path) and not overwrite:
        return (
            f"❌ File with new name already exists\n"
            f"Path: {new_path}\n"
            f"Use overwrite=true to replace existing file"
        )
    
    # Rename
    os.rename(file_path, new_path)
    
    return (
        f"✅ File renamed successfully\n"
        f"Old name: {os.path.basename(file_path)}\n"
        f"New name: {new_name}\n"
        f"Full path: {new_path}"
    )


async def handle_search_files(arguments: Dict[str, Any], config: ServerConfig) -> str:
    """
    Search for files (combines name and content search)
    
    Args:
        arguments: {
            "directory_path": str,
            "name_pattern": str (optional),
            "content_pattern": str (optional),
            "max_results": int (optional)
        }
        config: Server configuration
        
    Returns:
        Search results
    """
    from .search_operations import handle_find_files_by_pattern, handle_search_in_files
    
    dir_path = arguments["directory_path"]
    name_pattern = arguments.get("name_pattern")
    content_pattern = arguments.get("content_pattern")
    
    results = []
    
    if name_pattern:
        name_results = await handle_find_files_by_pattern(
            {"directory_path": dir_path, "pattern": name_pattern},
            config
        )
        results.append(name_results)
    
    if content_pattern:
        content_results = await handle_search_in_files(
            {"directory_path": dir_path, "search_text": content_pattern},
            config
        )
        results.append(content_results)
    
    if not results:
        return "❌ No search criteria provided (name_pattern or content_pattern required)"
    
    return "\n\n".join(results)


async def handle_read_multiple_files(arguments: Dict[str, Any], config: ServerConfig) -> str:
    """
    Read multiple files at once
    
    Args:
        arguments: {
            "file_paths": List[str],
            "encoding": str (optional)
        }
        config: Server configuration
        
    Returns:
        Combined file contents
    """
    from .file_operations import handle_read_file
    
    file_paths = arguments["file_paths"]
    encoding = arguments.get("encoding")
    
    if not isinstance(file_paths, list):
        return "❌ file_paths must be a list"
    
    if len(file_paths) > config.max_batch_files:
        return (
            f"❌ Too many files requested\n"
            f"Maximum: {config.max_batch_files}\n"
            f"Requested: {len(file_paths)}"
        )
    
    results = []
    
    for file_path in file_paths:
        try:
            args = {"file_path": file_path}
            if encoding:
                args["encoding"] = encoding
            
            content = await handle_read_file(args, config)
            results.append(content)
            results.append("\n" + "=" * 70 + "\n")
        except Exception as e:
            results.append(f"❌ Error reading {file_path}: {e}\n")
            results.append("\n" + "=" * 70 + "\n")
    
    header = (
        f"📚 Multiple File Read\n"
        f"{'=' * 70}\n"
        f"Files requested: {len(file_paths)}\n"
        f"{'=' * 70}\n\n"
    )
    
    return header + "\n".join(results)

