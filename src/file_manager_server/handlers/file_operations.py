"""
File operation handlers
"""

import os
import base64
from datetime import datetime
from typing import Any, Dict
import aiofiles

from ..config import ServerConfig
from ..utils import (
    validate_file_path,
    validate_path,
    get_security_warnings,
    is_binary_file,
    detect_encoding,
    format_file_size,
    get_file_type,
)


async def handle_read_file(arguments: Dict[str, Any], config: ServerConfig) -> str:
    """
    Read file contents
    
    Args:
        arguments: {
            "file_path": str,
            "encoding": str (optional, default: auto-detect),
            "as_base64": bool (optional, for binary files)
        }
        config: Server configuration
        
    Returns:
        File contents as string
    """
    file_path = validate_file_path(arguments["file_path"], must_exist=True)
    encoding = arguments.get("encoding")
    as_base64 = arguments.get("as_base64", False)
    
    # Security warnings
    warnings = get_security_warnings(file_path, config)
    warning_text = "\n".join(warnings) + "\n\n" if warnings else ""
    
    # Check if binary
    is_binary = is_binary_file(file_path)
    
    if is_binary or as_base64:
        # Read as binary and encode to base64
        async with aiofiles.open(file_path, 'rb') as f:
            content = await f.read()
            encoded = base64.b64encode(content).decode('ascii')
            file_size = format_file_size(len(content))
            return (
                f"{warning_text}"
                f"File: {file_path}\n"
                f"Type: binary\n"
                f"Size: {file_size}\n"
                f"Encoding: base64\n\n"
                f"{encoded}"
            )
    else:
        # Read as text
        if not encoding:
            encoding = detect_encoding(file_path)
        
        try:
            async with aiofiles.open(file_path, 'r', encoding=encoding) as f:
                content = await f.read()
                file_size = format_file_size(os.path.getsize(file_path))
                return (
                    f"{warning_text}"
                    f"File: {file_path}\n"
                    f"Type: text\n"
                    f"Size: {file_size}\n"
                    f"Encoding: {encoding}\n\n"
                    f"{content}"
                )
        except UnicodeDecodeError:
            # Fallback to binary
            async with aiofiles.open(file_path, 'rb') as f:
                content = await f.read()
                encoded = base64.b64encode(content).decode('ascii')
                file_size = format_file_size(len(content))
                return (
                    f"{warning_text}"
                    f"File: {file_path}\n"
                    f"Type: binary (failed to decode as text)\n"
                    f"Size: {file_size}\n"
                    f"Encoding: base64\n\n"
                    f"{encoded}"
                )


async def handle_write_file(arguments: Dict[str, Any], config: ServerConfig) -> str:
    """
    Write file contents
    
    Args:
        arguments: {
            "file_path": str,
            "content": str,
            "encoding": str (optional, default: utf-8),
            "is_base64": bool (optional, if content is base64 encoded)
        }
        config: Server configuration
        
    Returns:
        Success message
    """
    file_path = validate_path(arguments["file_path"])
    content = arguments["content"]
    encoding = arguments.get("encoding", "utf-8")
    is_base64_content = arguments.get("is_base64", False)
    
    # Security warnings
    warnings = get_security_warnings(file_path, config)
    warning_text = "\n".join(warnings) + "\n\n" if warnings else ""
    
    # Create parent directory if needed
    parent_dir = os.path.dirname(file_path)
    if parent_dir and not os.path.exists(parent_dir):
        os.makedirs(parent_dir, exist_ok=True)
    
    if is_base64_content:
        # Decode base64 and write binary
        try:
            binary_content = base64.b64decode(content)
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(binary_content)
            file_size = format_file_size(len(binary_content))
            return (
                f"{warning_text}"
                f"✅ File written successfully\n"
                f"Path: {file_path}\n"
                f"Type: binary\n"
                f"Size: {file_size}"
            )
        except Exception as e:
            raise ValueError(f"Failed to decode base64 content: {e}")
    else:
        # Write as text
        async with aiofiles.open(file_path, 'w', encoding=encoding) as f:
            await f.write(content)
        file_size = format_file_size(len(content.encode(encoding)))
        return (
            f"{warning_text}"
            f"✅ File written successfully\n"
            f"Path: {file_path}\n"
            f"Type: text\n"
            f"Size: {file_size}\n"
            f"Encoding: {encoding}"
        )


