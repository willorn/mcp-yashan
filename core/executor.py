# -*- coding: utf-8 -*-
"""
Java SQL 执行器 - 跨平台实现
优先使用仓库内置的 Java Runtime，不依赖用户机器上的系统 Java。
"""

import base64
import logging
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger("yashan_mcp")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_JDBC_JAR = "yashandb-jdbc-1.9.3.jar"
HELPER_CLASS = "io.yashan.mcp.SqlExecutorMain"
HELPER_JAR = PROJECT_ROOT / "runtime" / "java" / "yashan-mcp-helper.jar"


def _load_env_file() -> None:
    """从项目根目录加载 .env，避免只有 server.py 才能初始化配置。"""
    env_file = PROJECT_ROOT / ".env"
    if not env_file.exists():
        return

    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


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
        self.jar_path = PROJECT_ROOT / os.getenv("YASHAN_JDBC_JAR", DEFAULT_JDBC_JAR)
        self.helper_jar_path = Path(os.getenv("YASHAN_HELPER_JAR", str(HELPER_JAR)))
        self.java_cmd = self._find_java()
        self._initialized = True

    def _find_java(self) -> str:
        """优先查找仓库内置 Java，其次回退到环境变量和 PATH。"""
        candidates = []

        bundled_home = os.getenv("YASHAN_JAVA_HOME")
        if bundled_home:
            candidates.append(Path(bundled_home))

        candidates.extend(
            [
                PROJECT_ROOT / "runtime" / "jre",
                PROJECT_ROOT / "runtime" / "java" / "jre",
            ]
        )

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
            "未找到可用的 Java 运行时。请确保仓库内存在 runtime/jre，"
            "或设置 YASHAN_JAVA_HOME / JAVA_HOME。"
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
                timeout=60,
                cwd=PROJECT_ROOT,
            )

            if result.returncode != 0 and not result.stdout:
                return {
                    "success": False,
                    "error": result.stderr.strip() or f"Java 进程退出码: {result.returncode}",
                }

            return self._parse_output(result.stdout, result.stderr)

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
                        row_dict[col] = base64.b64decode(encoded_value).decode("utf-8")
                result["data"].append(row_dict)
            elif line.startswith("ROW_COUNT:") or line.startswith("UPDATE_COUNT:"):
                result["row_count"] = int(line.split(":", 1)[1])
            elif line.startswith("EXEC_TIME:"):
                result["execution_time"] = float(line.split(":", 1)[1]) / 1000.0

        if not result["success"] and not result["error"] and stderr.strip():
            result["error"] = stderr.strip()

        return result


_executor = None


def get_executor() -> JavaSqlExecutor:
    """获取执行器（单例）"""
    global _executor
    if _executor is None:
        _executor = JavaSqlExecutor()
    return _executor
