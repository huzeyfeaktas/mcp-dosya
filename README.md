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
# Clone the repository
git clone <repository-url>
cd mcp-file-manager

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

## Usage

### For Claude Desktop (Native MCP)

1. Edit your Claude Desktop configuration file:
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`

2. Add the MCP server configuration:

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

3. Restart Claude Desktop

### For ChatGPT and Web Clients (REST API)

1. Start the SSE server:

```bash
python mcp_sse_server.py
```

The server will start on `http://localhost:8080`

2. Expose to the internet using **Cloudflare Tunnel** or **ngrok**:

**Option A: Cloudflare Tunnel** (Free)
```bash
# Download cloudflared from https://github.com/cloudflare/cloudflared/releases
cloudflared tunnel --url http://localhost:8080
```

**Option B: ngrok** (Free with account)
```bash
# Download from https://ngrok.com/download
ngrok http 8080
```

3. Configure ChatGPT Custom Actions:
   - Open `gpt_actions.json`
   - Replace `"url": "https://your-tunnel-url.trycloudflare.com"` with your tunnel URL
   - Copy the entire JSON content
   - In ChatGPT: Settings → Actions → Add new action → Paste JSON

## Usage Examples

### Example 1: Code Analysis
```
You: "Read all Python files in the 'src' directory and find any TODO comments"

AI: *Uses MCP to scan files, reads each .py file, extracts TODOs*
"Found 5 TODO items:
1. src/server.py:45 - TODO: Add error handling
2. src/handlers/file.py:120 - TODO: Optimize large file reads
..."
```

### Example 2: Automated Documentation
```
You: "Create a CHANGELOG.md file by analyzing git commits and code changes"

AI: *Reads project files, analyzes structure, writes CHANGELOG.md*
"Created CHANGELOG.md with version history based on your project structure"
```

### Example 3: Image Processing
```
You: "Find all images larger than 2MB in my Pictures folder and create thumbnails"

AI: *Lists images, processes each one, saves compressed versions*
"Processed 12 images. Created thumbnails in Pictures/thumbnails/"
```

### Example 4: Batch File Operations
```
You: "Rename all .jpeg files to .jpg in the Downloads folder"

AI: *Finds .jpeg files, renames each one*
"Renamed 23 files from .jpeg to .jpg"
```

### Example 5: Project Setup
```
You: "Create a new Python project structure with src/, tests/, and docs/ folders"

AI: *Creates directories, generates __init__.py files, adds README*
"Created project structure with 8 files and 5 directories"
```

### Example 6: Data Extraction
```
You: "Search all .csv files in the data/ folder for entries where price > 100"

AI: *Reads CSV files, filters data, creates summary*
"Found 47 entries. Created summary in data/high_price_items.txt"
```

## Supported Platforms

| Platform | Support | Method |
|----------|---------|--------|
| **Claude Desktop** | Native | MCP Protocol (stdio) |
| **ChatGPT** | Full | Custom Actions (REST API) |
| **Claude API** | Native | MCP Protocol (SSE) |
| **LM Studio** | Via wrapper | Function calling |
| **Ollama** | Via wrapper | Function calling |
| **Any MCP Client** | Native | MCP Protocol |

## API Reference

### Native MCP Tools

| Tool | Description |
|------|-------------|
| `read_file` | Read file contents |
| `write_file` | Create or overwrite file |
| `append_file` | Append to file |
| `delete_file` | Delete file |
| `list_directory` | List directory contents |
| `create_directory` | Create new directory |
| `directory_tree` | Display tree structure |
| `search_in_files` | Search text in files |
| `find_files` | Find files by pattern |
| `copy_file` | Copy file |
| `move_file` | Move file |
| `get_file_hash` | Calculate file hash |
| `get_image` | Read image for Vision AI |
| `list_images` | List images in directory |

### REST API Endpoints

All endpoints accept POST requests with JSON body.

**Base URL**: `http://localhost:8080/api`

#### File Operations

- `POST /api/read` - Read file
  ```json
  {"path": "/path/to/file.txt"}
  ```

- `POST /api/write` - Write file
  ```json
  {
    "path": "/path/to/file.txt",
    "content": "file content",
    "is_base64": false
  }
  ```

