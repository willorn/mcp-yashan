"""
MCP Server for YashanDB

A Model Context Protocol server that enables AI assistants to interact with YashanDB databases.

支持两种模式：
- STDIO 模式：按需启动，适合本地开发和 AI 工具集成
- HTTP 模式：常驻服务，适合远程访问和多用户场景
"""

__version__ = "2.1.0"
__author__ = "MCP Yashan Team"
__license__ = "MIT"

from .core.executor import get_executor
from .core.tools import TOOLS

__all__ = ["get_executor", "TOOLS", "__version__"]
