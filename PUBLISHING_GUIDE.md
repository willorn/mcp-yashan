# 发布到 PyPI 指南

本文档详细说明如何将 mcp-yashan 发布到 PyPI。

## 前置准备

### 1. 注册账号

#### TestPyPI（测试环境）
- 访问：https://test.pypi.org/account/register/
- 注册账号并验证邮箱

#### PyPI（生产环境）
- 访问：https://pypi.org/account/register/
- 注册账号并验证邮箱

### 2. 创建 API Token

#### TestPyPI Token

1. 登录 https://test.pypi.org
2. 点击右上角用户名 → Account settings
3. 滚动到 "API tokens" 部分
4. 点击 "Add API token"
5. Token name: `mcp-yashan-test`
6. Scope: `Entire account` (首次发布) 或 `Project: mcp-yashan` (后续发布)
7. 点击 "Add token"
8. **立即复制 token**（只显示一次！）

#### PyPI Token

1. 登录 https://pypi.org
2. 点击右上角用户名 → Account settings
3. 滚动到 "API tokens" 部分
4. 点击 "Add API token"
5. Token name: `mcp-yashan-prod`
6. Scope: `Entire account` (首次发布) 或 `Project: mcp-yashan` (后续发布)
7. 点击 "Add token"
8. **立即复制 token**（只显示一次！）

### 3. 配置 `.pypirc`

创建 `~/.pypirc` 文件：

```bash
cat > ~/.pypirc << 'EOF'
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR-PRODUCTION-TOKEN-HERE

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR-TEST-TOKEN-HERE
EOF

# 设置文件权限（重要！）
chmod 600 ~/.pypirc
```

**注意**：
- 将 `pypi-YOUR-PRODUCTION-TOKEN-HERE` 替换为你的 PyPI token
- 将 `pypi-YOUR-TEST-TOKEN-HERE` 替换为你的 TestPyPI token
- Token 以 `pypi-` 开头

### 4. 安装发布工具

```bash
pip install build twine
```

---

## 发布流程

### 第一步：准备发布

#### 1. 更新版本号

编辑以下文件中的版本号：

**pyproject.toml**:
```toml
[project]
version = "2.1.0"  # 更新这里
```

**mcp_yashan/__init__.py**:
```python
__version__ = "2.1.0"  # 更新这里
```

**server.json**:
```json
{
  "version": "2.1.0",  # 更新这里
  "packages": [
    {
      "version": "2.1.0"  # 更新这里
    }
  ]
}
```

#### 2. 更新 CHANGELOG.md

添加新版本的变更记录：

```markdown
## [2.1.0] - 2026-04-30

### Added
- 新功能描述

### Changed
- 变更描述

### Fixed
- 修复描述
```

#### 3. 提交更改

```bash
git add .
git commit -m "chore: bump version to 2.1.0"
git push origin main
```

#### 4. 创建 Git Tag

```bash
git tag v2.1.0
git push origin v2.1.0
```

### 第二步：构建包

#### 1. 清理旧的构建文件

```bash
rm -rf dist/ build/ *.egg-info
```

#### 2. 构建包

```bash
python3 -m build
```

**预期输出**：
```
Successfully built mcp_yashan-2.1.0.tar.gz and mcp_yashan-2.1.0-py3-none-any.whl
```

#### 3. 检查构建产物

```bash
ls -lh dist/
```

应该看到两个文件：
- `mcp_yashan-2.1.0-py3-none-any.whl` (wheel 包)
- `mcp_yashan-2.1.0.tar.gz` (源码包)

#### 4. 验证包内容

```bash
# 检查 wheel 包内容
unzip -l dist/mcp_yashan-2.1.0-py3-none-any.whl

# 检查源码包内容
tar -tzf dist/mcp_yashan-2.1.0.tar.gz
```

