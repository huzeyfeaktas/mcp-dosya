"""
Tests for directory operations
"""

import pytest
import os
import tempfile
import shutil

from file_manager_server.config import ServerConfig
from file_manager_server.handlers.directory_operations import (
    handle_list_directory,
    handle_create_directory,
    handle_delete_directory,
    handle_directory_tree,
)
from file_manager_server.handlers.file_operations import handle_write_file


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests"""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def config():
    """Create test configuration"""
    return ServerConfig(
        log_level="DEBUG",
        enable_dangerous_operations=True
    )


@pytest.mark.asyncio
async def test_create_directory(temp_dir, config):
    """Test creating a directory"""
    new_dir = os.path.join(temp_dir, "new_folder")
    
    result = await handle_create_directory({
        "directory_path": new_dir
    }, config)
    
    assert "✅" in result
    assert os.path.isdir(new_dir)


@pytest.mark.asyncio
async def test_create_nested_directory(temp_dir, config):
    """Test creating nested directories"""
    nested_dir = os.path.join(temp_dir, "level1", "level2", "level3")
    
    result = await handle_create_directory({
        "directory_path": nested_dir,
        "parents": True
    }, config)
    
    assert "✅" in result
    assert os.path.isdir(nested_dir)


@pytest.mark.asyncio
async def test_list_directory(temp_dir, config):
    """Test listing directory contents"""
    # Create some files
    await handle_write_file({
        "file_path": os.path.join(temp_dir, "file1.txt"),
        "content": "Test 1"
    }, config)
    
    await handle_write_file({
        "file_path": os.path.join(temp_dir, "file2.txt"),
        "content": "Test 2"
    }, config)
    
    # Create subdirectory
    os.mkdir(os.path.join(temp_dir, "subdir"))
    
    # List directory
    result = await handle_list_directory({
        "directory_path": temp_dir
    }, config)
    
    assert "file1.txt" in result
    assert "file2.txt" in result
    assert "subdir" in result


@pytest.mark.asyncio
async def test_list_directory_recursive(temp_dir, config):
    """Test recursive directory listing"""
    # Create nested structure
    subdir = os.path.join(temp_dir, "subdir")
    os.mkdir(subdir)
    
    await handle_write_file({
        "file_path": os.path.join(temp_dir, "root.txt"),
        "content": "Root"
    }, config)
    
    await handle_write_file({
        "file_path": os.path.join(subdir, "nested.txt"),
        "content": "Nested"
    }, config)
    
    # List recursively
    result = await handle_list_directory({
        "directory_path": temp_dir,
        "recursive": True
    }, config)
    
    assert "root.txt" in result
    assert "nested.txt" in result


@pytest.mark.asyncio
async def test_list_directory_with_pattern(temp_dir, config):
    """Test listing with file pattern"""
    # Create files with different extensions
    await handle_write_file({
        "file_path": os.path.join(temp_dir, "file1.txt"),
        "content": "Test"
    }, config)
    
    await handle_write_file({
        "file_path": os.path.join(temp_dir, "file2.py"),
        "content": "Test"
    }, config)
    
    # List only .txt files
    result = await handle_list_directory({
        "directory_path": temp_dir,
        "pattern": "*.txt"
    }, config)
    
    assert "file1.txt" in result
    assert "file2.py" not in result


@pytest.mark.asyncio
async def test_delete_empty_directory(temp_dir, config):
    """Test deleting an empty directory"""
    new_dir = os.path.join(temp_dir, "empty_dir")
    os.mkdir(new_dir)
    
    result = await handle_delete_directory({
        "directory_path": new_dir
    }, config)
    
    assert "✅" in result
    assert not os.path.exists(new_dir)


@pytest.mark.asyncio
async def test_delete_directory_recursive(temp_dir, config):
    """Test recursively deleting a directory with contents"""
    # Create directory with files
    subdir = os.path.join(temp_dir, "to_delete")
    os.mkdir(subdir)
    
    await handle_write_file({
        "file_path": os.path.join(subdir, "file.txt"),
        "content": "Test"
    }, config)
    
    # Delete recursively
    result = await handle_delete_directory({
        "directory_path": subdir,
        "recursive": True
    }, config)
    
    assert "✅" in result
    assert not os.path.exists(subdir)


@pytest.mark.asyncio
async def test_directory_tree(temp_dir, config):
    """Test directory tree display"""
    # Create nested structure
    os.mkdir(os.path.join(temp_dir, "dir1"))
    os.mkdir(os.path.join(temp_dir, "dir1", "dir2"))
    
    await handle_write_file({
        "file_path": os.path.join(temp_dir, "root.txt"),
        "content": "Root"
    }, config)
    
    await handle_write_file({
        "file_path": os.path.join(temp_dir, "dir1", "file1.txt"),
        "content": "File 1"
    }, config)
    
    # Get tree
    result = await handle_directory_tree({
        "directory_path": temp_dir,
        "max_depth": 3
    }, config)
    
    assert "root.txt" in result
    assert "dir1" in result
    assert "file1.txt" in result

