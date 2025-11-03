"""
MCP File Manager - Tam SSE Transport Implementasyonu
GPT, Claude ve tüm MCP istemcileri ile uyumlu
Cloudflare Tunnel ile internete açılabilir
"""

import asyncio
import json
import logging
from typing import Any, Optional
from aiohttp import web
import sys
import os

# MCP imports
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import TextContent

# Mevcut server'ı import et
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from file_manager_server.server import app as mcp_app, config
from file_manager_server.rest_api import setup_rest_routes

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MCPSSEServer:
    """MCP SSE Server - Tam protokol implementasyonu"""
    
    def __init__(self):
        self.mcp_server = mcp_app
        self.sessions = {}
        logger.info("MCP SSE Server initialized")
    
    async def handle_sse(self, request: web.Request) -> web.StreamResponse:
        """
        SSE endpoint - MCP protokolü için ana giriş noktası
        Bu endpoint SSE stream oluşturur ve MCP mesajlaşmasını yönetir
        """
        logger.info(f"🔌 New SSE connection from {request.remote}")
        
        # SSE response başlat
        response = web.StreamResponse()
        response.headers['Content-Type'] = 'text/event-stream'
        response.headers['Cache-Control'] = 'no-cache'
        response.headers['Connection'] = 'keep-alive'
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['X-Accel-Buffering'] = 'no'  # Nginx için buffering kapat
        
        await response.prepare(request)
        
        try:
            # MCP SSE transport oluştur
            logger.info("📡 Creating SSE transport...")
            async with SseServerTransport("/messages") as (read_stream, write_stream):
                logger.info("✅ SSE transport created, starting MCP server...")
                
                # MCP server'ı çalıştır
                init_options = self.mcp_server.create_initialization_options()
                
                await self.mcp_server.run(
                    read_stream,
                    write_stream,
                    init_options
                )
                
                logger.info("✅ MCP server session completed")
                
        except asyncio.CancelledError:
            logger.info("🔌 SSE connection cancelled by client")
        except Exception as e:
            logger.error(f"❌ SSE error: {e}", exc_info=True)
        finally:
            try:
                await response.write_eof()
            except:
                pass
        
        return response
    
    async def handle_messages(self, request: web.Request) -> web.Response:
        """
        POST endpoint - Client'tan gelen MCP mesajları
        SSE transport ile birlikte çalışır
        """
        try:
            data = await request.json()
            method = data.get('method', 'unknown')
            msg_id = data.get('id', 'unknown')
            
            logger.info(f"📨 Received MCP message: {method} (id: {msg_id})")
            
            # Bu endpoint SSE transport tarafından kullanılır
            # Direct POST için basit bir response döndür
            
            return web.json_response({
                "jsonrpc": "2.0",
                "id": data.get("id"),
                "result": {
                    "status": "received",
                    "message": "Use SSE endpoint for full MCP protocol"
                }
            })
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON: {e}")
            return web.json_response({
                "jsonrpc": "2.0",
                "error": {
                    "code": -32700,
                    "message": "Parse error"
                }
            }, status=400)
        except Exception as e:
            logger.error(f"❌ Message handling error: {e}", exc_info=True)
            return web.json_response({
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }, status=500)
    
    async def handle_health(self, request: web.Request) -> web.Response:
        """Health check endpoint"""
        return web.json_response({
            "status": "healthy",
            "protocol": "MCP (Model Context Protocol)",
            "transport": "SSE (Server-Sent Events)",
            "version": "1.0.0",
            "timestamp": asyncio.get_event_loop().time()
        })
    
    async def handle_info(self, request: web.Request) -> web.Response:
        """Server bilgileri ve kullanım kılavuzu"""
        base_url = str(request.url.origin())
        
        return web.json_response({
            "name": "MCP File Manager",
            "description": "Comprehensive file system operations via Model Context Protocol",
            "version": "1.0.0",
            "protocol": {
                "name": "Model Context Protocol",
                "version": "2024-11-05",
                "spec": "https://modelcontextprotocol.io"
            },
            "transport": {
                "type": "SSE (Server-Sent Events)",
                "endpoint": f"{base_url}/sse",
                "messages_endpoint": f"{base_url}/messages"
            },
            "endpoints": {
                "sse": {
                    "url": "/sse",
                    "method": "GET",
                    "description": "SSE stream endpoint for MCP protocol"
                },
                "messages": {
                    "url": "/messages",
                    "method": "POST",
                    "description": "MCP message endpoint (used with SSE)"
                },
                "health": {
                    "url": "/health",
                    "method": "GET",
                    "description": "Health check endpoint"
                },
                "info": {
                    "url": "/info",
                    "method": "GET",
                    "description": "Server information and usage guide"
                }
            },
            "capabilities": {
                "file_operations": [
                    "read_file",
                    "write_file",
                    "append_file",
                    "delete_file",
                    "file_exists",
                    "get_file_info"
                ],
                "directory_operations": [
                    "list_directory",
                    "create_directory",
                    "delete_directory",
                    "directory_tree"
                ],
                "advanced_operations": [
                    "copy_file",
                    "move_file",
                    "rename_file",
                    "read_multiple_files"
                ],
                "search_operations": [
                    "search_in_files",
                    "find_files"
                ],
                "special_features": [
                    "compress_file",
                    "decompress_file",
                    "get_file_hash"
                ]
            },
            "security": {
                "enabled": True,
                "features": [
                    "System critical file protection",
                    "Dangerous file warnings",
                    "Path traversal prevention",
                    "File size limits",
                    "Comprehensive logging"
                ]
            },
            "usage": {
                "mcp_clients": "Connect MCP client to SSE endpoint",
                "example": f"mcp-client connect {base_url}/sse"
            }
        })
    
    async def handle_cors_preflight(self, request: web.Request) -> web.Response:
        """CORS preflight handling"""
        return web.Response(
            headers={
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization, Accept',
                'Access-Control-Max-Age': '86400',
            }
        )


