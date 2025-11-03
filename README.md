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
```json
{
  "openapi": "3.1.0",
  "info": {
    "title": "MCP File Manager",
    "description": "Complete file system operations with image support",
    "version": "2.0.0"
  },
  "servers": [
    {
      "url": "https://attachment-gene-missed-yen.trycloudflare.com"
    }
  ],
  "paths": {
    "/api/read": {
      "post": {
        "operationId": "readFile",
        "summary": "Read file content",
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "properties": {
                  "path": {
                    "type": "string",
                    "description": "Full file path"
                  },
                  "encoding": {
                    "type": "string",
                    "default": "utf-8"
                  }
                },
                "required": ["path"]
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "Success"
          }
        }
      }
    },
    "/api/list": {
      "post": {
        "operationId": "listDirectory",
        "summary": "List directory contents",
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "properties": {
                  "path": {
                    "type": "string",
                    "description": "Directory path"
                  },
                  "recursive": {
                    "type": "boolean",
                    "default": false
                  },
                  "pattern": {
                    "type": "string",
                    "description": "File pattern (e.g. *.py)"
                  }
                },
                "required": ["path"]
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "Success"
          }
        }
      }
    },
    "/api/write": {
      "post": {
        "operationId": "writeFile",
        "summary": "Write or create file",
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "properties": {
                  "path": {
                    "type": "string",
                    "description": "File path"
                  },
                  "content": {
                    "type": "string",
                    "description": "File content (text or base64)"
                  },
                  "encoding": {
                    "type": "string",
                    "default": "utf-8"
                  },
                  "is_base64": {
                    "type": "boolean",
                    "default": false,
                    "description": "Set true for binary files (images)"
                  }
                },
                "required": ["path", "content"]
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "Success"
          }
        }
      }
    },
    "/api/search": {
      "post": {
        "operationId": "searchInFiles",
        "summary": "Search text in files",
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "properties": {
                  "path": {
                    "type": "string",
                    "description": "Directory to search"
                  },
                  "text": {
                    "type": "string",
                    "description": "Text to search for"
                  },
                  "pattern": {
                    "type": "string",
                    "description": "File pattern (e.g. *.txt)"
                  }
                },
                "required": ["path", "text"]
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "Success"
          }
        }
      }
    },
    "/api/find": {
      "post": {
        "operationId": "findFiles",
        "summary": "Find files by pattern",
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "properties": {
                  "path": {
                    "type": "string",
                    "description": "Directory to search"
                  },
                  "pattern": {
                    "type": "string",
                    "description": "File pattern (e.g. *.jpg)"
                  }
                },
                "required": ["path", "pattern"]
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "Success"
          }
        }
      }
    },
    "/api/tree": {
      "post": {
        "operationId": "directoryTree",
        "summary": "Get directory tree structure",
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "properties": {
                  "path": {
                    "type": "string",
                    "description": "Directory path"
                  },
                  "max_depth": {
                    "type": "integer",
                    "default": 3
                  }
                },
                "required": ["path"]
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "Success"
          }
        }
      }
    },
    "/api/image": {
      "post": {
        "operationId": "getImage",
        "summary": "Get image for GPT Vision",
        "description": "Returns image with auto-compression",
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "properties": {
                  "path": {
                    "type": "string",
                    "description": "Image file path"
                  }
                },
                "required": ["path"]
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "Image file",
            "content": {
              "image/jpeg": {},
              "image/png": {},
              "image/gif": {}
            }
          }
        }
      }
    },
    "/api/image/base64": {
      "post": {
        "operationId": "getImageBase64",
        "summary": "Get image as base64",
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "properties": {
                  "path": {
                    "type": "string",
                    "description": "Image file path"
                  }
                },
                "required": ["path"]
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "Base64 encoded image"
          }
        }
      }
    },
    "/api/images": {
      "post": {
        "operationId": "listImages",
        "summary": "List images in directory",
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "properties": {
                  "path": {
                    "type": "string",
                    "description": "Directory path"
                  }
                },
                "required": ["path"]
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "List of images"
          }
        }
      }
    },
    "/api/copy": {
      "post": {
        "operationId": "copyFile",
        "summary": "Copy file",
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "properties": {
                  "source": {
                    "type": "string",
                    "description": "Source file path"
                  },
                  "destination": {
                    "type": "string",
                    "description": "Destination path"
                  },
                  "overwrite": {
                    "type": "boolean",
                    "default": false
                  }
                },
                "required": ["source", "destination"]
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "Success"
          }
        }
      }
    },
    "/api/delete": {
      "post": {
        "operationId": "deleteFile",
        "summary": "Delete file",
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "properties": {
                  "path": {
                    "type": "string",
                    "description": "File path to delete"
                  }
                },
                "required": ["path"]
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "Success"
          }
        }
      }
    }
  }
}
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