- `POST /api/delete` - Delete file
  ```json
  {"path": "/path/to/file.txt"}
  ```

#### Directory Operations

- `POST /api/list` - List directory
  ```json
  {
    "path": "/path/to/directory",
    "recursive": false,
    "pattern": "*.py"
  }
  ```

- `POST /api/tree` - Directory tree
  ```json
  {
    "path": "/path/to/directory",
    "max_depth": 3
  }
  ```

#### Search

- `POST /api/search` - Search in files
  ```json
  {
    "path": "/path/to/directory",
    "text": "search term",
    "pattern": "*.txt"
  }
  ```

- `POST /api/find` - Find files
  ```json
  {
    "path": "/path/to/directory",
    "pattern": "*.jpg"
  }
  ```

#### Images

- `POST /api/image` - Get image (binary)
  ```json
  {"path": "/path/to/image.jpg"}
  ```

- `POST /api/image/base64` - Get image as base64
  ```json
  {"path": "/path/to/image.jpg"}
  ```

- `POST /api/images` - List images
  ```json
  {"path": "/path/to/directory"}
  ```

#### Advanced

- `POST /api/copy` - Copy file
  ```json
  {
    "source": "/source/file.txt",
    "destination": "/dest/file.txt",
    "overwrite": false
  }
  ```

## Configuration

Environment variables for customization:

```bash
# Logging
LOG_LEVEL=INFO              # DEBUG, INFO, WARNING, ERROR
LOG_FILE=/path/to/log.txt   # Optional log file

# Limits
MAX_FILE_SIZE_MB=100        # Maximum file size
MAX_BATCH_FILES=50          # Max files in batch operations
MAX_SEARCH_RESULTS=1000     # Max search results

# Image settings
MAX_IMAGE_SIZE_MB=15        # Max image size for Vision AI
ENABLE_IMAGE_COMPRESSION=true  # Auto-compress large images
MAX_IMAGE_DIMENSION=1920    # Max width/height for auto-resize

# Security
ENABLE_DANGEROUS_OPERATIONS=false  # Allow deletion of executables

# Features
ENABLE_COMPRESSION=true     # Enable ZIP compression
ENABLE_HASHING=true        # Enable hash calculations
```

## Security

This server provides file system access with multiple security layers:

### Protection Mechanisms

**System File Protection**
- Blocks operations on critical system paths (`/etc`, `C:\Windows\System32`, `/bin`, `/usr/bin`)
- Prevents accidental damage to operating system files
- Configurable protection lists

**Dangerous Operations**
- Executable deletion requires explicit permission (`ENABLE_DANGEROUS_OPERATIONS=true`)
- Warnings for operations on `.exe`, `.dll`, `.sys` files
- Safeguards against unintended deletions

**Path Validation**
- Path traversal prevention (blocks `../../../` patterns)
- All file paths validated before operations
- Rejects suspicious path patterns

**Size Limits**
- Configurable max file size (default: 100MB)
- Prevents memory exhaustion
- Separate limits for images (default: 15MB)

**Operation Logging**
- All operations logged with timestamps
- Audit trail for file system changes
- Error logging for debugging

**Network Security**
- When using tunnels (Cloudflare/ngrok), your file system becomes internet-accessible
- Recommended only for trusted services (ChatGPT, Claude)
- Consider authentication for production environments
- Regular log monitoring advised

### Best Practices

**Recommended:**
- Start with non-critical directories
- Monitor operation logs regularly
- Keep file size limits reasonable
- Test on development machines first
- Review security warnings before proceeding

**Not Recommended:**
- Enabling dangerous operations without understanding implications
- Exposing to public internet without authentication
- Ignoring security warnings
- Production use without thorough testing

## Project Structure

