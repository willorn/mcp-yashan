#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
崖山数据库 MCP Server - 支持 SSE 和 Streamable HTTP 双协议

保留的 MCP 能力：
- test_connection: 测试数据库连接
- run_sql: 执行 SQL 查询
- list_schemas: 列出所有 Schema（用户）
- list_tables: 列出表
- describe_table: 查看表结构
- search_tables: 搜索表
- get_table_indexes: 查看表索引
- get_table_count: 快速获取表行数
- get_database_info: 获取数据库信息
- explain_sql: 获取 SQL 执行计划

端点：
- GET  /sse      - SSE 连接端点（旧版）
- POST /messages - SSE 消息端点（旧版）
- POST /mcp      - Streamable HTTP 端点（新版，推荐）
- GET  /healthz  - 健康检查
"""

import json
import os
import sys
import logging
import asyncio
from typing import Dict, Any, Optional

from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import Response, StreamingResponse, JSONResponse
from starlette.requests import Request
from starlette.middleware.cors import CORSMiddleware

# 加载环境变量
def _load_env_file():
    """加载 .env 文件"""
    env_file = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_file):
        with open(env_file, "r", encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ.setdefault(key.strip(), value.strip())

_load_env_file()

# 日志配置
logger = logging.getLogger("yashan_mcp")
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr),
        logging.FileHandler(
            os.path.join(os.path.dirname(__file__), 'yashan_mcp.log'),
            encoding='utf-8'
        )
    ]
)

# 导入核心逻辑
from core import get_executor, get_metadata, TOOLS, handle_tool_call

# ============================================================
# SSE 协议支持（旧版，保留兼容）
# ============================================================

clients = {}


async def sse_endpoint(request: Request):
    """SSE 连接端点"""
    client_id = id(request)
    clients[client_id] = {"queue": asyncio.Queue()}

    async def event_generator():
        try:
            # 发送 endpoint 事件
            yield f"event: endpoint\ndata: /messages?sessionId={client_id}\n\n"

            # 等待并转发消息
            while True:
                try:
                    message = await asyncio.wait_for(
                        clients[client_id]["queue"].get(),
                        timeout=30.0
                    )
                    yield f"event: message\ndata: {json.dumps(message)}\n\n"
                except asyncio.TimeoutError:
                    # 发送心跳
                    yield ": ping\n\n"
        except Exception as e:
            logger.error(f"SSE 流错误：{e}")
        finally:
            clients.pop(client_id, None)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


async def messages_endpoint(request: Request):
    """SSE 消息处理端点（POST）"""
    if request.method == "POST":
        try:
            session_id = int(request.query_params.get("sessionId", 0))
            body = await request.json()

            response = await process_mcp_request(body)

            # 将响应放入队列
            if session_id in clients:
                await clients[session_id]["queue"].put(response)

            return JSONResponse({"status": "ok"})

        except Exception as e:
            logger.error(f"消息处理错误：{e}")
            return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

    return JSONResponse({"error": "Method not allowed"}, status_code=405)


# ============================================================
# Streamable HTTP 协议支持（新版，推荐）
# ============================================================

async def mcp_endpoint(request: Request):
    """
    Streamable HTTP MCP 端点

    支持：
    - initialize
    - tools/list
    - tools/call

    返回 JSON 响应，符合 MCP Streamable HTTP 规范
    """
    if request.method != "POST":
        return JSONResponse(
            {"error": "Method not allowed", "message": "Only POST is supported"},
            status_code=405
        )

    try:
        body = await request.json()
        response = await process_mcp_request(body)
        # 对于通知类型的请求（如 notifications/initialized），返回空响应
        if response is None:
            return Response(status_code=202)
        return JSONResponse(response)

    except json.JSONDecodeError as e:
        logger.error(f"JSON 解析错误: {e}")
        return JSONResponse(
            {"jsonrpc": "2.0", "error": {"code": -32700, "message": f"Parse error: {str(e)}"}},
            status_code=400
        )
    except Exception as e:
        logger.error(f"MCP 请求处理错误: {e}")
        return JSONResponse(
            {"jsonrpc": "2.0", "error": {"code": -32603, "message": f"Internal error: {str(e)}"}},
            status_code=500
        )


# ============================================================
# MCP 请求处理（公共逻辑）
# ============================================================

async def process_mcp_request(body: Dict[str, Any]) -> Dict[str, Any]:
    """
    处理 MCP 请求（协议无关的公共逻辑）

    Args:
        body: 请求体

    Returns:
        MCP 响应
    """
    method = body.get("method", "")
    params = body.get("params", {})
    msg_id = body.get("id")

    result = None
    error = None

    if method == "initialize":
        result = {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {},
                "logging": {}
            },
            "serverInfo": {
                "name": "yashan-mcp-server",
                "version": "2.1.0"
            }
        }
    elif method == "notifications/initialized":
        # 客户端初始化完成通知，无需返回结果
        logger.info("Client initialized notification received")
        return None
    elif method == "tools/list":
        result = {"tools": TOOLS}
    elif method == "tools/call":
        tool_name = params.get("name", "")
        args = params.get("arguments", {})
        result = handle_tool_call(tool_name, args)
    else:
        error = {"code": -32601, "message": f"Method not found: {method}"}

    # 构建响应
    if error:
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "error": error
        }
    else:
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": result
        }


# ============================================================
# 健康检查
# ============================================================

async def health_check(request: Request):
    """健康检查"""
    return JSONResponse({
        "ok": True,
        "service": "yashan-mcp-server",
        "version": "2.1.0",
        "protocols": ["sse", "streamable-http"]
    })


# ============================================================
# 创建应用
# ============================================================

routes = [
    # 旧版 SSE 端点（保留兼容）
    Route("/sse", endpoint=sse_endpoint, methods=["GET"]),
    Mount("/messages", routes=[
        Route("/", endpoint=messages_endpoint, methods=["POST"]),
    ]),
    # 新版 Streamable HTTP 端点（推荐）
    Route("/mcp", endpoint=mcp_endpoint, methods=["POST"]),
    # 健康检查
    Route("/healthz", endpoint=health_check, methods=["GET"]),
]

app = Starlette(routes=routes)
app = CORSMiddleware(
    app=app,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# 启动入口
# ============================================================

if __name__ == "__main__":
    import argparse
    import uvicorn

    parser = argparse.ArgumentParser(description="崖山数据库 MCP Server")
    parser.add_argument("--host", default="0.0.0.0", help="监听地址")
    parser.add_argument("--port", type=int, default=20302, help="监听端口")
    args = parser.parse_args()

    logger.info("正在初始化...")
    get_executor()

    config = get_executor().config
    logger.info(f"数据库：{config['host']}:{config['port']}/{config['db_name']}")
    logger.info(f"旧版 SSE 端点：http://{args.host}:{args.port}/sse")
    logger.info(f"新版 MCP 端点：http://{args.host}:{args.port}/mcp")
    logger.info(f"健康检查：http://{args.host}:{args.port}/healthz")

    uvicorn.run(app, host=args.host, port=args.port, forwarded_allow_ips="*")
