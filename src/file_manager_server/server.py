"""
MCP File Manager Server

Main server implementation with full file system operations support.
"""

import asyncio
import logging
from typing import Any, Sequence
import traceback

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .config import ServerConfig
from .handlers import (
    # File operations
    handle_read_file,
    handle_write_file,
    handle_append_file,
    handle_delete_file,
    handle_file_exists,
    handle_get_file_info,
    # Directory operations
    handle_list_directory,
    handle_create_directory,
    handle_delete_directory,
    handle_directory_tree,
    # Advanced operations
    handle_copy_file,
    handle_move_file,
    handle_rename_file,
    handle_search_files,
    handle_read_multiple_files,
    # Search operations
    handle_search_in_files,
    handle_find_files_by_pattern,
    # Image operations
    handle_get_image,
    handle_list_images,
)

# Special features will be imported after implementation
try:
    from .handlers.special_operations import (
        handle_compress_file,
        handle_decompress_file,
        handle_get_file_hash,
    )
    SPECIAL_FEATURES_AVAILABLE = True
except ImportError:
    SPECIAL_FEATURES_AVAILABLE = False


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Initialize server
app = Server("file-manager")
config = ServerConfig.from_env()


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available tools"""
    tools = [
        # File operations
        Tool(
            name="read_file",
            description="Read file contents. Supports both text and binary files. Binary files are returned as base64.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file to read"
                    },
                    "encoding": {
                        "type": "string",
                        "description": "Text encoding (optional, auto-detected if not specified)",
                        "default": "utf-8"
                    },
                    "as_base64": {
                        "type": "boolean",
                        "description": "Force base64 encoding for binary content",
                        "default": False
                    }
                },
                "required": ["file_path"]
            }
        ),
        Tool(
            name="write_file",
            description="Write content to a file. Creates parent directories if needed. Can write both text and binary (base64) content.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file to write"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write to the file"
                    },
                    "encoding": {
                        "type": "string",
                        "description": "Text encoding",
                        "default": "utf-8"
                    },
                    "is_base64": {
                        "type": "boolean",
                        "description": "Whether content is base64 encoded",
                        "default": False
                    }
                },
                "required": ["file_path", "content"]
            }
        ),
        Tool(
            name="append_file",
            description="Append content to the end of a file. Creates the file if it doesn't exist.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to append"
                    },
                    "encoding": {
                        "type": "string",
                        "description": "Text encoding",
                        "default": "utf-8"
                    }
                },
                "required": ["file_path", "content"]
            }
        ),
        Tool(
            name="delete_file",
            description="Delete a file. Protected files trigger security warnings.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file to delete"
                    }
                },
                "required": ["file_path"]
            }
        ),
        Tool(
            name="file_exists",
            description="Check if a file exists.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to check"
                    }
                },
                "required": ["file_path"]
            }
        ),
        Tool(
            name="get_file_info",
            description="Get detailed file metadata (size, dates, permissions).",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file"
                    }
                },
                "required": ["file_path"]
            }
        ),
        
        # Directory operations
        Tool(
            name="list_directory",
            description="List directory contents. Supports recursive listing and glob patterns.",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory_path": {
                        "type": "string",
                        "description": "Path to the directory"
                    },
                    "recursive": {
                        "type": "boolean",
                        "description": "List recursively",
                        "default": False
                    },
                    "show_hidden": {
                        "type": "boolean",
                        "description": "Show hidden files (starting with .)",
                        "default": False
                    },
                    "pattern": {
                        "type": "string",
                        "description": "Glob pattern to filter files (e.g., '*.py')"
                    }
                },
                "required": ["directory_path"]
            }
        ),
        Tool(
            name="create_directory",
            description="Create a new directory. Can create parent directories.",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory_path": {
                        "type": "string",
                        "description": "Path to the directory to create"
                    },
                    "parents": {
                        "type": "boolean",
                        "description": "Create parent directories if needed",
                        "default": True
                    }
                },
                "required": ["directory_path"]
            }
        ),
        Tool(
            name="delete_directory",
            description="Delete a directory. Can delete recursively.",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory_path": {
                        "type": "string",
                        "description": "Path to the directory to delete"
                    },
                    "recursive": {
                        "type": "boolean",
                        "description": "Delete directory contents recursively",
                        "default": False
                    }
                },
                "required": ["directory_path"]
            }
        ),
        Tool(
            name="directory_tree",
            description="Show directory structure as a tree.",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory_path": {
                        "type": "string",
                        "description": "Path to the directory"
                    },
                    "max_depth": {
                        "type": "integer",
                        "description": "Maximum depth to display",
                        "default": 3
                    },
                    "show_hidden": {
                        "type": "boolean",
                        "description": "Show hidden files",
                        "default": False
                    }
                },
                "required": ["directory_path"]
            }
        ),
        
        # Advanced operations
        Tool(
            name="copy_file",
            description="Copy a file to a new location.",
            inputSchema={
                "type": "object",
                "properties": {
                    "source_path": {
                        "type": "string",
                        "description": "Source file path"
                    },
                    "destination_path": {
                        "type": "string",
                        "description": "Destination file path"
                    },
                    "overwrite": {
                        "type": "boolean",
                        "description": "Overwrite if destination exists",
                        "default": False
                    }
                },
                "required": ["source_path", "destination_path"]
            }
        ),
        Tool(
            name="move_file",
            description="Move a file to a new location.",
            inputSchema={
                "type": "object",
                "properties": {
                    "source_path": {
                        "type": "string",
                        "description": "Source file path"
                    },
                    "destination_path": {
                        "type": "string",
                        "description": "Destination file path"
                    },
                    "overwrite": {
                        "type": "boolean",
                        "description": "Overwrite if destination exists",
                        "default": False
                    }
                },
                "required": ["source_path", "destination_path"]
            }
        ),
        Tool(
            name="rename_file",
            description="Rename a file.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file to rename"
                    },
                    "new_name": {
                        "type": "string",
                        "description": "New filename (not full path, just the name)"
                    },
                    "overwrite": {
                        "type": "boolean",
                        "description": "Overwrite if file with new name exists",
                        "default": False
                    }
                },
                "required": ["file_path", "new_name"]
            }
        ),
        Tool(
            name="search_in_files",
            description="Search for text content within files.",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory_path": {
                        "type": "string",
                        "description": "Directory to search in"
                    },
                    "search_text": {
                        "type": "string",
                        "description": "Text to search for"
                    },
                    "file_pattern": {
                        "type": "string",
                        "description": "File pattern to filter (e.g., '*.py')",
                        "default": "*"
                    },
                    "case_sensitive": {
                        "type": "boolean",
                        "description": "Case sensitive search",
                        "default": False
                    },
                    "regex": {
                        "type": "boolean",
                        "description": "Treat search_text as regex",
                        "default": False
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results"
                    }
                },
                "required": ["directory_path", "search_text"]
            }
        ),
        Tool(
            name="find_files",
            description="Find files by name pattern.",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory_path": {
                        "type": "string",
                        "description": "Directory to search in"
                    },
                    "pattern": {
                        "type": "string",
                        "description": "File name pattern (e.g., '*.txt', 'test_*.py')"
                    },
                    "case_sensitive": {
                        "type": "boolean",
                        "description": "Case sensitive search",
                        "default": False
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results"
                    }
                },
                "required": ["directory_path", "pattern"]
            }
        ),
        Tool(
            name="read_multiple_files",
            description="Read multiple files at once.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_paths": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of file paths to read"
                    },
                    "encoding": {
                        "type": "string",
                        "description": "Text encoding for all files"
                    }
                },
                "required": ["file_paths"]
            }
        ),
    ]
    
    # Add special features if available
    if SPECIAL_FEATURES_AVAILABLE and config.enable_compression:
        tools.extend([
            Tool(
                name="compress_file",
                description="Compress a file or directory to ZIP format.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "source_path": {
                            "type": "string",
                            "description": "Path to file or directory to compress"
                        },
                        "output_path": {
                            "type": "string",
                            "description": "Output ZIP file path"
                        }
                    },
                    "required": ["source_path", "output_path"]
                }
            ),
            Tool(
                name="decompress_file",
                description="Extract a ZIP archive.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "archive_path": {
                            "type": "string",
                            "description": "Path to ZIP file"
                        },
                        "output_directory": {
                            "type": "string",
                            "description": "Directory to extract to"
                        }
                    },
                    "required": ["archive_path", "output_directory"]
                }
            ),
        ])
    
    if SPECIAL_FEATURES_AVAILABLE and config.enable_hashing:
        tools.append(
            Tool(
                name="get_file_hash",
                description="Calculate file hash (MD5, SHA256, etc.).",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the file"
                        },
                        "algorithm": {
                            "type": "string",
                            "description": "Hash algorithm (md5, sha1, sha256, sha512)",
                            "default": "sha256"
                        }
                    },
                    "required": ["file_path"]
                }
            )
        )
    
    # Image operations (GPT Vision support)
    tools.extend([
        Tool(
            name="get_image",
            description="Get image as base64 data URL for viewing. Supports OneDrive paths, symlinks, and auto-compression for large images. Returns base64 encoded image with metadata.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to image file (supports .jpg, .jpeg, .png, .gif, .bmp, .webp, .svg, .ico, .tiff)"
                    },
                    "max_size": {
                        "type": "integer",
                        "description": "Maximum dimension in pixels (width/height)",
                        "default": 1920
                    },
                    "quality": {
                        "type": "integer",
                        "description": "JPEG quality (1-100) for compression",
                        "default": 85
                    }
                },
                "required": ["file_path"]
            }
        ),
        Tool(
            name="list_images",
            description="List all image files in a directory. Shows file names, paths, sizes, and types.",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory_path": {
                        "type": "string",
                        "description": "Path to directory"
                    },
                    "recursive": {
                        "type": "boolean",
                        "description": "Search subdirectories recursively",
                        "default": False
                    }
                },
                "required": ["directory_path"]
            }
        ),
    ])
    
    return tools


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent]:
    """Handle tool calls"""
    try:
        logger.info(f"Tool called: {name} with arguments: {arguments}")
        
        # Route to appropriate handler
        result = None
        
        # File operations
        if name == "read_file":
            result = await handle_read_file(arguments, config)
        elif name == "write_file":
            result = await handle_write_file(arguments, config)
        elif name == "append_file":
            result = await handle_append_file(arguments, config)
        elif name == "delete_file":
            result = await handle_delete_file(arguments, config)
        elif name == "file_exists":
            result = await handle_file_exists(arguments, config)
        elif name == "get_file_info":
            result = await handle_get_file_info(arguments, config)
        
        # Directory operations
        elif name == "list_directory":
            result = await handle_list_directory(arguments, config)
        elif name == "create_directory":
            result = await handle_create_directory(arguments, config)
        elif name == "delete_directory":
            result = await handle_delete_directory(arguments, config)
        elif name == "directory_tree":
            result = await handle_directory_tree(arguments, config)
        
        # Advanced operations
        elif name == "copy_file":
            result = await handle_copy_file(arguments, config)
        elif name == "move_file":
            result = await handle_move_file(arguments, config)
        elif name == "rename_file":
            result = await handle_rename_file(arguments, config)
        elif name == "search_in_files":
            result = await handle_search_in_files(arguments, config)
        elif name == "find_files":
            result = await handle_find_files_by_pattern(arguments, config)
        elif name == "read_multiple_files":
            result = await handle_read_multiple_files(arguments, config)
        
        # Special operations
        elif SPECIAL_FEATURES_AVAILABLE:
            if name == "compress_file" and config.enable_compression:
                result = await handle_compress_file(arguments, config)
            elif name == "decompress_file" and config.enable_compression:
                result = await handle_decompress_file(arguments, config)
            elif name == "get_file_hash" and config.enable_hashing:
                result = await handle_get_file_hash(arguments, config)
        
        # Image operations
        elif name == "get_image":
            result = await handle_get_image(arguments, config)
        elif name == "list_images":
            result = await handle_list_images(arguments, config)
        
        if result is None:
            result = f"❌ Unknown tool: {name}"
        
        logger.info(f"Tool {name} completed successfully")
        return [TextContent(type="text", text=result)]
    
    except Exception as e:
        error_msg = f"❌ Error executing {name}: {str(e)}\n\n{traceback.format_exc()}"
        logger.error(error_msg)
        return [TextContent(type="text", text=error_msg)]


async def run_server():
    """Run the MCP server"""
    logger.info("Starting MCP File Manager Server")
    logger.info(f"Configuration: {config}")
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


def main():
    """Main entry point"""
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise


if __name__ == "__main__":
    main()