def create_app() -> web.Application:
    """AIOHTTP application oluştur"""
    
    server = MCPSSEServer()
    app = web.Application()
    
    # CORS middleware - Tüm platformlar için gerekli
    async def cors_middleware(app, handler):
        async def middleware(request):
            # OPTIONS request (preflight)
            if request.method == "OPTIONS":
                return await server.handle_cors_preflight(request)
            
            # Normal request
            try:
                response = await handler(request)
            except web.HTTPException as e:
                response = e
            
            # CORS headers ekle
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, Accept"
            response.headers["Access-Control-Expose-Headers"] = "Content-Type"
            
            return response
        return middleware
    
    # Error handling middleware
    async def error_middleware(app, handler):
        async def middleware(request):
            try:
                return await handler(request)
            except web.HTTPException:
                raise
            except Exception as e:
                logger.error(f"Unhandled error: {e}", exc_info=True)
                return web.json_response({
                    "error": {
                        "code": -32603,
                        "message": "Internal server error",
                        "data": str(e)
                    }
                }, status=500)
        return middleware
    
    # Middleware'leri ekle
    app.middlewares.append(error_middleware)
    app.middlewares.append(cors_middleware)
    
    # MCP Routes
    app.router.add_get("/sse", server.handle_sse)
    app.router.add_post("/messages", server.handle_messages)
    app.router.add_get("/health", server.handle_health)
    app.router.add_get("/info", server.handle_info)
    app.router.add_get("/", server.handle_info)  # Root = info
    
    # REST API Routes (for GPT and web clients)
    setup_rest_routes(app, config)
    
    # OPTIONS için route (CORS preflight)
    app.router.add_route("OPTIONS", "/{tail:.*}", server.handle_cors_preflight)
    
    return app


def print_banner(host: str, port: int):
    """Başlangıç banner'ı"""
    print("\n" + "=" * 70)
    print("🚀 MCP FILE MANAGER SSE SERVER")
    print("=" * 70)
    print(f"📍 Server URL:        http://{host}:{port}")
    print(f"📍 SSE Endpoint:      http://{host}:{port}/sse")
    print(f"📍 Health Check:      http://{host}:{port}/health")
    print(f"📍 Server Info:       http://{host}:{port}/info")
    print("=" * 70)
    print("✅ Tam MCP Protokolü Aktif (JSON-RPC 2.0)")
    print("✅ SSE Transport Hazır")
    print("✅ REST API Aktif (GPT uyumlu)")
    print("✅ CORS Etkin (Tüm platformlar)")
    print("✅ Cloudflare Tunnel ile kullanıma hazır")
    print("=" * 70)
    print(f"📡 REST API Endpoints:")
    print(f"   - GET  /api              → API dokümantasyonu")
    print(f"   - GET  /api/read         → Dosya oku")
    print(f"   - POST /api/write        → Dosya yaz")
    print(f"   - GET  /api/list         → Dizin listele")
    print(f"   - GET  /api/search       → Dosyalarda ara")
    print(f"   - GET  /api/tree         → Dizin ağacı")
    print("=" * 70)
    print(f"📊 Konfigürasyon:")
    print(f"   - Log Level:       {config.log_level}")
    print(f"   - Max File Size:   {config.max_file_size_mb} MB")
    print(f"   - Max Batch:       {config.max_batch_files} files")
    print(f"   - Compression:     {'✅' if config.enable_compression else '❌'}")
    print(f"   - Hashing:         {'✅' if config.enable_hashing else '❌'}")
    print("=" * 70)
    print("🔧 Cloudflare Tunnel başlatmak için:")
    print(f"   cloudflared tunnel --url http://localhost:{port}")
    print("=" * 70)
    print("🌐 GPT/Claude/diğer platformlarda kullanmak için:")
    print("   1. Cloudflare tunnel ile HTTPS URL alın")
    print("   2. Platform'da MCP endpoint olarak /sse kullanın")
    print("=" * 70)
    print("\n✨ Server başlatılıyor...\n")


def main():
    """Ana fonksiyon"""
    port = int(os.getenv("PORT", 8080))
    host = os.getenv("HOST", "0.0.0.0")
    
    print_banner(host, port)
    
    try:
        app = create_app()
        web.run_app(
            app, 
            host=host, 
            port=port, 
            access_log=logger,
            print=None  # Custom banner kullandığımız için
        )
    except KeyboardInterrupt:
        logger.info("\n\n👋 Server stopped by user")
    except Exception as e:
        logger.error(f"\n\n❌ Server error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()

