"""
Image operations handlers for MCP
Provides image viewing support with auto-compression
"""

import base64
import mimetypes
from pathlib import Path
from typing import Dict, Any

try:
    from PIL import Image
    import io
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

from ..config import ServerConfig, IMAGE_EXTENSIONS
from ..utils import validate_filename


async def handle_get_image(arguments: Dict[str, Any], config: ServerConfig) -> str:
    """
    Get image as base64 for MCP clients
    
    Args:
        file_path: Path to image file
        max_size: Optional max dimension (default: 1920)
        quality: Optional JPEG quality (default: 85)
    
    Returns:
        Base64 encoded image with metadata
    """
    file_path = arguments.get("file_path")
    max_size = arguments.get("max_size", config.max_image_dimension)
    quality = arguments.get("quality", 85)
    
    if not file_path:
        raise ValueError("file_path is required")
    
    # Validate and resolve path
    validate_filename(file_path)
    path = Path(file_path).resolve()
    
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {file_path}")
    
    if not path.is_file():
        raise ValueError(f"Not a file: {file_path}")
    
    # Check if it's an image by extension
    if path.suffix.lower() not in IMAGE_EXTENSIONS:
        raise ValueError(f"Not an image file: {file_path} (extension: {path.suffix})")
    
    # Get file info
    file_size = path.stat().st_size
    mime_type, _ = mimetypes.guess_type(str(path))
    if not mime_type:
        mime_type = 'image/jpeg'
    
    # Check if compression is needed
    max_file_size = config.max_image_size_mb * 1024 * 1024
    needs_compression = file_size > max_file_size
    
    if needs_compression and config.enable_image_compression and PIL_AVAILABLE:
        try:
            # Open and process image
            img = Image.open(path)
            
            # Preserve EXIF orientation
            try:
                from PIL import ImageOps
                img = ImageOps.exif_transpose(img)
            except:
                pass
            
            # Resize if needed
            if img.width > max_size or img.height > max_size:
                img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            # Save to bytes
            output = io.BytesIO()
            
            # Determine format
            if img.format == 'PNG' and img.mode == 'RGBA':
                img.save(output, format='PNG', optimize=True)
                mime_type = 'image/png'
            else:
                # Convert to RGB if needed
                if img.mode not in ('RGB', 'L'):
                    img = img.convert('RGB')
                img.save(output, format='JPEG', quality=quality, optimize=True)
                mime_type = 'image/jpeg'
            
            image_data = output.getvalue()
            compressed = True
            
        except Exception as e:
            # If compression fails, use original (if under hard limit)
            if file_size < 20 * 1024 * 1024:
                with open(path, 'rb') as f:
                    image_data = f.read()
                compressed = False
            else:
                raise ValueError(f"Image too large and compression failed: {str(e)}")
    else:
        # Use original image
        with open(path, 'rb') as f:
            image_data = f.read()
        compressed = False
    
    # Encode to base64
    base64_data = base64.b64encode(image_data).decode('utf-8')
    data_url = f"data:{mime_type};base64,{base64_data}"
    
    # Format response
    result = f"""📷 Image: {path.name}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📁 Path: {path}
📊 Type: {mime_type}
💾 Original Size: {file_size:,} bytes ({file_size / 1024 / 1024:.2f} MB)
💾 Returned Size: {len(image_data):,} bytes ({len(image_data) / 1024 / 1024:.2f} MB)
{'🔧 Compressed: Yes (quality: ' + str(quality) + ')' if compressed else '✓ Original: No compression needed'}
📐 Max Dimension: {max_size}px

🔗 Data URL (Base64):
{data_url[:100]}... ({len(base64_data):,} characters)

💡 To view in browser, copy the full data URL or use in <img> tag:
<img src="{data_url[:50]}..." />

Note: MCP clients may display this image automatically.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    return result


async def handle_list_images(arguments: Dict[str, Any], config: ServerConfig) -> str:
    """
    List all image files in a directory
    
    Args:
        directory_path: Path to directory
        recursive: Optional, search subdirectories (default: False)
    
    Returns:
        List of image files with metadata
    """
    directory_path = arguments.get("directory_path")
    recursive = arguments.get("recursive", False)
    
    if not directory_path:
        raise ValueError("directory_path is required")
    
    validate_filename(directory_path)
    path = Path(directory_path).resolve()
    
    if not path.exists():
        raise FileNotFoundError(f"Directory not found: {directory_path}")
    
    if not path.is_dir():
        raise ValueError(f"Not a directory: {directory_path}")
    
    # Find image files
    images = []
    
    if recursive:
        pattern = "**/*"
    else:
        pattern = "*"
    
    for item in path.glob(pattern):
        if item.is_file() and item.suffix.lower() in IMAGE_EXTENSIONS:
            size = item.stat().st_size
            mime_type, _ = mimetypes.guess_type(str(item))
            
            images.append({
                'name': item.name,
                'path': str(item),
                'extension': item.suffix,
                'size_bytes': size,
                'size_mb': round(size / 1024 / 1024, 2),
                'mime_type': mime_type or 'unknown'
            })
    
    # Sort by name
    images.sort(key=lambda x: x['name'])
    
    # Format output
    result = f"""🖼️  Images in: {path}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Total: {len(images)} image(s)
{'🔄 Recursive: Yes' if recursive else '📂 Recursive: No'}

"""
    
    if not images:
        result += "❌ No image files found.\n"
    else:
        for i, img in enumerate(images, 1):
            result += f"""
{i}. 📷 {img['name']}
   Path: {img['path']}
   Type: {img['mime_type']}
   Size: {img['size_mb']} MB ({img['size_bytes']:,} bytes)
"""
    
    result += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    result += f"💡 Use get_image tool with any path to view the image.\n"
    
    return result