确认包含：
- ✅ Python 源代码
- ✅ JAR 文件（runtime/*.jar）
- ✅ README.md
- ✅ LICENSE
- ✅ 文档（docs/*.md）

### 第三步：发布到 TestPyPI（测试）

#### 1. 上传到 TestPyPI

```bash
python3 -m twine upload --repository testpypi dist/*
```

**预期输出**：
```
Uploading distributions to https://test.pypi.org/legacy/
Uploading mcp_yashan-2.1.0-py3-none-any.whl
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 555.0/555.0 kB • 00:01
Uploading mcp_yashan-2.1.0.tar.gz
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 576.0/576.0 kB • 00:01

View at:
https://test.pypi.org/project/mcp-yashan/2.1.0/
```

#### 2. 验证 TestPyPI 页面

访问：https://test.pypi.org/project/mcp-yashan/

检查：
- ✅ 版本号正确
- ✅ 描述显示正常
- ✅ 依赖列表正确
- ✅ 文件列表完整

#### 3. 测试安装

```bash
# 创建测试环境
python3 -m venv test_env
source test_env/bin/activate  # Windows: test_env\Scripts\activate

# 从 TestPyPI 安装
pip install --index-url https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple/ \
    mcp-yashan

# 验证安装
mcp-yashan --help
python3 -c "import mcp_yashan; print(mcp_yashan.__version__)"
```

#### 4. 测试功能

```bash
# 配置数据库（如果有测试数据库）
export DB_HOST=localhost
export DB_PORT=1688
export DB_NAME=yashandb
export DB_USER=test_user
export DB_PASSWORD=test_password

# 测试 STDIO 模式
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | mcp-yashan

# 测试 HTTP 模式
python3 -m mcp_yashan.http_server --host 127.0.0.1 --port 20302 &
curl http://127.0.0.1:20302/healthz
```

#### 5. 清理测试环境

```bash
deactivate
rm -rf test_env
```

### 第四步：发布到 PyPI（正式）

⚠️ **重要提示**：
- 确保 TestPyPI 测试通过
- 确保版本号正确
- 发布后无法删除，只能发布新版本

#### 1. 上传到 PyPI

```bash
python3 -m twine upload dist/*
```

**预期输出**：
```
Uploading distributions to https://upload.pypi.org/legacy/
Uploading mcp_yashan-2.1.0-py3-none-any.whl
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 555.0/555.0 kB • 00:02
Uploading mcp_yashan-2.1.0.tar.gz
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 576.0/576.0 kB • 00:02

View at:
https://pypi.org/project/mcp-yashan/2.1.0/
```

#### 2. 验证 PyPI 页面

访问：https://pypi.org/project/mcp-yashan/

检查：
- ✅ 版本号正确
- ✅ 描述显示正常
- ✅ 依赖列表正确
- ✅ 文件列表完整
- ✅ 下载统计开始工作

#### 3. 测试安装

```bash
# 创建新的测试环境
python3 -m venv prod_test_env
source prod_test_env/bin/activate

# 从 PyPI 安装
pip install mcp-yashan

# 验证安装
mcp-yashan --help
python3 -c "import mcp_yashan; print(mcp_yashan.__version__)"

# 测试 uvx 安装
deactivate
uvx mcp-yashan --help
```

#### 4. 清理

```bash
rm -rf prod_test_env
```

### 第五步：创建 GitHub Release

#### 1. 访问 GitHub Releases 页面

https://github.com/yourusername/mcp-yashan/releases/new

#### 2. 填写 Release 信息

- **Tag**: `v2.1.0` (选择已创建的 tag)
- **Release title**: `v2.1.0 - PyPI 打包支持`
- **Description**: 从 CHANGELOG.md 复制对应版本的内容

示例：

```markdown
## What's New

### Added
- **PyPI 打包支持**：现在可以通过 `pip install mcp-yashan` 或 `uvx mcp-yashan` 安装
- **STDIO 模式**：按需启动的 MCP 服务器模式
- **HTTP 模式**：常驻的 HTTP 服务器模式
- 详细文档（5 分钟快速上手、STDIO 模式、HTTP 模式）

### Changed
- 目录结构重构为标准 Python 包
- 移除内置 JRE，用户需自行安装 Java 8+

### Installation

```bash
# Using uvx (recommended)
uvx mcp-yashan

# Using pip
pip install mcp-yashan
```

**Full Changelog**: https://github.com/yourusername/mcp-yashan/compare/v2.0.0...v2.1.0
```

#### 3. 附加构建产物

上传以下文件：
- `dist/mcp_yashan-2.1.0-py3-none-any.whl`
- `dist/mcp_yashan-2.1.0.tar.gz`

#### 4. 发布

点击 "Publish release"

---

## 注册到 MCP Registry

### 第一步：准备 server.json

确保 `server.json` 已创建并包含正确信息：

```json
{
  "$schema": "https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json",
  "name": "io.github.yourusername/mcp-yashan",
  "title": "YashanDB MCP Server",
  "description": "MCP Server for YashanDB...",
  "version": "2.1.0",
  "packages": [
    {
      "registryType": "pypi",
      "identifier": "mcp-yashan",
      "version": "2.1.0",
      "transport": {
        "type": "stdio"
      }
    }
  ]
}
```

### 第二步：验证 README 标记

确保 README.md 包含验证标记：

```markdown
<!-- mcp-name: io.github.yourusername/mcp-yashan -->
```

### 第三步：提交到 MCP Registry

1. **Fork MCP Servers 仓库**

   访问：https://github.com/modelcontextprotocol/servers
   点击 "Fork"

2. **克隆你的 Fork**

   ```bash
   git clone https://github.com/your-username/servers.git
   cd servers
   ```

3. **添加 server.json**

   ```bash
   cp /path/to/mcp-yashan/server.json src/servers/mcp-yashan.json
   ```

4. **提交更改**

   ```bash
   git add src/servers/mcp-yashan.json
   git commit -m "Add mcp-yashan server"
   git push origin main
   ```

5. **创建 Pull Request**

   - 访问你的 Fork 页面
   - 点击 "New Pull Request"
   - 填写 PR 描述：

   ```markdown
   ## Add YashanDB MCP Server
   
   This PR adds the YashanDB MCP Server to the registry.
   
   **Package**: https://pypi.org/project/mcp-yashan/
   **Repository**: https://github.com/yourusername/mcp-yashan
   **License**: MIT
   
   ### Description
   
   MCP Server for YashanDB that enables AI assistants to interact with YashanDB databases through natural language.
   
   ### Features
   
   - Complete database operations (SELECT, INSERT, UPDATE, DELETE)
   - Metadata management
   - Multi-schema support
   - Oracle-compatible SQL syntax
   - Dual mode support (STDIO and HTTP)
   
   ### Verification
   
   - [x] Package published to PyPI
   - [x] README contains mcp-name verification comment
   - [x] server.json follows the schema
   - [x] Tested installation: `uvx mcp-yashan`
   ```

6. **等待审核**

   MCP Registry 维护者会审核你的 PR。

---

## 后续版本发布

### 版本号规范

遵循 [Semantic Versioning](https://semver.org/)：

- **MAJOR** (x.0.0): 不兼容的 API 变更
- **MINOR** (0.x.0): 向后兼容的新功能
- **PATCH** (0.0.x): 向后兼容的 bug 修复

示例：
- `2.1.0` → `2.1.1` (bug 修复)
- `2.1.0` → `2.2.0` (新功能)
- `2.1.0` → `3.0.0` (破坏性变更)

### 发布检查清单

- [ ] 更新版本号（pyproject.toml, __init__.py, server.json）
- [ ] 更新 CHANGELOG.md
- [ ] 运行所有测试
- [ ] 提交更改
- [ ] 创建 Git tag
- [ ] 清理旧构建文件
- [ ] 构建新包
- [ ] 发布到 TestPyPI 并测试
- [ ] 发布到 PyPI
- [ ] 创建 GitHub Release
- [ ] 更新 MCP Registry（如果需要）

---

## 故障排查

### 问题 1：上传失败 - 401 Unauthorized

**原因**：API Token 错误或过期

**解决**：
1. 检查 `~/.pypirc` 中的 token 是否正确
2. 确保 token 以 `pypi-` 开头
3. 重新生成 token 并更新配置

### 问题 2：上传失败 - 400 Bad Request

**原因**：包配置错误

**解决**：
1. 检查 `pyproject.toml` 配置
2. 运行 `python3 -m build` 查看警告
3. 使用 `twine check dist/*` 验证包

### 问题 3：版本已存在

**错误**：`File already exists`

**原因**：PyPI 不允许覆盖已发布的版本

**解决**：
1. 更新版本号（如 2.1.0 → 2.1.1）
2. 重新构建和上传

### 问题 4：包大小超限

**错误**：`File size exceeds maximum`

**原因**：包大小超过 60 MB

**解决**：
1. 检查是否包含了不必要的文件
2. 更新 `MANIFEST.in` 排除大文件
3. 考虑运行时下载大文件

### 问题 5：依赖安装失败

**原因**：依赖版本冲突

**解决**：
1. 检查 `pyproject.toml` 中的依赖版本
2. 使用更宽松的版本约束（如 `>=0.37.0` 而不是 `==0.37.0`）
3. 测试不同 Python 版本的兼容性

---

## 参考资源

- **PyPI 官方文档**：https://packaging.python.org/
- **Twine 文档**：https://twine.readthedocs.io/
- **MCP Registry**：https://github.com/modelcontextprotocol/servers
- **Semantic Versioning**：https://semver.org/
- **Keep a Changelog**：https://keepachangelog.com/

---

## 联系方式

如有问题，请：
- 创建 [GitHub Issue](https://github.com/yourusername/mcp-yashan/issues)
- 查看 [文档](./docs/)
