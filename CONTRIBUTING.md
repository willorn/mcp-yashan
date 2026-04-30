# Contributing to MCP YashanDB Server

感谢你考虑为 MCP YashanDB Server 做出贡献！

## 如何贡献

### 报告 Bug

如果你发现了 bug，请在 [GitHub Issues](https://github.com/willorn/mcp-yashan/issues) 创建一个 issue，并包含以下信息：

- **Bug 描述**：清晰简洁地描述问题
- **复现步骤**：详细的复现步骤
- **预期行为**：你期望发生什么
- **实际行为**：实际发生了什么
- **环境信息**：
  - 操作系统（macOS, Linux, Windows）
  - Python 版本
  - Java 版本
  - 崖山数据库版本
  - mcp-yashan 版本
- **日志**：相关的错误日志或堆栈跟踪

### 提出新功能

如果你有新功能的想法，请先创建一个 issue 讨论：

- **功能描述**：清晰描述你想要的功能
- **使用场景**：为什么需要这个功能
- **可能的实现**：如果有想法，可以描述如何实现

### 提交代码

1. **Fork 仓库**

   点击 GitHub 页面右上角的 "Fork" 按钮

2. **克隆你的 Fork**

   ```bash
   git clone https://github.com/willorn/mcp-yashan.git
   cd mcp-yashan
   ```

3. **创建分支**

   ```bash
   git checkout -b feature/your-feature-name
   ```

   分支命名规范：
   - `feature/` - 新功能
   - `fix/` - Bug 修复
   - `docs/` - 文档更新
   - `refactor/` - 代码重构
   - `test/` - 测试相关

4. **安装开发依赖**

   ```bash
   pip install -e ".[dev]"
   ```

5. **进行修改**

   - 遵循现有的代码风格
   - 添加必要的测试
   - 更新相关文档

6. **运行测试**

   ```bash
   # 运行所有测试
   pytest tests/
   
   # 运行特定测试
   pytest tests/test_stability.py
   ```

7. **提交更改**

   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

   提交信息规范（遵循 [Conventional Commits](https://www.conventionalcommits.org/)）：
   - `feat:` - 新功能
   - `fix:` - Bug 修复
   - `docs:` - 文档更新
   - `style:` - 代码格式（不影响功能）
   - `refactor:` - 代码重构
   - `test:` - 测试相关
   - `chore:` - 构建/工具相关

8. **推送到你的 Fork**

   ```bash
   git push origin feature/your-feature-name
   ```

9. **创建 Pull Request**

   - 访问你的 Fork 页面
   - 点击 "New Pull Request"
   - 填写 PR 描述：
     - 修改了什么
     - 为什么要修改
     - 如何测试
     - 相关的 issue（如果有）

## 代码规范

### Python 代码风格

- 遵循 [PEP 8](https://pep8.org/) 规范
- 使用 4 个空格缩进
- 最大行长度：100 字符
- 使用类型提示（Type Hints）

示例：

```python
def execute_sql(sql: str, max_rows: int = 1000) -> Dict[str, Any]:
    """
    执行 SQL 查询
    
    Args:
        sql: SQL 语句
        max_rows: 最大返回行数
        
    Returns:
        包含查询结果的字典
        
    Raises:
        ValueError: 如果 SQL 为空或 max_rows 超出范围
    """
    if not sql or not sql.strip():
        raise ValueError("SQL 语句不能为空")
    
    # 实现...
```

### 文档字符串

- 使用 Google 风格的文档字符串
- 包含参数、返回值、异常说明
- 提供使用示例（如果适用）

### 测试

- 为新功能添加测试
- 确保测试覆盖率不降低
- 测试文件命名：`test_*.py`
- 测试函数命名：`test_*`

示例：

```python
def test_execute_sql_with_valid_input():
    """测试正常的 SQL 执行"""
    executor = get_executor()
    result = executor.execute("SELECT 1 FROM DUAL", max_rows=10)
    
    assert result["success"] is True
    assert len(result["data"]) > 0


def test_execute_sql_with_empty_input():
    """测试空 SQL 输入"""
    executor = get_executor()
    result = executor.execute("", max_rows=10)
    
    assert result["success"] is False
    assert "不能为空" in result["error"]
```

## 开发环境设置

### 1. 安装依赖

```bash
# 安装项目依赖
pip install -r requirements.txt

# 安装开发依赖
pip install -e ".[dev]"
```

### 2. 配置数据库

```bash
cp config/.env.example .env
# 编辑 .env 填写数据库连接信息
```

### 3. 运行测试

```bash
# 运行所有测试
pytest tests/

# 运行特定测试文件
pytest tests/test_stability.py

# 显示详细输出
pytest tests/ -v

# 显示测试覆盖率
pytest tests/ --cov=mcp_yashan
```

### 4. 本地测试 MCP Server

```bash
# STDIO 模式
python3 -m mcp_yashan.mcp_server

# HTTP 模式
python3 -m mcp_yashan.http_server --host 127.0.0.1 --port 20302
```

## 发布流程

（仅维护者）

1. 更新版本号
   - `pyproject.toml`
   - `mcp_yashan/__init__.py`
   - `CHANGELOG.md`

2. 创建 Git tag

   ```bash
   git tag v2.1.0
   git push origin v2.1.0
   ```

3. 构建包

   ```bash
   python3 -m build
   ```

4. 发布到 PyPI

   ```bash
   python3 -m twine upload dist/*
   ```

5. 创建 GitHub Release

## 行为准则

### 我们的承诺

为了营造一个开放和友好的环境，我们承诺：

- 使用友好和包容的语言
- 尊重不同的观点和经验
- 优雅地接受建设性批评
- 关注对社区最有利的事情
- 对其他社区成员表示同理心

### 不可接受的行为

- 使用性化的语言或图像
- 人身攻击或侮辱性评论
- 公开或私下骚扰
- 未经许可发布他人的私人信息
- 其他在专业环境中不适当的行为

## 问题和帮助

如果你有任何问题：

- 查看 [文档](./docs/)
- 搜索 [已有的 Issues](https://github.com/willorn/mcp-yashan/issues)
- 创建新的 Issue

## 许可证

通过贡献代码，你同意你的贡献将在 MIT 许可证下发布。

---

再次感谢你的贡献！🎉
