# -*- coding: utf-8 -*-
"""
Java SQL 执行器 - 跨平台实现
使用 Java 子进程调用 JDBC 驱动
"""

import json
import subprocess
import os
import sys
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("yashan_mcp")

# Java SQL 执行器模板
JAVA_TEMPLATE = '''
import java.sql.*;
public class TempSqlExecutor {{
    public static void main(String[] args) throws Exception {{
        String jdbcUrl = "{jdbc_url}";
        String user = "{username}";
        String password = "{password}";
        String sql = args[0];
        int maxRows = Integer.parseInt(args[1]);

        long startTime = System.currentTimeMillis();

        try {{
            Class.forName("com.yashandb.jdbc.Driver");
            Connection conn = DriverManager.getConnection(jdbcUrl, user, password);
            Statement stmt = conn.createStatement();
            stmt.setMaxRows(maxRows);
            boolean isResultSet = stmt.execute(sql);

            if (isResultSet) {{
                ResultSet rs = stmt.getResultSet();
                ResultSetMetaData metaData = rs.getMetaData();
                int columnCount = metaData.getColumnCount();

                System.out.println("COLUMNS:" + columnCount);
                for (int i = 1; i <= columnCount; i++) {{
                    System.out.println("COL:" + metaData.getColumnName(i));
                }}

                int rowCount = 0;
                while (rs.next() && rowCount < maxRows) {{
                    System.out.print("ROW:");
                    for (int i = 1; i <= columnCount; i++) {{
                        if (i > 1) System.out.print("|");
                        Object value = rs.getObject(i);
                        System.out.print(value != null ? value.toString().replace("\\n", " ").replace("\\r", " ").replace("\\t", " ") : "NULL");
                    }}
                    System.out.println();
                    rowCount++;
                }}
                System.out.println("ROW_COUNT:" + rowCount);
                rs.close();
            }} else {{
                int updateCount = stmt.getUpdateCount();
                System.out.println("UPDATE_COUNT:" + updateCount);
            }}

            stmt.close();
            conn.close();
            System.out.println("SUCCESS:true");
        }} catch (Exception e) {{
            System.out.println("SUCCESS:false");
            System.out.println("ERROR:" + e.getMessage());
        }}

        System.out.println("EXEC_TIME:" + (System.currentTimeMillis() - startTime));
    }}
}}
'''


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
        self.jdbc_url = os.getenv("DB_JDBC_URL",
            f"jdbc:yasdb://{self.config['host']}:{self.config['port']}/{self.config['db_name']}?failover=on")
        self.jar_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "yashandb-jdbc-1.9.3.jar")
        self.java_cmd = self._find_java()
        self._initialized = True

    def _find_java(self) -> str:
        """查找 Java 可执行文件（跨平台）"""
        java_home = os.getenv("JAVA_HOME")
        if java_home:
            java_exe = os.path.join(java_home, "bin", "java.exe")
            if os.path.exists(java_exe):
                return java_exe
            java_exe = os.path.join(java_home, "bin", "java")
            if os.path.exists(java_exe):
                return java_exe
        return "java"

    def execute(self, sql: str, max_rows: int = 1000) -> Dict[str, Any]:
        """执行 SQL"""
        temp_dir = os.path.dirname(os.path.dirname(__file__))
        temp_java = os.path.join(temp_dir, "TempSqlExecutor.java")
        temp_class = os.path.join(temp_dir, "TempSqlExecutor.class")

        safe_jdbc_url = self.jdbc_url.replace("\\", "\\\\")
        safe_username = self.config['username'].replace("\\", "\\\\")
        safe_password = self.config['password'].replace("\\", "\\\\")

        java_code = JAVA_TEMPLATE.format(
            jdbc_url=safe_jdbc_url,
            username=safe_username,
            password=safe_password
        )

        try:
            with open(temp_java, "w", encoding="utf-8") as f:
                f.write(java_code)

            javac_cmd = self._get_javac_cmd()
            compile_result = subprocess.run(
                [javac_cmd, "-cp", self.jar_path, temp_java],
                capture_output=True, timeout=30, cwd=temp_dir
            )

            if compile_result.returncode != 0:
                return {
                    "success": False,
                    "error": f"编译失败: {compile_result.stderr.decode('utf-8', errors='ignore')}"
                }

            classpath_sep = ";" if os.name == "nt" else ":"
            result = subprocess.run(
                [self.java_cmd, "-cp", f"{self.jar_path}{classpath_sep}{temp_dir}", "TempSqlExecutor", sql, str(max_rows)],
                capture_output=True, text=True, timeout=60, cwd=temp_dir
            )

            return self._parse_output(result.stdout)

        except Exception as e:
            logger.error(f"SQL 执行错误: {e}")
            return {"success": False, "error": str(e)}
        finally:
            for f in [temp_java, temp_class]:
                try:
                    if os.path.exists(f):
                        os.remove(f)
                except:
                    pass

    def _get_javac_cmd(self) -> str:
        """获取 javac 命令"""
        javac_cmd = self.java_cmd.replace("java.exe", "javac.exe").replace("java", "javac")
        if javac_cmd == "javac":
            return "javac"
        if os.path.exists(javac_cmd):
            return javac_cmd
        return "javac"

    def _parse_output(self, output: str) -> Dict[str, Any]:
        """解析 Java 输出"""
        result = {
            "success": False,
            "columns": [],
            "data": [],
            "row_count": 0,
            "execution_time": 0,
            "error": None
        }

        for line in output.strip().split("\n"):
            line = line.strip()
            if line.startswith("SUCCESS:"):
                result["success"] = line.split(":")[1].lower() == "true"
            elif line.startswith("ERROR:"):
                result["error"] = line[6:]
            elif line.startswith("COLUMNS:"):
                pass
            elif line.startswith("COL:"):
                result["columns"].append(line[4:])
            elif line.startswith("ROW:"):
                row_data = line[4:].split("|")
                row_dict = {}
                for i, col in enumerate(result["columns"]):
                    if i < len(row_data):
                        row_dict[col] = None if row_data[i] == "NULL" else row_data[i]
                result["data"].append(row_dict)
            elif line.startswith("ROW_COUNT:") or line.startswith("UPDATE_COUNT:"):
                result["row_count"] = int(line.split(":")[1])
            elif line.startswith("EXEC_TIME:"):
                result["execution_time"] = float(line.split(":")[1]) / 1000.0

        return result


# 全局单例
_executor = None


def get_executor() -> JavaSqlExecutor:
    """获取执行器（单例）"""
    global _executor
    if _executor is None:
        _executor = JavaSqlExecutor()
    return _executor
