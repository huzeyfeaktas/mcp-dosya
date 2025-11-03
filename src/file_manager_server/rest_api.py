"""
REST API Wrapper for GPT and Web Clients
Wraps MCP handlers into simple REST endpoints
"""

import json
import base64
import mimetypes
import io
from pathlib import Path
from typing import Any, Dict
from aiohttp import web

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

from .config import ServerConfig, IMAGE_EXTENSIONS, ONEDRIVE_PATHS
from .handlers import (
    handle_read_file,
    handle_write_file,
    handle_append_file,
    handle_delete_file,
    handle_list_directory,
    handle_create_directory,
    handle_directory_tree,
    handle_copy_file,
    handle_move_file,
    handle_search_in_files,
    handle_find_files_by_pattern,
)

try:
    from .handlers.special_operations import (
        handle_compress_file,
        handle_get_file_hash,
    )
    SPECIAL_OPS_AVAILABLE = True
except ImportError:
    SPECIAL_OPS_AVAILABLE = False


class RestAPI:
    """REST API wrapper for MCP operations"""
    
    def __init__(self, config: ServerConfig):
        self.config = config
    
    async def read_file(self, request: web.Request) -> web.Response:
        """GET /api/read?path=<file_path>&encoding=<encoding>
        POST /api/read with JSON body (for GPT compatibility)"""
        try:
            # Support both GET (query params) and POST (JSON body)
            if request.method == 'POST':
                data = await request.json()
                file_path = data.get('path')
                encoding = data.get('encoding', 'utf-8')
            else:  # GET
                file_path = request.query.get('path')
                encoding = request.query.get('encoding', 'utf-8')
            
            if not file_path:
                return web.json_response({
                    'error': 'Missing required parameter: path'
                }, status=400)
            
            result = await handle_read_file({
                'file_path': file_path,
                'encoding': encoding
            }, self.config)
            
            return web.json_response({
                'success': True,
                'result': result
            })
        
        except Exception as e:
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)
    
    async def write_file(self, request: web.Request) -> web.Response:
        """POST /api/write
        Body: {"path": "...", "content": "...", "encoding": "utf-8", "is_base64": false}
        """
        try:
            data = await request.json()
            
            file_path = data.get('path')
            content = data.get('content')
            
            if not file_path or content is None:
                return web.json_response({
                    'error': 'Missing required parameters: path and content'
                }, status=400)
            
            encoding = data.get('encoding', 'utf-8')
            is_base64 = data.get('is_base64', False)  # ✅ EKLENDI!
            
            result = await handle_write_file({
                'file_path': file_path,
                'content': content,
                'encoding': encoding,
                'is_base64': is_base64  # ✅ EKLENDI!
            }, self.config)
            
            return web.json_response({
                'success': True,
                'result': result
            })
        
        except Exception as e:
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)
    
    async def append_file(self, request: web.Request) -> web.Response:
        """POST /api/append
        Body: {"path": "...", "content": "..."}
        """
        try:
            data = await request.json()
            
            file_path = data.get('path')
            content = data.get('content')
            
            if not file_path or content is None:
                return web.json_response({
                    'error': 'Missing required parameters: path and content'
                }, status=400)
            
            result = await handle_append_file({
                'file_path': file_path,
                'content': content
            }, self.config)
            
            return web.json_response({
                'success': True,
                'result': result
            })
        
        except Exception as e:
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)
    
    async def list_directory(self, request: web.Request) -> web.Response:
        """GET /api/list?path=<dir_path>&recursive=true&pattern=*.py
        POST /api/list with JSON body (for GPT compatibility)"""
        try:
            # Support both GET (query params) and POST (JSON body)
            if request.method == 'POST':
                data = await request.json()
                dir_path = data.get('path')
                recursive = data.get('recursive', False)
                show_hidden = data.get('show_hidden', False)
                pattern = data.get('pattern')
            else:  # GET
                dir_path = request.query.get('path')
                recursive = request.query.get('recursive', 'false').lower() == 'true'
                show_hidden = request.query.get('show_hidden', 'false').lower() == 'true'
                pattern = request.query.get('pattern')
            
            if not dir_path:
                return web.json_response({
                    'error': 'Missing required parameter: path'
                }, status=400)
            
            result = await handle_list_directory({
                'directory_path': dir_path,
                'recursive': recursive,
                'show_hidden': show_hidden,
                'pattern': pattern
            }, self.config)
            
            return web.json_response({
                'success': True,
                'result': result
            })
        
        except Exception as e:
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)
    
    async def directory_tree(self, request: web.Request) -> web.Response:
        """GET /api/tree?path=<dir_path>&max_depth=3
        POST /api/tree with JSON body (for GPT compatibility)"""
        try:
            # Support both GET (query params) and POST (JSON body)
            if request.method == 'POST':
                data = await request.json()
                dir_path = data.get('path')
                max_depth = data.get('max_depth', 3)
            else:  # GET
                dir_path = request.query.get('path')
                max_depth = int(request.query.get('max_depth', '3'))
            
            if not dir_path:
                return web.json_response({
                    'error': 'Missing required parameter: path'
                }, status=400)
            
            result = await handle_directory_tree({
                'directory_path': dir_path,
                'max_depth': max_depth
            }, self.config)
            
            return web.json_response({
                'success': True,
                'result': result
            })
        
        except Exception as e:
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)
    
    async def search_in_files(self, request: web.Request) -> web.Response:
        """GET /api/search?path=<dir>&text=<search_text>&pattern=*.py
        POST /api/search with JSON body (for GPT compatibility)"""
        try:
            # Support both GET (query params) and POST (JSON body)
            if request.method == 'POST':
                data = await request.json()
                dir_path = data.get('path')
                search_text = data.get('text')
                file_pattern = data.get('pattern', '*')
                case_sensitive = data.get('case_sensitive', False)
            else:  # GET
                dir_path = request.query.get('path')
                search_text = request.query.get('text')
                file_pattern = request.query.get('pattern', '*')
                case_sensitive = request.query.get('case_sensitive', 'false').lower() == 'true'
            
            if not dir_path or not search_text:
                return web.json_response({
                    'error': 'Missing required parameters: path and text'
                }, status=400)
            
            result = await handle_search_in_files({
                'directory_path': dir_path,
                'search_text': search_text,
                'file_pattern': file_pattern,
                'case_sensitive': case_sensitive
            }, self.config)
            
            return web.json_response({
                'success': True,
                'result': result
            })
        
        except Exception as e:
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)
    
    async def find_files(self, request: web.Request) -> web.Response:
        """GET /api/find?path=<dir>&pattern=*.txt
        POST /api/find with JSON body (for GPT compatibility)"""
        try:
            # Support both GET (query params) and POST (JSON body)
            if request.method == 'POST':
                data = await request.json()
                dir_path = data.get('path')
                pattern = data.get('pattern')
            else:  # GET
                dir_path = request.query.get('path')
                pattern = request.query.get('pattern')
            
            if not dir_path or not pattern:
                return web.json_response({
                    'error': 'Missing required parameters: path and pattern'
                }, status=400)
            
            result = await handle_find_files_by_pattern({
                'directory_path': dir_path,
                'pattern': pattern
            }, self.config)
            
            return web.json_response({
                'success': True,
                'result': result
            })
        
        except Exception as e:
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)
    
    async def copy_file(self, request: web.Request) -> web.Response:
        """POST /api/copy
        Body: {"source": "...", "destination": "...", "overwrite": false}
        """
        try:
            data = await request.json()
            
            source = data.get('source')
            destination = data.get('destination')
            
            if not source or not destination:
                return web.json_response({
                    'error': 'Missing required parameters: source and destination'
                }, status=400)
            
            overwrite = data.get('overwrite', False)
            
            result = await handle_copy_file({
                'source_path': source,
                'destination_path': destination,
                'overwrite': overwrite
            }, self.config)
            
            return web.json_response({
                'success': True,
                'result': result
            })
        
        except Exception as e:
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)
    
    async def delete_file(self, request: web.Request) -> web.Response:
        """DELETE /api/file?path=<file_path>
        POST /api/delete with JSON body (for GPT compatibility)"""
        try:
            # Support both DELETE (query params) and POST (JSON body)
            if request.method == 'POST':
                data = await request.json()
                file_path = data.get('path')
            else:  # DELETE
                file_path = request.query.get('path')
            
            if not file_path:
                return web.json_response({
                    'error': 'Missing required parameter: path'
                }, status=400)
            
            result = await handle_delete_file({
                'file_path': file_path
            }, self.config)
            
            return web.json_response({
                'success': True,
                'result': result
            })
        
        except Exception as e:
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)
    
    async def get_file_hash(self, request: web.Request) -> web.Response:
        """GET /api/hash?path=<file_path>&algorithm=sha256"""
        if not SPECIAL_OPS_AVAILABLE:
            return web.json_response({
                'error': 'Special operations not available'
            }, status=501)
        
        try:
            file_path = request.query.get('path')
            if not file_path:
                return web.json_response({
                    'error': 'Missing required parameter: path'
                }, status=400)
            
            algorithm = request.query.get('algorithm', 'sha256')
            
            result = await handle_get_file_hash({
                'file_path': file_path,
                'algorithm': algorithm
            }, self.config)
            
            return web.json_response({
                'success': True,
                'result': result
            })
        
        except Exception as e:
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)
    
    async def get_image(self, request: web.Request) -> web.Response:
        """GET /api/image?path=<file_path>
        POST /api/image with JSON body (for GPT compatibility)
        Returns image file directly for GPT Vision
        With automatic compression for large images
        """
        try:
            # Support both GET (query params) and POST (JSON body)
            if request.method == 'POST':
                data = await request.json()
                file_path = data.get('path')
            else:  # GET
                file_path = request.query.get('path')
            
            if not file_path:
                return web.json_response({
                    'error': 'Missing required parameter: path'
                }, status=400)
            
            # Resolve real path (symlinks, OneDrive reparse points)
            path = Path(file_path).resolve()
            
            # Security check
            if not path.exists():
                return web.json_response({
                    'error': f'File not found: {file_path}'
                }, status=404)
            
            if not path.is_file():
                return web.json_response({
                    'error': f'Not a file: {file_path}'
                }, status=400)
            
            # Check if it's an image by extension
            if path.suffix.lower() not in IMAGE_EXTENSIONS:
                return web.json_response({
                    'error': f'Not an image file: {file_path}',
                    'extension': path.suffix
                }, status=400)
            
            # Detect MIME type
            mime_type, _ = mimetypes.guess_type(str(path))
            if not mime_type:
                mime_type = 'image/jpeg'  # Default fallback
            
            # Check file size
            file_size = path.stat().st_size
            max_size = self.config.max_image_size_mb * 1024 * 1024
            
            # If file is too large and compression is enabled, compress it
            if file_size > max_size and self.config.enable_image_compression and PIL_AVAILABLE:
                try:
                    # Open and resize image
                    img = Image.open(path)
                    
                    # Preserve EXIF orientation
                    try:
                        from PIL import ImageOps
                        img = ImageOps.exif_transpose(img)
                    except:
                        pass
                    
                    # Calculate new size maintaining aspect ratio
                    max_dim = self.config.max_image_dimension
                    if img.width > max_dim or img.height > max_dim:
                        img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)
                    
                    # Save to bytes
                    output = io.BytesIO()
                    
                    # Determine format
                    img_format = img.format or 'JPEG'
                    if img_format == 'PNG' and img.mode == 'RGBA':
                        img.save(output, format='PNG', optimize=True)
                        mime_type = 'image/png'
                    else:
                        # Convert to RGB if needed
                        if img.mode not in ('RGB', 'L'):
                            img = img.convert('RGB')
                        img.save(output, format='JPEG', quality=85, optimize=True)
                        mime_type = 'image/jpeg'
                    
                    image_data = output.getvalue()
                    
                    return web.Response(
                        body=image_data,
                        content_type=mime_type,
                        headers={
                            'Cache-Control': 'public, max-age=3600',
                            'Access-Control-Allow-Origin': '*',
                            'X-Image-Compressed': 'true',
                            'X-Original-Size': str(file_size)
                        }
                    )
                except Exception as compress_error:
                    # If compression fails, try to return original if under hard limit
                    if file_size < 20 * 1024 * 1024:  # 20MB hard limit
                        pass  # Fall through to original
                    else:
                        return web.json_response({
                            'error': f'Image too large and compression failed: {str(compress_error)}',
                            'size_mb': round(file_size / (1024 * 1024), 2)
                        }, status=413)
            
            # Return original image
            with open(path, 'rb') as f:
                image_data = f.read()
            
            return web.Response(
                body=image_data,
                content_type=mime_type,
                headers={
                    'Cache-Control': 'public, max-age=3600',
                    'Access-Control-Allow-Origin': '*',
                    'Content-Length': str(len(image_data))
                }
            )
        
        except Exception as e:
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)
    
    async def get_image_base64(self, request: web.Request) -> web.Response:
        """GET /api/image/base64?path=<file_path>
        POST /api/image/base64 with JSON body (for GPT compatibility)
        Returns image as base64 JSON for GPT Vision
        """
        try:
            # Support both GET (query params) and POST (JSON body)
            if request.method == 'POST':
                data = await request.json()
                file_path = data.get('path')
            else:  # GET
                file_path = request.query.get('path')
            
            if not file_path:
                return web.json_response({
                    'error': 'Missing required parameter: path'
                }, status=400)
            
            path = Path(file_path)
            
            if not path.exists():
                return web.json_response({
                    'error': f'File not found: {file_path}'
                }, status=404)
            
            if not path.is_file():
                return web.json_response({
                    'error': f'Not a file: {file_path}'
                }, status=400)
            
            # Detect MIME type
            mime_type, _ = mimetypes.guess_type(str(path))
            if not mime_type or not mime_type.startswith('image/'):
                return web.json_response({
                    'error': f'Not an image file: {file_path}',
                    'detected_type': mime_type
                }, status=400)
            
            # Read and encode
            with open(path, 'rb') as f:
                image_data = f.read()
            
            base64_data = base64.b64encode(image_data).decode('utf-8')
            
            return web.json_response({
                'success': True,
                'file_path': str(path),
                'file_name': path.name,
                'mime_type': mime_type,
                'size_bytes': len(image_data),
                'base64': base64_data,
                'data_url': f'data:{mime_type};base64,{base64_data}'
            })
        
        except Exception as e:
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)
    
    async def list_images(self, request: web.Request) -> web.Response:
        """GET /api/images?path=<dir_path>
        POST /api/images with JSON body (for GPT compatibility)
        Lists all image files in a directory
        """
        try:
            # Support both GET (query params) and POST (JSON body)
            if request.method == 'POST':
                data = await request.json()
                dir_path = data.get('path')
            else:  # GET
                dir_path = request.query.get('path')
            
            if not dir_path:
                return web.json_response({
                    'error': 'Missing required parameter: path'
                }, status=400)
            
            path = Path(dir_path)
            
            if not path.exists():
                return web.json_response({
                    'error': f'Directory not found: {dir_path}'
                }, status=404)
            
            if not path.is_dir():
                return web.json_response({
                    'error': f'Not a directory: {dir_path}'
                }, status=400)
            
            # Find image files
            image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg', '.ico'}
            images = []
            
            for item in path.iterdir():
                if item.is_file() and item.suffix.lower() in image_extensions:
                    images.append({
                        'path': str(item),
                        'name': item.name,
                        'extension': item.suffix,
                        'size_bytes': item.stat().st_size,
                        'url': f'{request.url.origin()}/api/image?path={item}'
                    })
            
            return web.json_response({
                'success': True,
                'directory': str(path),
                'image_count': len(images),
                'images': images
            })
        
        except Exception as e:
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)
    
    async def api_help(self, request: web.Request) -> web.Response:
        """GET /api - API documentation"""
        endpoints = {
            'GET /api': 'This help message',
            'GET /api/read': 'Read file - ?path=<file_path>&encoding=utf-8',
            'POST /api/write': 'Write file - Body: {path, content, encoding}',
            'POST /api/append': 'Append to file - Body: {path, content}',
            'GET /api/list': 'List directory - ?path=<dir>&recursive=true&pattern=*.py',
            'GET /api/tree': 'Directory tree - ?path=<dir>&max_depth=3',
            'GET /api/search': 'Search in files - ?path=<dir>&text=<query>&pattern=*.py',
            'GET /api/find': 'Find files - ?path=<dir>&pattern=*.txt',
            'POST /api/copy': 'Copy file - Body: {source, destination, overwrite}',
            'DELETE /api/file': 'Delete file - ?path=<file_path>',
            'GET /api/hash': 'Get file hash - ?path=<file>&algorithm=sha256',
            'GET /api/image': 'Get image (for GPT Vision) - ?path=<image_path>',
            'GET /api/image/base64': 'Get image as base64 - ?path=<image_path>',
            'GET /api/images': 'List images in directory - ?path=<dir_path>'
        }
        
        return web.json_response({
            'name': 'MCP File Manager REST API',
            'version': '1.0.0',
            'description': 'Simple REST API wrapper for GPT and web clients',
            'base_url': str(request.url.origin()) + '/api',
            'endpoints': endpoints,
            'example': {
                'read_file': f"{request.url.origin()}/api/read?path=C:/test.txt",
                'list_dir': f"{request.url.origin()}/api/list?path=C:/Windows",
                'search': f"{request.url.origin()}/api/search?path=C:/Projects&text=TODO",
                'get_image': f"{request.url.origin()}/api/image?path=C:/Pictures/photo.jpg",
                'list_images': f"{request.url.origin()}/api/images?path=C:/Pictures"
            }
        })


