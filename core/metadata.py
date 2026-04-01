# -*- coding: utf-8 -*-
"""
元数据管理器
"""

from typing import List, Dict, Optional
from .executor import JavaSqlExecutor, get_executor


class MetadataManager:
    """元数据管理器"""

    _instance = None

    def __new__(cls, executor: JavaSqlExecutor = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, executor: JavaSqlExecutor = None):
        if self._initialized:
            return
        self.executor = executor or get_executor()
        self._initialized = True

    def list_schemas(self) -> List[str]:
        """列出所有 Schema"""
        sql = """
            SELECT USERNAME FROM ALL_USERS
            WHERE USERNAME NOT IN ('SYS', 'SYSTEM', 'PUBLIC')
            ORDER BY USERNAME
        """
        result = self.executor.execute(sql)
        if result.get("success") and result.get("data"):
            return [row.get('USERNAME', '') for row in result["data"]]
        return []

    def list_tables(self, schema: str = None) -> List[Dict]:
        """列出表"""
        if schema:
            sql = f"""
                SELECT TABLE_NAME, OWNER
                FROM ALL_TABLES
                WHERE OWNER = '{schema.upper()}'
                ORDER BY TABLE_NAME
            """
        else:
            sql = """
                SELECT TABLE_NAME, OWNER
                FROM ALL_TABLES
                ORDER BY OWNER, TABLE_NAME
            """

        result = self.executor.execute(sql, max_rows=1000)
        tables = []
        if result.get("success") and result.get("data"):
            for row in result["data"]:
                tables.append({
                    "name": row.get('TABLE_NAME', ''),
                    "owner": row.get('OWNER', '')
                })
        return tables

    def describe_table(self, table_name: str, schema: str = None) -> List[Dict]:
        """获取表结构"""
        schema_filter = f"AND OWNER = '{schema.upper()}'" if schema else ""

        sql = f"""
            SELECT
                COLUMN_NAME,
                DATA_TYPE,
                DATA_LENGTH,
                NULLABLE,
                DATA_DEFAULT
            FROM ALL_TAB_COLUMNS
            WHERE TABLE_NAME = '{table_name.upper()}' {schema_filter}
            ORDER BY COLUMN_ID
        """

        result = self.executor.execute(sql)
        columns = []
        if result.get("success") and result.get("data"):
            for row in result["data"]:
                columns.append({
                    "name": row.get('COLUMN_NAME', ''),
                    "data_type": row.get('DATA_TYPE', ''),
                    "length": row.get('DATA_LENGTH', 0),
                    "nullable": row.get('NULLABLE', 'Y') == 'Y',
                    "default": row.get('DATA_DEFAULT')
                })
        return columns

    def search_tables(self, pattern: str, schema: str = None) -> List[Dict]:
        """搜索表"""
        schema_filter = f"AND OWNER = '{schema.upper()}'" if schema else ""

        sql = f"""
            SELECT TABLE_NAME, OWNER
            FROM ALL_TABLES
            WHERE TABLE_NAME LIKE '%{pattern.upper()}%'
            {schema_filter}
            ORDER BY OWNER, TABLE_NAME
        """

        result = self.executor.execute(sql, max_rows=200)
        tables = []
        if result.get("success") and result.get("data"):
            for row in result["data"]:
                tables.append({
                    "name": row.get('TABLE_NAME', ''),
                    "owner": row.get('OWNER', '')
                })
        return tables

    def get_table_indexes(self, table_name: str, schema: str = None) -> List[Dict]:
        """获取表索引"""
        schema_filter = f"AND TABLE_OWNER = '{schema.upper()}'" if schema else ""

        sql = f"""
            SELECT
                INDEX_NAME,
                INDEX_TYPE,
                UNIQUENESS,
                TABLE_NAME,
                TABLE_OWNER
            FROM ALL_INDEXES
            WHERE TABLE_NAME = '{table_name.upper()}' {schema_filter}
            ORDER BY INDEX_NAME
        """

        result = self.executor.execute(sql)
        return result.get("data", []) if result.get("success") else []

    def get_table_count(self, table_name: str, schema: str = None) -> int:
        """获取表行数"""
        full_table = f"{schema.upper()}.{table_name.upper()}" if schema else table_name.upper()
        sql = f"SELECT COUNT(*) as count FROM {full_table}"

        result = self.executor.execute(sql)
        if result.get("success") and result.get("data"):
            return result["data"][0].get('COUNT', 0)
        return 0


# 全局单例
_metadata = None


def get_metadata() -> MetadataManager:
    """获取元数据管理器（单例）"""
    global _metadata
    if _metadata is None:
        _metadata = MetadataManager(get_executor())
    return _metadata
