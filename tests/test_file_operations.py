"""
Tests for file operations
"""

import pytest
import os
import tempfile
import shutil
from pathlib import Path

from file_manager_server.config import ServerConfig
from file_manager_server.handlers.file_operations import (
    handle_read_file,
    handle_write_file,
    handle_append_file,
    handle_delete_file,
    handle_file_exists,
    handle_get_file_info,
)


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
        max_file_size_mb=10,
        enable_dangerous_operations=True
    )


@pytest.mark.asyncio
async def test_write_and_read_file(temp_dir, config):
    """Test writing and reading a file"""
    file_path = os.path.join(temp_dir, "test.txt")
    content = "Hello, World!"
    
    # Write file
    result = await handle_write_file({
        "file_path": file_path,
        "content": content
    }, config)
    
    assert "✅" in result
    assert os.path.exists(file_path)
    
    # Read file
    result = await handle_read_file({
        "file_path": file_path
    }, config)
    
    assert content in result


@pytest.mark.asyncio
async def test_append_file(temp_dir, config):
    """Test appending to a file"""
    file_path = os.path.join(temp_dir, "test.txt")
    
    # Write initial content
    await handle_write_file({
        "file_path": file_path,
        "content": "Line 1\n"
    }, config)
    
    # Append content
    await handle_append_file({
        "file_path": file_path,
        "content": "Line 2\n"
    }, config)
    
    # Read and verify
    result = await handle_read_file({
        "file_path": file_path
    }, config)
    
    assert "Line 1" in result
    assert "Line 2" in result


@pytest.mark.asyncio
async def test_delete_file(temp_dir, config):
    """Test deleting a file"""
    file_path = os.path.join(temp_dir, "test.txt")
    
    # Create file
    await handle_write_file({
        "file_path": file_path,
        "content": "Test"
    }, config)
    
    assert os.path.exists(file_path)
    
    # Delete file
    result = await handle_delete_file({
        "file_path": file_path
    }, config)
    
    assert "✅" in result
    assert not os.path.exists(file_path)


@pytest.mark.asyncio
async def test_file_exists(temp_dir, config):
    """Test file existence check"""
    file_path = os.path.join(temp_dir, "test.txt")
    
    # Check non-existent file
    result = await handle_file_exists({
        "file_path": file_path
    }, config)
    
    assert "❌" in result or "does not exist" in result
    
    # Create file
    await handle_write_file({
        "file_path": file_path,
        "content": "Test"
    }, config)
    
    # Check existing file
    result = await handle_file_exists({
        "file_path": file_path
    }, config)
    
    assert "✅" in result or "exists" in result.lower()


@pytest.mark.asyncio
async def test_get_file_info(temp_dir, config):
    """Test getting file metadata"""
    file_path = os.path.join(temp_dir, "test.txt")
    content = "Test content"
    
    # Create file
    await handle_write_file({
        "file_path": file_path,
        "content": content
    }, config)
    
    # Get info
    result = await handle_get_file_info({
        "file_path": file_path
    }, config)
    
    assert file_path in result
    assert "Size:" in result
    assert "Modified:" in result


@pytest.mark.asyncio
async def test_write_binary_file(temp_dir, config):
    """Test writing binary file with base64"""
    import base64
    
    file_path = os.path.join(temp_dir, "test.bin")
    binary_data = b"\x00\x01\x02\x03\x04"
    base64_content = base64.b64encode(binary_data).decode('ascii')
    
    # Write binary file
    result = await handle_write_file({
        "file_path": file_path,
        "content": base64_content,
        "is_base64": True
    }, config)
    
    assert "✅" in result
    
    # Verify content
    with open(file_path, 'rb') as f:
        assert f.read() == binary_data


@pytest.mark.asyncio
async def test_read_with_encoding(temp_dir, config):
    """Test reading file with specific encoding"""
    file_path = os.path.join(temp_dir, "test_utf8.txt")
    content = "Türkçe karakterler: ğüşıöç"
    
    # Write with UTF-8
    await handle_write_file({
        "file_path": file_path,
        "content": content,
        "encoding": "utf-8"
    }, config)
    
    # Read with UTF-8
    result = await handle_read_file({
        "file_path": file_path,
        "encoding": "utf-8"
    }, config)
    
    assert "Türkçe" in result

