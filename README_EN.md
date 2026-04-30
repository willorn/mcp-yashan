# YashanDB MCP Server

<!-- mcp-name: io.github.willorn/mcp-yashan -->

A Model Context Protocol (MCP) server for YashanDB that enables AI assistants to interact with YashanDB databases through natural language.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

[中文文档](./README.md) | English

---

## 🚀 Quick Start

**For new users**: [5-Minute Quick Start Guide](./docs/QUICK_START.md)

---

## Features

- **Complete Database Operations**: Support for SELECT, INSERT, UPDATE, DELETE, and more
- **MCP Protocol Support**: SSE and Streamable HTTP protocols
- **Metadata Management**: Table structure, indexes, table search, row count statistics
- **Multi-Schema Support**: Work with multiple database schemas
- **Detailed Error Handling**: Comprehensive error messages and logging
- **Oracle-Compatible Syntax**: Support for Oracle-compatible SQL syntax
- **Dual Mode Support**:
  - **STDIO Mode** (Recommended): On-demand startup, low resource usage
  - **HTTP Mode**: Persistent service for remote access

## Installation

### Using uvx (Recommended)

```bash
uvx mcp-yashan
```

### Using pip

```bash
pip install mcp-yashan
```

### From Source

```bash
git clone https://github.com/willorn/mcp-yashan.git
cd mcp-yashan
pip install -r requirements.txt
```

## Prerequisites

- Python 3.10+
- **Java 8+ (JRE or JDK)**
- YashanDB or compatible database
- JDBC Driver: `yashandb-jdbc-1.9.3.jar` (included)

### Java Installation

**Check Java version**:
```bash
java -version
# Should show version 1.8 or higher
```

**Install Java if needed**:
- **macOS**: `brew install openjdk@17`
- **Ubuntu/Debian**: `sudo apt install openjdk-17-jre`
- **CentOS/RHEL**: `sudo yum install java-17-openjdk`
- **Windows**: Download from [Oracle](https://www.oracle.com/java/technologies/downloads/) or [OpenJDK](https://adoptium.net/)

## Configuration

Create a `.env` file:

```bash
cp config/.env.example .env
```

Edit `.env`:

```env
DB_HOST=localhost
DB_PORT=1688
DB_NAME=yashandb
DB_USER=your_username
DB_PASSWORD=your_password

# Optional: SQL execution timeout (seconds), default 60
# SQL_TIMEOUT=60
```

Or use a complete JDBC URL:

```env
DB_JDBC_URL=jdbc:yasdb://host:port/dbname?param=value
```

## Usage

### STDIO Mode (Recommended)

```bash
mcp-yashan
# or
python3 -m mcp_yashan.mcp_server
```

### HTTP Mode

```bash
./scripts/start.sh
# or
python3 -m mcp_yashan.http_server --host 0.0.0.0 --port 20302
```

## Integration with AI Tools

### STDIO Mode (Recommended)

Add to your MCP configuration (Kiro, Claude Desktop, etc.):

```json
{
  "mcpServers": {
    "yashan": {
      "command": "uvx",
      "args": ["mcp-yashan"]
    }
  }
}
```

Or if installed via pip:

```json
{
  "mcpServers": {
    "yashan": {
      "command": "mcp-yashan"
    }
  }
}
```

### HTTP Mode

If your client supports `streamable-http`:

```json
{
  "mcpServers": {
    "yashan": {
      "type": "streamable-http",
      "url": "http://your-server-ip:20302/mcp"
    }
  }
}
```

## MCP Tools

| Tool Name | Description |
|-----------|-------------|
| `test_connection` | Test database connection |
| `run_sql` | Execute SQL queries |
| `list_schemas` | List all schemas |
| `list_tables` | List tables |
| `describe_table` | View table structure |
| `search_tables` | Search tables |
| `get_table_indexes` | View table indexes |
| `get_table_count` | Get table row count |
| `get_database_info` | Get database information |
| `explain_sql` | Get SQL execution plan |

## Documentation

- **STDIO Mode**: [docs/STDIO_MODE.md](./docs/STDIO_MODE.md)
- **HTTP Mode**: [docs/HTTP_MODE.md](./docs/HTTP_MODE.md)
- **Quick Start**: [docs/QUICK_START.md](./docs/QUICK_START.md)
- **SQL Guide**: [docs/YASHAN_SQL_GUIDE.md](./docs/YASHAN_SQL_GUIDE.md)
- **Windows Autostart**: [docs/WINDOWS_AUTOSTART.md](./docs/WINDOWS_AUTOSTART.md)

## Project Structure

```
mcp-yashan/
├── mcp_yashan/                 # Source code (Python package)
│   ├── __init__.py
│   ├── mcp_server.py          # STDIO mode entry
│   ├── http_server.py         # HTTP mode entry
│   ├── core/                  # Core logic
│   │   ├── executor.py        # SQL executor
│   │   ├── metadata.py        # Metadata manager
│   │   └── tools.py           # MCP tools
│   └── runtime/               # Runtime dependencies
│       ├── yashandb-jdbc-1.9.3.jar
│       └── java/yashan-mcp-helper.jar
├── config/                     # Configuration
├── scripts/                    # Scripts
├── tests/                      # Tests
├── docs/                       # Documentation
├── pyproject.toml              # Package config
└── README.md                   # Project README
```

## Development

### Run Tests

```bash
pytest tests/
```

### Build Package

```bash
python3 -m build
```

### Install in Development Mode

```bash
pip install -e .
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

MIT License

### Third-Party Dependencies

This project includes the following third-party dependencies:

- **yashandb-jdbc-1.9.3.jar** - Apache License 2.0
  - YashanDB JDBC Driver
  - License: http://www.apache.org/licenses/LICENSE-2.0

- **yashan-mcp-helper.jar** - MIT License
  - Java helper classes compiled by this project

## Support

- **Issues**: [GitHub Issues](https://github.com/willorn/mcp-yashan/issues)
- **Documentation**: [docs/](./docs/)

## Changelog

See [CHANGELOG.md](./CHANGELOG.md) for version history.
