"""
Directory operation handlers
"""

import os
import shutil
from datetime import datetime
from typing import Any, Dict, List
from pathlib import Path

from ..config import ServerConfig
from ..utils import (
    validate_directory_path,
    validate_path,
    get_security_warnings,
    format_file_size,
    get_file_type,
)


async def handle_list_directory(arguments: Dict[str, Any], config: ServerConfig) -> str:
    """
    List directory contents
    
    Args:
        arguments: {
            "directory_path": str,
            "recursive": bool (optional, default: False),
            "show_hidden": bool (optional, default: False),
            "pattern": str (optional, glob pattern)
        }
        config: Server configuration
        
    Returns:
        Directory listing
    """
    dir_path = validate_directory_path(arguments["directory_path"], must_exist=True)
    recursive = arguments.get("recursive", False)
    show_hidden = arguments.get("show_hidden", False)
    pattern = arguments.get("pattern")
    
    # Security warnings
    warnings = get_security_warnings(dir_path, config)
    warning_text = "\n".join(warnings) + "\n\n" if warnings else ""
    
    entries = []
    
    if recursive:
        # Recursive listing
        for root, dirs, files in os.walk(dir_path):
            # Filter hidden
            if not show_hidden:
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                files = [f for f in files if not f.startswith('.')]
            
            # Apply pattern
            if pattern:
                import fnmatch
                files = [f for f in files if fnmatch.fnmatch(f, pattern)]
            
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    stat = os.stat(file_path)
                    size = format_file_size(stat.st_size)
                    rel_path = os.path.relpath(file_path, dir_path)
                    entries.append(f"  📄 {rel_path} ({size})")
                except Exception:
                    pass
            
            for dir_name in dirs:
                rel_path = os.path.relpath(os.path.join(root, dir_name), dir_path)
                entries.append(f"  📁 {rel_path}/")
    else:
        # Non-recursive listing
        try:
            with os.scandir(dir_path) as it:
                items = list(it)
                
                # Filter hidden
                if not show_hidden:
                    items = [item for item in items if not item.name.startswith('.')]
                
                # Apply pattern
                if pattern:
                    import fnmatch
                    items = [item for item in items if fnmatch.fnmatch(item.name, pattern)]
                
                # Sort: directories first, then files
                items.sort(key=lambda x: (not x.is_dir(), x.name.lower()))
                
                for item in items:
                    try:
                        if item.is_dir():
                            entries.append(f"  📁 {item.name}/")
                        else:
                            stat = item.stat()
                            size = format_file_size(stat.st_size)
                            entries.append(f"  📄 {item.name} ({size})")
                    except Exception:
                        pass
        except PermissionError:
            return f"❌ Permission denied: {dir_path}"
    
    if not entries:
        listing = "  (empty directory)"
    else:
        listing = "\n".join(entries)
    
    return (
        f"{warning_text}"
        f"📁 Directory: {dir_path}\n"
        f"Total items: {len(entries)}\n"
        f"{'=' * 50}\n"
        f"{listing}"
    )


async def handle_create_directory(arguments: Dict[str, Any], config: ServerConfig) -> str:
    """
    Create a directory
    
    Args:
        arguments: {
            "directory_path": str,
            "parents": bool (optional, create parent directories, default: True)
        }
        config: Server configuration
        
    Returns:
        Success message
    """
    dir_path = validate_path(arguments["directory_path"])
    parents = arguments.get("parents", True)
    
    # Security warnings
    warnings = get_security_warnings(dir_path, config)
    warning_text = "\n".join(warnings) + "\n\n" if warnings else ""
    
    if os.path.exists(dir_path):
        if os.path.isdir(dir_path):
            return f"ℹ️  Directory already exists\nPath: {dir_path}"
        else:
            return f"❌ Path exists but is not a directory\nPath: {dir_path}"
    
    if parents:
        os.makedirs(dir_path, exist_ok=True)
    else:
        os.mkdir(dir_path)
    
    return (
        f"{warning_text}"
        f"✅ Directory created successfully\n"
        f"Path: {dir_path}"
    )