```
mcp-file-manager/
├── src/
│   └── file_manager_server/
│       ├── server.py           # Native MCP server
│       ├── rest_api.py         # REST API wrapper
│       ├── config.py           # Configuration
│       ├── handlers/           # Operation handlers
│       │   ├── file_operations.py
│       │   ├── directory_operations.py
│       │   ├── search_operations.py
│       │   ├── image_operations.py
│       │   └── ...
│       └── utils/              # Utilities
│           ├── security.py
│           ├── validators.py
│           └── file_helpers.py
├── mcp_sse_server.py          # SSE transport server
├── gpt_actions.json           # ChatGPT Actions configuration
├── requirements.txt           # Python dependencies
├── pyproject.toml            # Project metadata
└── tests/                    # Test suite
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=file_manager_server --cov-report=html

# Run specific test file
pytest tests/test_file_operations.py
```

## Use Cases

### Developers
- Code quality analysis and bug detection
- Documentation generation from code structure
- Batch file refactoring and restructuring
- Log file analysis and error tracking

### Content Creators
- Batch image compression and optimization
- Automated file organization by type or date
- Archive creation and file integrity verification

### Data Scientists
- Dataset preparation and transformation
- Automated report generation from data
- Duplicate detection and cleanup

### System Administrators
- Configuration file management
- Log monitoring and pattern matching
- Mass file operations across directories

## Limitations

- **Large Files**: Files over 100MB may timeout (configurable)
- **Binary Files**: Limited support for complex binary formats
- **Concurrent Operations**: Single-threaded, no parallel file operations
- **Network Latency**: REST API depends on tunnel stability (Cloudflare/ngrok)

## Roadmap

- [ ] Authentication and user permissions
- [ ] File watching and real-time updates
- [ ] Parallel/batch operation optimization
- [ ] Support for more binary file formats
- [ ] Web-based management UI
- [ ] Docker containerization
- [ ] Plugin system for custom operations

## FAQ

### Q: Is this safe to use?
**A:** Yes, with proper precautions. The server includes multiple security layers including system file protection, path validation, and size limits. Since you're granting AI access to your file system:
- Use only with trusted AI platforms (ChatGPT, Claude)
- Start with non-critical directories
- Review logs regularly
- Don't expose to public internet without authentication

### Q: Does it work offline?
**A:** Depends on the client:
- **Claude Desktop**: Yes, works completely offline (native MCP)
- **ChatGPT**: No, requires internet (REST API via tunnel)

### Q: Can I use it with my own AI models?
**A:** Yes, if your model supports:
- **MCP Protocol**: Use native server (stdio/SSE transport)
- **HTTP/REST**: Use REST API endpoints
- **Function Calling**: Wrap endpoints with function definitions

### Q: What platforms are supported?
**A:** Fully cross-platform. Tested on:
- Windows 10/11
- macOS (Intel & Apple Silicon)
- Linux (Ubuntu, Debian, Fedora)

### Q: Why does ChatGPT need a tunnel?
**A:** ChatGPT Custom Actions require publicly accessible HTTPS endpoints. Tunnels (Cloudflare/ngrok) expose your local server to the internet temporarily.

### Q: Can multiple AI instances use it simultaneously?
**A:** Yes, the server handles concurrent connections. However:
- File operations are sequential (not parallelized)
- Heavy concurrent use may cause slowdowns

### Q: How do I handle large files?
**A:** 
- Increase `MAX_FILE_SIZE_MB` in config
- Use streaming for very large files
- Consider chunking operations
- Images auto-compress if over limit

### Q: Can AI delete my system files?
**A:** No. System-critical paths are hardcoded and blocked. Even if AI tries, operations will fail with security warnings.

## Contributing

Contributions are welcome! Here's how you can help:

1. **Report Bugs**: Open an issue with reproduction steps
2. **Suggest Features**: Describe your use case and proposed solution
3. **Submit PRs**: Fork, create feature branch, submit PR
4. **Improve Docs**: Fix typos, add examples, clarify instructions
5. **Share Use Cases**: Tell us how you're using MCP File Manager

### Development Setup

```bash
# Clone and setup
git clone <your-fork>
cd mcp-file-manager

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linters
flake8 src/
black src/
```

## License

MIT License - see [LICENSE](LICENSE) file for details

## Acknowledgments

- Anthropic for creating the Model Context Protocol (MCP)
- OpenAI for ChatGPT Custom Actions support
- The open-source community

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/mcp-file-manager/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/mcp-file-manager/discussions)
- **Security**: Report security issues via GitHub Security Advisories
#   m c p - d o s y a  
 