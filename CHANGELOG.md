# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.1] - 2026-04-30

### Fixed
- **关键 Bug 修复**：修复 `core/__init__.py` 中的导入错误
  - 将 `get_metadata_manager` 改为正确的 `get_metadata`
  - 修复了 `ImportError: cannot import name 'get_metadata_manager'` 错误
  - 现在可以正常执行 `python -m mcp_yashan` 和 `uvx mcp-yashan`

## [2.1.0] - 2026-04-30

### Added
- **PyPI 打包支持**：项目现在可以通过 `pip install mcp-yashan` 或 `uvx mcp-yashan` 安装
- **STDIO 模式**：按需启动的 MCP 服务器模式，适合本地开发和 AI 工具集成
- **HTTP 模式**：常驻的 HTTP 服务器模式，适合远程访问和多用户场景
- **输入验证**：SQL 语句非空验证，max_rows 范围验证（1-10000）
- **超时保护**：可配置的 SQL 执行超时（默认 60 秒）
- **增强的异常处理**：单独捕获 TimeoutExpired 异常
- **解析容错**：Base64 解码和数值解析异常保护
- **详细文档**：
  - 5 分钟快速上手指南
  - STDIO 模式文档（3000+ 字）
  - HTTP 模式文档（2500+ 字）
  - 崖山 SQL 语法指南

### Changed
- **目录结构重构**：
  - `src/` → `mcp_yashan/` (符合 Python 包规范)
  - `runtime/` → `mcp_yashan/runtime/` (JAR 文件包含在包内)
  - 根目录从 14 个文件减少到核心文件
- **移除内置 JRE**：用户需要自行安装 Java 8+ (JRE 或 JDK)
- **Git 仓库瘦身**：从 215MB 降至 1.5MB（减少 99.3%）
- **导入路径更新**：所有导入使用 `mcp_yashan` 包名

### Fixed
- 超时异常处理改进
- Base64 解码容错
- 数值解析异常保护

### Security
- 输入验证防止恶意输入
- SQL 执行超时防止长时间阻塞

## [2.0.0] - 2026-04-24

### Added
- 初始版本
- 10 个 MCP 工具：
  - test_connection - 测试数据库连接
  - run_sql - 执行 SQL 查询
  - list_schemas - 列出所有 Schema
  - list_tables - 列出表
  - describe_table - 查看表结构
  - search_tables - 搜索表
  - get_table_indexes - 查看表索引
  - get_table_count - 获取表行数
  - get_database_info - 获取数据库信息
  - explain_sql - 获取 SQL 执行计划
- MCP SSE / Streamable HTTP 协议支持
- 元数据管理
- 多 Schema 支持
- 详细的错误处理和日志记录
- Oracle 兼容语法支持

[2.1.1]: https://github.com/willorn/mcp-yashan/compare/v2.1.0...v2.1.1
[2.1.0]: https://github.com/willorn/mcp-yashan/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/willorn/mcp-yashan/releases/tag/v2.0.0
