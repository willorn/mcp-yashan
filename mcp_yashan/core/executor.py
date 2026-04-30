# -*- coding: utf-8 -*-
"""
Java SQL 执行器 - 跨平台实现
支持开发环境和打包后的环境。
"""

import base64
import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger("yashan_mcp")

# 支持打包后的环境
try:
    # Python 3.9+
    from importlib.resources import files
    PACKAGE_ROOT = files('mcp_yashan')
    RUNTIME_DIR = PACKAGE_ROOT / 'runtime'
    IS_PACKAGED = True
except Exception:
    # 开发环境回退
    PACKAGE_ROOT = Path(__file__).resolve().parent.parent
    RUNTIME_DIR = PACKAGE_ROOT / 'runtime'
    IS_PACKAGED = False

# 项目根目录（用于查找 .env）
if IS_PACKAGED:
    PROJECT_ROOT = Path.cwd()
else:
    PROJECT_ROOT = PACKAGE_ROOT.parent

DEFAULT_JDBC_JAR = "yashandb-jdbc-1.9.3.jar"
HELPER_CLASS = "io.yashan.mcp.SqlExecutorMain"


def _get_runtime_path(relative_path: str) -> Path:
    """获取 runtime 目录下的文件路径（兼容打包和开发环境）"""
    if IS_PACKAGED:
        # 打包环境：需要提取到临时目录
        import tempfile
        import shutil as sh
        
        temp_dir = Path(tempfile.gettempdir()) / "mcp_yashan_runtime"
        temp_dir.mkdir(exist_ok=True)
        
        target_file = temp_dir / relative_path
        if not target_file.exists():
            target_file.parent.mkdir(parents=True, exist_ok=True)
            # 从包中复制文件
            try:
                source = RUNTIME_DIR / relative_path
                with source.open('rb') as src:
                    target_file.write_bytes(src.read())
            except Exception as e:
                logger.error(f"无法提取运行时文件 {relative_path}: {e}")
        
        return target_file
    else:
        # 开发环境：直接返回路径
        return RUNTIME_DIR / relative_path


def _load_env_file() -> None:
    """从项目根目录加载 .env"""
    # 尝试多个可能的位置
    env_candidates = [
        PROJECT_ROOT / ".env",
        Path.cwd() / ".env",
        Path.home() / ".mcp_yashan" / ".env",
    ]
    
    for env_file in env_candidates:
        if env_file.exists():
            logger.debug(f"加载配置文件: {env_file}")
            for line in env_file.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ.setdefault(key.strip(), value.strip())
            break


_load_env_file()