def setup_rest_routes(app: web.Application, config: ServerConfig):
    """Setup REST API routes"""
    api = RestAPI(config)
    
    # API routes - Both GET and POST for GPT compatibility
    app.router.add_get('/api', api.api_help)
    
    # File operations
    app.router.add_get('/api/read', api.read_file)
    app.router.add_post('/api/read', api.read_file)  # ✅ GPT compatibility
    app.router.add_post('/api/write', api.write_file)
    app.router.add_post('/api/append', api.append_file)
    app.router.add_delete('/api/file', api.delete_file)
    app.router.add_post('/api/delete', api.delete_file)  # ✅ GPT compatibility
    
    # Directory operations
    app.router.add_get('/api/list', api.list_directory)
    app.router.add_post('/api/list', api.list_directory)  # ✅ GPT compatibility
    app.router.add_get('/api/tree', api.directory_tree)
    app.router.add_post('/api/tree', api.directory_tree)  # ✅ GPT compatibility
    
    # Search operations
    app.router.add_get('/api/search', api.search_in_files)
    app.router.add_post('/api/search', api.search_in_files)  # ✅ GPT compatibility
    app.router.add_get('/api/find', api.find_files)
    app.router.add_post('/api/find', api.find_files)  # ✅ GPT compatibility
    
    # File management
    app.router.add_post('/api/copy', api.copy_file)
    
    # Image endpoints (GPT Vision support)
    app.router.add_get('/api/image', api.get_image)
    app.router.add_post('/api/image', api.get_image)  # ✅ GPT compatibility
    app.router.add_get('/api/image/base64', api.get_image_base64)
    app.router.add_post('/api/image/base64', api.get_image_base64)  # ✅ GPT compatibility
    app.router.add_get('/api/images', api.list_images)
    app.router.add_post('/api/images', api.list_images)  # ✅ GPT compatibility
    
    if SPECIAL_OPS_AVAILABLE:
        app.router.add_get('/api/hash', api.get_file_hash)

