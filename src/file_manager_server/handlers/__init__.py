"""
Handler modules for file operations
"""

from .file_operations import (
    handle_read_file,
    handle_write_file,
    handle_append_file,
    handle_delete_file,
    handle_file_exists,
    handle_get_file_info,
)

from .directory_operations import (
    handle_list_directory,
    handle_create_directory,
    handle_delete_directory,
    handle_directory_tree,
)

from .advanced_operations import (
    handle_copy_file,
    handle_move_file,
    handle_rename_file,
    handle_search_files,
    handle_read_multiple_files,
)

from .search_operations import (
    handle_search_in_files,
    handle_find_files_by_pattern,
)

from .image_operations import (
    handle_get_image,
    handle_list_images,
)

__all__ = [
    # File operations
    "handle_read_file",
    "handle_write_file",
    "handle_append_file",
    "handle_delete_file",
    "handle_file_exists",
    "handle_get_file_info",
    # Directory operations
    "handle_list_directory",
    "handle_create_directory",
    "handle_delete_directory",
    "handle_directory_tree",
    # Advanced operations
    "handle_copy_file",
    "handle_move_file",
    "handle_rename_file",
    "handle_search_files",
    "handle_read_multiple_files",
    # Search operations
    "handle_search_in_files",
    "handle_find_files_by_pattern",
    # Image operations
    "handle_get_image",
    "handle_list_images",
]

