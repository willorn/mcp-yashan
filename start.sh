#!/bin/bash
# 崖山数据库 MCP Server 启动脚本 (Mac/Linux)

cd "$(dirname "$0")"

echo "正在启动崖山数据库 MCP Server..."
echo "旧版 SSE 端点：http://0.0.0.0:20302/sse"
echo "新版 MCP 端点：http://0.0.0.0:20302/mcp"
echo "健康检查：http://0.0.0.0:20302/healthz"
echo ""

python3 server.py --host 0.0.0.0 --port 20302
