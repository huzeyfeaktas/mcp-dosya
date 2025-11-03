"""
Search operation handlers
"""

import os
import re
from typing import Any, Dict, List
import aiofiles

from ..config import ServerConfig
from ..utils import (
    validate_directory_path,
    validate_search_pattern,
    format_file_size,
    is_binary_file,
    detect_encoding,
)


async def handle_search_in_files(arguments: Dict[str, Any], config: ServerConfig) -> str:
    """
    Search for text in files
    
    Args:
        arguments: {
            "directory_path": str,
            "search_text": str,
            "file_pattern": str (optional, e.g., "*.py"),
            "case_sensitive": bool (optional, default: False),
            "regex": bool (optional, default: False),
            "max_results": int (optional)
        }
        config: Server configuration
        
    Returns:
        Search results
    """
    dir_path = validate_directory_path(arguments["directory_path"], must_exist=True)
    search_text = arguments["search_text"]
    file_pattern = arguments.get("file_pattern", "*")
    case_sensitive = arguments.get("case_sensitive", False)
    use_regex = arguments.get("regex", False)
    max_results = arguments.get("max_results", config.max_search_results)
    
    if use_regex:
        validate_search_pattern(search_text)
        flags = 0 if case_sensitive else re.IGNORECASE
        pattern = re.compile(search_text, flags)
    else:
        if not case_sensitive:
            search_text = search_text.lower()
    
    results = []
    files_searched = 0
    
    # Walk through directory
    for root, _, files in os.walk(dir_path):
        for filename in files:
            # Apply file pattern
            import fnmatch
            if not fnmatch.fnmatch(filename, file_pattern):
                continue
            
            file_path = os.path.join(root, filename)
            
            # Skip binary files
            if is_binary_file(file_path):
                continue
            
            files_searched += 1
            
            try:
                encoding = detect_encoding(file_path)
                async with aiofiles.open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                    line_num = 0
                    async for line in f:
                        line_num += 1
                        
                        # Search in line
                        found = False
                        if use_regex:
                            match = pattern.search(line)
                            found = match is not None
                        else:
                            search_in = line if case_sensitive else line.lower()
                            found = search_text in search_in
                        
                        if found:
                            rel_path = os.path.relpath(file_path, dir_path)
                            results.append({
                                'file': rel_path,
                                'line_num': line_num,
                                'line': line.rstrip()
                            })
                            
                            if len(results) >= max_results:
                                break
                
                if len(results) >= max_results:
                    break
            
            except Exception:
                continue  # Skip files we can't read
        
        if len(results) >= max_results:
            break
    
    # Format results
    if not results:
        return (
            f"🔍 Search Results\n"
            f"{'=' * 50}\n"
            f"Directory: {dir_path}\n"
            f"Search text: '{search_text}'\n"
            f"Files searched: {files_searched}\n"
            f"Matches found: 0"
        )
    
    output_lines = [
        f"🔍 Search Results",
        f"{'=' * 50}",
        f"Directory: {dir_path}",
        f"Search text: '{search_text}'",
        f"Files searched: {files_searched}",
        f"Matches found: {len(results)}",
        "",
    ]
    
    current_file = None
    for result in results:
        if result['file'] != current_file:
            current_file = result['file']
            output_lines.append(f"\n📄 {current_file}:")
        
        output_lines.append(f"  Line {result['line_num']}: {result['line']}")
    
    if len(results) >= max_results:
        output_lines.append(f"\n⚠️  Showing first {max_results} results. There may be more matches.")
    
    return "\n".join(output_lines)


async def handle_find_files_by_pattern(arguments: Dict[str, Any], config: ServerConfig) -> str:
    """
    Find files by name pattern
    
    Args:
        arguments: {
            "directory_path": str,
            "pattern": str (glob pattern, e.g., "*.py"),
            "case_sensitive": bool (optional, default: False),
            "max_results": int (optional)
        }
        config: Server configuration
        
    Returns:
        List of matching files
    """
    dir_path = validate_directory_path(arguments["directory_path"], must_exist=True)
    pattern = arguments["pattern"]
    case_sensitive = arguments.get("case_sensitive", False)
    max_results = arguments.get("max_results", config.max_search_results)
    
    import fnmatch
    
    results = []
    
    # Walk through directory
    for root, dirs, files in os.walk(dir_path):
        for filename in files:
            # Apply pattern
            if case_sensitive:
                match = fnmatch.fnmatch(filename, pattern)
            else:
                match = fnmatch.fnmatch(filename.lower(), pattern.lower())
            
            if match:
                file_path = os.path.join(root, filename)
                rel_path = os.path.relpath(file_path, dir_path)
                
                try:
                    stat = os.stat(file_path)
                    size = format_file_size(stat.st_size)
                    results.append(f"  📄 {rel_path} ({size})")
                except Exception:
                    results.append(f"  📄 {rel_path}")
                
                if len(results) >= max_results:
                    break
        
        if len(results) >= max_results:
            break
    
    if not results:
        return (
            f"🔍 File Search Results\n"
            f"{'=' * 50}\n"
            f"Directory: {dir_path}\n"
            f"Pattern: '{pattern}'\n"
            f"Matches found: 0"
        )
    
    output = (
        f"🔍 File Search Results\n"
        f"{'=' * 50}\n"
        f"Directory: {dir_path}\n"
        f"Pattern: '{pattern}'\n"
        f"Matches found: {len(results)}\n\n"
        f"{chr(10).join(results)}"
    )
    
    if len(results) >= max_results:
        output += f"\n\n⚠️  Showing first {max_results} results. There may be more matches."
    
    return output