async def handle_delete_directory(arguments: Dict[str, Any], config: ServerConfig) -> str:
    """
    Delete a directory
    
    Args:
        arguments: {
            "directory_path": str,
            "recursive": bool (optional, delete contents too, default: False)
        }
        config: Server configuration
        
    Returns:
        Success message
    """
    dir_path = validate_directory_path(arguments["directory_path"], must_exist=True)
    recursive = arguments.get("recursive", False)
    
    # Security warnings
    warnings = get_security_warnings(dir_path, config)
    if warnings:
        warning_text = "\n".join(warnings)
        return (
            f"⚠️  DELETION BLOCKED\n\n"
            f"{warning_text}\n\n"
            f"Directory was NOT deleted. If you really want to delete this directory, "
            f"please set ENABLE_DANGEROUS_OPERATIONS=true in the configuration."
        )
    
    # Count contents
    total_items = 0
    if recursive:
        for root, dirs, files in os.walk(dir_path):
            total_items += len(dirs) + len(files)
    
    # Delete
    if recursive:
        shutil.rmtree(dir_path)
        return (
            f"✅ Directory deleted successfully (recursive)\n"
            f"Path: {dir_path}\n"
            f"Items deleted: {total_items}"
        )
    else:
        try:
            os.rmdir(dir_path)
            return (
                f"✅ Directory deleted successfully\n"
                f"Path: {dir_path}"
            )
        except OSError:
            return (
                f"❌ Directory is not empty\n"
                f"Path: {dir_path}\n"
                f"Use recursive=true to delete non-empty directories"
            )


async def handle_directory_tree(arguments: Dict[str, Any], config: ServerConfig) -> str:
    """
    Show directory tree structure
    
    Args:
        arguments: {
            "directory_path": str,
            "max_depth": int (optional, default: 3),
            "show_hidden": bool (optional, default: False)
        }
        config: Server configuration
        
    Returns:
        Tree structure
    """
    dir_path = validate_directory_path(arguments["directory_path"], must_exist=True)
    max_depth = arguments.get("max_depth", 3)
    show_hidden = arguments.get("show_hidden", False)
    
    if max_depth > config.max_tree_depth:
        max_depth = config.max_tree_depth
    
    # Security warnings
    warnings = get_security_warnings(dir_path, config)
    warning_text = "\n".join(warnings) + "\n\n" if warnings else ""
    
    lines = []
    
    def build_tree(current_path: str, prefix: str = "", depth: int = 0) -> None:
        """Recursively build tree structure"""
        if depth > max_depth:
            return
        
        try:
            entries = []
            with os.scandir(current_path) as it:
                for entry in it:
                    if not show_hidden and entry.name.startswith('.'):
                        continue
                    entries.append(entry)
            
            # Sort: directories first, then files
            entries.sort(key=lambda x: (not x.is_dir(), x.name.lower()))
            
            for i, entry in enumerate(entries):
                is_last = i == len(entries) - 1
                current_prefix = "└── " if is_last else "├── "
                next_prefix = "    " if is_last else "│   "
                
                if entry.is_dir():
                    lines.append(f"{prefix}{current_prefix}📁 {entry.name}/")
                    build_tree(entry.path, prefix + next_prefix, depth + 1)
                else:
                    try:
                        size = format_file_size(entry.stat().st_size)
                        lines.append(f"{prefix}{current_prefix}📄 {entry.name} ({size})")
                    except Exception:
                        lines.append(f"{prefix}{current_prefix}📄 {entry.name}")
        
        except PermissionError:
            lines.append(f"{prefix}❌ Permission denied")
    
    # Start with root
    lines.append(f"📁 {os.path.basename(dir_path) or dir_path}/")
    build_tree(dir_path, "", 0)
    
    tree = "\n".join(lines)
    
    return (
        f"{warning_text}"
        f"Directory Tree (max depth: {max_depth})\n"
        f"{'=' * 50}\n"
        f"{tree}"
    )