async def handle_append_file(arguments: Dict[str, Any], config: ServerConfig) -> str:
    """
    Append content to file
    
    Args:
        arguments: {
            "file_path": str,
            "content": str,
            "encoding": str (optional, default: utf-8)
        }
        config: Server configuration
        
    Returns:
        Success message
    """
    file_path = validate_path(arguments["file_path"])
    content = arguments["content"]
    encoding = arguments.get("encoding", "utf-8")
    
    # Security warnings
    warnings = get_security_warnings(file_path, config)
    warning_text = "\n".join(warnings) + "\n\n" if warnings else ""
    
    # Create parent directory if needed
    parent_dir = os.path.dirname(file_path)
    if parent_dir and not os.path.exists(parent_dir):
        os.makedirs(parent_dir, exist_ok=True)
    
    async with aiofiles.open(file_path, 'a', encoding=encoding) as f:
        await f.write(content)
    
    file_size = format_file_size(os.path.getsize(file_path))
    return (
        f"{warning_text}"
        f"✅ Content appended successfully\n"
        f"Path: {file_path}\n"
        f"New size: {file_size}\n"
        f"Encoding: {encoding}"
    )


async def handle_delete_file(arguments: Dict[str, Any], config: ServerConfig) -> str:
    """
    Delete a file
    
    Args:
        arguments: {
            "file_path": str
        }
        config: Server configuration
        
    Returns:
        Success message
    """
    file_path = validate_file_path(arguments["file_path"], must_exist=True)
    
    # Check for critical security issues only
    from ..utils.security import is_system_critical_path, is_dangerous_file
    
    is_critical, critical_msg = is_system_critical_path(file_path)
    is_dangerous, dangerous_msg = is_dangerous_file(file_path)
    
    # Block deletion only for system-critical paths or dangerous executables
    if is_critical or (is_dangerous and not config.enable_dangerous_operations):
        blocking_warnings = []
        if is_critical:
            blocking_warnings.append(critical_msg)
        if is_dangerous:
            blocking_warnings.append(dangerous_msg)
        
        warning_text = "\n".join(blocking_warnings)
        return (
            f"⚠️  DELETION BLOCKED\n\n"
            f"{warning_text}\n\n"
            f"File was NOT deleted. For system-critical files, deletion is always blocked. "
            f"For dangerous files, set ENABLE_DANGEROUS_OPERATIONS=true to allow deletion."
        )
    
    file_size = format_file_size(os.path.getsize(file_path))
    os.remove(file_path)
    
    return (
        f"✅ File deleted successfully\n"
        f"Path: {file_path}\n"
        f"Size: {file_size}"
    )


async def handle_file_exists(arguments: Dict[str, Any], config: ServerConfig) -> str:
    """
    Check if file exists
    
    Args:
        arguments: {
            "file_path": str
        }
        config: Server configuration
        
    Returns:
        Existence status
    """
    file_path = validate_path(arguments["file_path"])
    exists = os.path.exists(file_path) and os.path.isfile(file_path)
    
    if exists:
        file_size = format_file_size(os.path.getsize(file_path))
        file_type = get_file_type(file_path)
        return (
            f"✅ File exists\n"
            f"Path: {file_path}\n"
            f"Type: {file_type}\n"
            f"Size: {file_size}"
        )
    else:
        return f"❌ File does not exist\nPath: {file_path}"


async def handle_get_file_info(arguments: Dict[str, Any], config: ServerConfig) -> str:
    """
    Get file metadata
    
    Args:
        arguments: {
            "file_path": str
        }
        config: Server configuration
        
    Returns:
        File metadata
    """
    file_path = validate_file_path(arguments["file_path"], must_exist=True)
    
    stat = os.stat(file_path)
    
    # Format timestamps
    created = datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S")
    modified = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
    accessed = datetime.fromtimestamp(stat.st_atime).strftime("%Y-%m-%d %H:%M:%S")
    
    # File type
    file_type = get_file_type(file_path)
    
    # File size
    file_size = format_file_size(stat.st_size)
    
    # Permissions (Unix-style)
    import stat as stat_module
    permissions = stat_module.filemode(stat.st_mode)
    
    return (
        f"📄 File Information\n"
        f"{'=' * 50}\n"
        f"Path: {file_path}\n"
        f"Type: {file_type}\n"
        f"Size: {file_size} ({stat.st_size:,} bytes)\n"
        f"Permissions: {permissions}\n"
        f"Created: {created}\n"
        f"Modified: {modified}\n"
        f"Accessed: {accessed}\n"
    )

