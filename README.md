# MCP File Manager
A Model Context Protocol (MCP) server that provides file system access for AI models. Supports both native MCP protocol and REST API.
![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)  
![License](https://img.shields.io/badge/license-MIT-green.svg)  
![MCP](https://img.shields.io/badge/MCP-Compatible-purple.svg)

## Overview
MCP File Manager enables AI models like ChatGPT and Claude to interact directly with your file system. Instead of manually copying file contents or uploading documents, AI assistants can read, write, search, and manage files programmatically.
**Key capabilities:**
- Read and write files (text and binary)
- Search and find files by pattern or content
- Process images with automatic compression
- Copy, move, and organize files
- Calculate hashes and create archives
- List directory contents and tree structures  
**Dual protocol support:**
- **Native MCP**: Direct integration with Claude Desktop and other MCP clients  
- **REST API**: HTTP endpoints for ChatGPT Custom Actions and web clients

## Features
### File Operations
- Read, write, append, and delete files  
- Support for text and binary files  
- Base64 encoding for images and binary data  
- Multiple encoding support (UTF-8, UTF-16, Latin-1, etc.)
### Directory Operations
- List directory contents with recursive support  
- Create and delete directories  
- Display directory tree structure  
- Pattern matching (wildcards)
### Search & Discovery
- Search text within files  
- Find files by pattern  
- Content-based file discovery  
- Case-sensitive/insensitive search
### Image Support
- Read images for Vision AI models  
- Automatic image compression for large files  
- Base64 encoding for AI processing  
- List images in directories  
- Support for JPG, PNG, GIF, BMP, WebP
### Advanced Features
- File copying and moving  
- File hash calculation (MD5, SHA256, SHA512)  
- File compression (ZIP)  
- Batch operations  
- OneDrive and symlink resolution
### Security
- System-critical file protection  
- Dangerous file warnings  
- Path traversal prevention  
- Configurable file size limits  
- Comprehensive operation logging

## Quick Start
### Requirements
- Python 3.10 or higher  
- pip package manager
### Setup
```bash
git clone <repository-url>
cd mcp-file-manager
pip install -r requirements.txt
pip install -e .
```

## Usage
### For Claude Desktop (Native MCP)
Edit your Claude Desktop configuration file:
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`  
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
- **Linux**: `~/.config/Claude/claude_desktop_config.json`
Add this configuration:
```json
{
  "mcpServers": {
    "file-manager": {
      "command": "python",
      "args": ["-m", "file_manager_server.server"],
      "env": {
        "LOG_LEVEL": "INFO",
        "MAX_FILE_SIZE_MB": "100"
      }
    }
  }
}
```
Restart Claude Desktop after editing.

### For ChatGPT and Web Clients (REST API)
Run the server:
```bash
python mcp_sse_server.py
```
Server runs at **http://localhost:8080**  
Expose to the internet using a tunnel:
#### Option A — Cloudflare Tunnel
```bash
cloudflared tunnel --url http://localhost:8080
```
#### Option B — ngrok
```bash
ngrok http 8080
```
Then, in ChatGPT → Settings → Actions → Add new action  
Paste the content of `gpt_actions.json` and replace the URL with your tunnel.

## Example Use Cases
### Code Analysis
> Read all Python files in the `src` directory and find any TODO comments.
### Automated Documentation
> Create a `CHANGELOG.md` file by analyzing git commits and code changes.
### Image Processing
> Find all images larger than 2MB in my Pictures folder and create thumbnails.
### Batch File Operations
> Rename all `.jpeg` files to `.jpg` in the Downloads folder.
### Project Setup
> Create a new Python project structure with `src/`, `tests/`, and `docs/` folders.

## API Reference
**Base URL:** `http://localhost:8080/api`
### File Operations
```json
POST /api/read
{"path": "/path/to/file.txt"}

POST /api/write
{"path": "/path/to/file.txt", "content": "file content", "is_base64": false}

POST /api/delete
{"path": "/path/to/file.txt"}
```
### Directory Operations
```json
POST /api/list
{"path": "/path/to/directory", "recursive": false, "pattern": "*.py"}

POST /api/tree
{"path": "/path/to/directory", "max_depth": 3}
```
### Search
```json
POST /api/search
{"path": "/path/to/directory", "text": "search term", "pattern": "*.txt"}

POST /api/find
{"path": "/path/to/directory", "pattern": "*.jpg"}
```
### Images
```json
POST /api/image
{"path": "/path/to/image.jpg"}

POST /api/image/base64
{"path": "/path/to/image.jpg"}

POST /api/images
{"path": "/path/to/directory"}
```
### Advanced
```json
POST /api/copy
{"source": "/source/file.txt", "destination": "/dest/file.txt", "overwrite": false}
```

## Configuration
| Variable | Default | Description |
|-----------|----------|-------------|
| `LOG_LEVEL` | INFO | Logging level |
| `MAX_FILE_SIZE_MB` | 100 | Max file size |
| `MAX_IMAGE_SIZE_MB` | 15 | Max image size |
| `ENABLE_COMPRESSION` | true | Enable ZIP compression |
| `ENABLE_HASHING` | true | Enable hash calculations |
| `ENABLE_DANGEROUS_OPERATIONS` | false | Allow deletion of executables |

## Project Structure
```
mcp-file-manager/
├── src/
│   └── file_manager_server/
│       ├── server.py
│       ├── rest_api.py
│       ├── config.py
│       ├── handlers/
│       └── utils/
├── mcp_sse_server.py
├── gpt_actions.json
├── requirements.txt
└── tests/
```

## Testing
```bash
pytest
pytest --cov=file_manager_server --cov-report=html
```

## Security
This server provides file system access with multiple safety layers.  
**Protection Mechanisms**
- Blocks operations on system-critical paths  
- Prevents path traversal and dangerous deletions  
- Configurable file size limits  
- Comprehensive operation logging  
**Recommended Practices**
- Start with non-critical directories  
- Monitor logs regularly  
- Avoid exposing public tunnels without authentication

## License
MIT License — see [LICENSE](LICENSE)

## Acknowledgments
- Anthropic — for the Model Context Protocol (MCP)  
- OpenAI — for ChatGPT Custom Actions support  
- The open-source community ❤️
