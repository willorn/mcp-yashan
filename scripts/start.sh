#!/bin/bash
# 崖山数据库 MCP Server 启动脚本 (Mac/Linux)

set -euo pipefail

cd "$(dirname "$0")/.."

echo "正在启动崖山数据库 MCP Server (HTTP 模式)..."
echo "Java Runtime：优先使用 ./runtime/jre/bin/java"
echo "旧版 SSE 端点：http://0.0.0.0:20302/sse"
echo "新版 MCP 端点：http://0.0.0.0:20302/mcp"
echo "健康检查：http://0.0.0.0:20302/healthz"
echo ""

python3 src/http_server.py --host 0.0.0.0 --port 20302