class JavaSqlExecutor:
    """Java SQL 执行器 - 跨平台"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.config = {
            "host": os.getenv("DB_HOST", "localhost"),
            "port": os.getenv("DB_PORT", "1688"),
            "db_name": os.getenv("DB_NAME", "yashandb"),
            "username": os.getenv("DB_USER", ""),
            "password": os.getenv("DB_PASSWORD", ""),
        }
        self.jdbc_url = os.getenv(
            "DB_JDBC_URL",
            f"jdbc:yasdb://{self.config['host']}:{self.config['port']}/{self.config['db_name']}?failover=on"
        )
        
        # 使用新的路径获取方式
        jdbc_jar_name = os.getenv("YASHAN_JDBC_JAR", DEFAULT_JDBC_JAR)
        self.jar_path = _get_runtime_path(jdbc_jar_name)
        self.helper_jar_path = _get_runtime_path("java/yashan-mcp-helper.jar")
        
        self.java_cmd = self._find_java()
        # 可配置的超时时间（秒），默认 60 秒
        self.sql_timeout = int(os.getenv("SQL_TIMEOUT", "60"))
        self._initialized = True

    def _find_java(self) -> str:
        """优先查找系统 Java，其次查找环境变量。"""
        candidates = []

        bundled_home = os.getenv("YASHAN_JAVA_HOME")
        if bundled_home:
            candidates.append(Path(bundled_home))

        # 不再查找 runtime/jre（已移除内置 JRE）
        
        java_home = os.getenv("JAVA_HOME")
        if java_home:
            candidates.append(Path(java_home))

        for home in candidates:
            java_cmd = self._java_from_home(home)
            if java_cmd:
                return java_cmd

        java_on_path = shutil.which("java")
        if java_on_path:
            return java_on_path

        raise FileNotFoundError(
            "未找到可用的 Java 运行时。请安装 Java 8+ (JRE 或 JDK)，"
            "或设置 JAVA_HOME 环境变量。"
        )

    @staticmethod
    def _java_from_home(java_home: Path) -> Optional[str]:
        if not java_home:
            return None

        for executable in ("java.exe", "java"):
            java_cmd = java_home / "bin" / executable
            if java_cmd.exists():
                return str(java_cmd)
        return None

    def execute(self, sql: str, max_rows: int = 1000) -> Dict[str, Any]:
        """执行 SQL"""
        # 输入验证
        if not sql or not sql.strip():
            return {"success": False, "error": "SQL 语句不能为空"}
        
        if max_rows < 1 or max_rows > 10000:
            return {"success": False, "error": f"max_rows 必须在 1-10000 之间，当前值: {max_rows}"}
        
        if not self.jar_path.exists():
            return {"success": False, "error": f"JDBC 驱动不存在: {self.jar_path}"}

        if not self.helper_jar_path.exists():
            return {"success": False, "error": f"Java helper 不存在: {self.helper_jar_path}"}

        classpath_sep = ";" if os.name == "nt" else ":"
        classpath = f"{self.jar_path}{classpath_sep}{self.helper_jar_path}"

        try:
            result = subprocess.run(
                [
                    self.java_cmd,
                    "-cp",
                    classpath,
                    HELPER_CLASS,
                    sql,
                    str(max_rows),
                    self.jdbc_url,
                    self.config["username"],
                    self.config["password"],
                ],
                capture_output=True,
                text=True,
                timeout=self.sql_timeout,
            )

            if result.returncode != 0 and not result.stdout:
                return {
                    "success": False,
                    "error": result.stderr.strip() or f"Java 进程退出码: {result.returncode}",
                }

            return self._parse_output(result.stdout, result.stderr)

        except subprocess.TimeoutExpired:
            logger.warning("SQL 执行超时 (%d 秒): %s", self.sql_timeout, sql[:100])
            return {"success": False, "error": f"SQL 执行超时（{self.sql_timeout} 秒）"}
        except Exception as e:
            logger.error("SQL 执行错误: %s", e)
            return {"success": False, "error": str(e)}

    def _parse_output(self, output: str, stderr: str = "") -> Dict[str, Any]:
        """解析 Java 输出"""
        result = {
            "success": False,
            "columns": [],
            "data": [],
            "row_count": 0,
            "execution_time": 0,
            "error": None,
        }

        try:
            for raw_line in output.strip().splitlines():
                line = raw_line.strip()
                if line.startswith("SUCCESS:"):
                    result["success"] = line.split(":", 1)[1].lower() == "true"
                elif line.startswith("ERROR:"):
                    result["error"] = line[6:]
                elif line.startswith("COL:"):
                    result["columns"].append(line[4:])
                elif line.startswith("ROW_B64:"):
                    row_data = line[8:].split("|")
                    row_dict = {}
                    for i, col in enumerate(result["columns"]):
                        if i >= len(row_data):
                            continue
                        encoded_value = row_data[i]
                        if encoded_value == "NULL":
                            row_dict[col] = None
                        else:
                            try:
                                row_dict[col] = base64.b64decode(encoded_value).decode("utf-8")
                            except Exception as decode_err:
                                logger.warning("解码失败: %s", decode_err)
                                row_dict[col] = f"<解码错误: {encoded_value[:20]}...>"
                    result["data"].append(row_dict)
                elif line.startswith("ROW_COUNT:") or line.startswith("UPDATE_COUNT:"):
                    try:
                        result["row_count"] = int(line.split(":", 1)[1])
                    except ValueError:
                        logger.warning("无法解析行数: %s", line)
                elif line.startswith("EXEC_TIME:"):
                    try:
                        result["execution_time"] = float(line.split(":", 1)[1]) / 1000.0
                    except ValueError:
                        logger.warning("无法解析执行时间: %s", line)

            if not result["success"] and not result["error"] and stderr.strip():
                result["error"] = stderr.strip()

        except Exception as e:
            logger.error("解析 Java 输出失败: %s", e)
            result["error"] = f"解析输出失败: {str(e)}"

        return result


_executor = None


def get_executor() -> JavaSqlExecutor:
    """获取执行器（单例）"""
    global _executor
    if _executor is None:
        _executor = JavaSqlExecutor()
    return _executor
