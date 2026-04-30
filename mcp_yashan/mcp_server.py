#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
崖山数据库 MCP Server - STDIO 模式（默认）

用法：
  python3 -m mcp_yashan.mcp_server
  或
  mcp-yashan

配置：
  通过 .env 文件配置数据库连接
"""

import json
import logging
import os
import sys
from pathlib import Path

from mcp_yashan.core import get_executor, TOOLS, handle_tool_call

# 配置日志（只输出到 stderr，避免污染 stdout）
log_dir = Path(__file__).parent.parent / "logs"
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "WARNING").upper(),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "yashan_mcp_stdio.log"),
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger("yashan_mcp")


def handle_initialize(request_id):
    """处理 initialize 请求"""
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {
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
    }


def handle_tools_list(request_id):
    """处理 tools/list 请求"""
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {"tools": TOOLS}
    }


def handle_tools_call(request_id, params):
    """处理 tools/call 请求"""
    tool_name = params.get("name", "")
    args = params.get("arguments", {})
    
    try:
        result = handle_tool_call(tool_name, args)
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result
        }
    except Exception as e:
        logger.error(f"工具调用失败 {tool_name}: {e}", exc_info=True)
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32603,
                "message": f"工具执行错误: {str(e)}"
            }
        }


def handle_notification(method, params):
    """处理通知（无需返回）"""
    if method == "notifications/initialized":
        logger.info("客户端初始化完成")
    else:
        logger.debug(f"收到通知: {method}")


def handle_request(request):
    """处理单个 MCP 请求"""
    try:
        method = request.get("method", "")
        params = request.get("params", {})
        request_id = request.get("id")
        
        # 通知类型（无 id）
        if request_id is None:
            handle_notification(method, params)
            return None
        
        # 请求类型（有 id）
        if method == "initialize":
            return handle_initialize(request_id)
        elif method == "tools/list":
            return handle_tools_list(request_id)
        elif method == "tools/call":
            return handle_tools_call(request_id, params)
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"方法不存在: {method}"
                }
            }
    
    except Exception as e:
        logger.error(f"处理请求失败: {e}", exc_info=True)
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "error": {
                "code": -32603,
                "message": f"内部错误: {str(e)}"
            }
        }


def main():
    """主循环：从 stdin 读取请求，向 stdout 输出响应"""
    # 检查配置（在启动时）
    import sys
    if sys.stdin.isatty():  # 只在交互式终端检查
        from mcp_yashan.config_wizard import check_and_prompt
        if not check_and_prompt():
            sys.exit(1)
    
    logger.info("崖山数据库 MCP Server (STDIO) 启动")
    logger.info(f"日志文件: {log_dir / 'yashan_mcp_stdio.log'}")
    
    # 验证配置
    try:
        executor = get_executor()
        logger.info(f"数据库配置: {executor.config['host']}:{executor.config['port']}")
    except Exception as e:
        logger.error(f"初始化失败: {e}")
        # 如果是交互式终端，提示用户
        if sys.stdin.isatty():
            print(f"\n❌ 初始化失败: {e}", file=sys.stderr)
            print("\n请检查配置或运行: mcp-yashan --configure", file=sys.stderr)
        sys.exit(1)
    
    # 主循环
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        
        try:
            request = json.loads(line)
            response = handle_request(request)
            
            # 通知类型不返回响应
            if response is not None:
                print(json.dumps(response), flush=True)
        
        except json.JSONDecodeError as e:
            logger.error(f"JSON 解析失败: {e}")
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": f"JSON 解析错误: {str(e)}"
                }
            }
            print(json.dumps(error_response), flush=True)
        
        except Exception as e:
            logger.error(f"未知错误: {e}", exc_info=True)


if __name__ == "__main__":
    # 处理命令行参数
    if len(sys.argv) > 1:
        if sys.argv[1] in ["--configure", "-c", "configure"]:
            from mcp_yashan.config_wizard import run_wizard
            success = run_wizard(silent=False)
            sys.exit(0 if success else 1)
        elif sys.argv[1] in ["--help", "-h", "help"]:
            print("""
崖山数据库 MCP Server - STDIO 模式

用法:
  mcp-yashan                启动 STDIO 模式服务器
  mcp-yashan --configure    运行配置向导
  mcp-yashan --help         显示帮助信息

配置:
  通过 .env 文件或环境变量配置数据库连接
  详见: https://github.com/willorn/mcp-yashan
""")
            sys.exit(0)
        else:
            print(f"未知参数: {sys.argv[1]}", file=sys.stderr)
            print("使用 --help 查看帮助", file=sys.stderr)
            sys.exit(1)
    
    main()
