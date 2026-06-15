# Git 提交和 Release 指南

## 需要提交的核心文件

### 必需文件（核心功能）
```bash
git add mcp_yashan/                    # Python 包（源代码）
git add pyproject.toml                 # 包配置
git add MANIFEST.in                    # 打包清单
git add server.json                    # MCP Registry 配置
git add README.md                      # 中文文档
git add README_EN.md                   # 英文文档
git add CHANGELOG.md                   # 版本历史
git add CONTRIBUTING.md                # 贡献指南
git add PUBLISHING_GUIDE.md            # 发布指南
git add LICENSE                        # 许可证
git add requirements.txt               # Python 依赖
git add .gitignore                     # Git 忽略规则
```

### 需要删除的旧文件
```bash
git rm -r src/                         # 旧的源代码目录
git rm runtime/java/yashan-mcp-helper.jar
git rm runtime/yashandb-jdbc-1.9.3.jar
```

### 更新的文件
```bash
git add docs/QUICK_START.md
git add scripts/start.sh
```

## 执行提交

```bash
# 1. 添加核心文件
git add mcp_yashan/ pyproject.toml MANIFEST.in server.json
git add README.md README_EN.md CHANGELOG.md CONTRIBUTING.md PUBLISHING_GUIDE.md
git add LICENSE requirements.txt .gitignore
git add docs/QUICK_START.md scripts/start.sh

# 2. 删除旧文件
git rm -r src/
git rm runtime/java/yashan-mcp-helper.jar
git rm runtime/yashandb-jdbc-1.9.3.jar

# 3. 提交
git commit -m "feat: PyPI packaging support (v2.1.0)

- Restructure project to Python package format
- Add STDIO mode (recommended for local use)
- Add HTTP mode (for remote access)
- Add input validation and timeout protection
- Add comprehensive documentation
- Publish to PyPI: https://pypi.org/project/mcp-yashan/
"

# 4. 创建 tag
git tag -a v2.1.0 -m "Release v2.1.0 - PyPI packaging support"

# 5. 推送到 GitHub
git push origin main
git push origin v2.1.0
```

## 创建 GitHub Release

### 方式 1：通过 GitHub 网页（推荐）

1. 访问：https://github.com/willorn/mcp-yashan/releases/new

2. 填写信息：
   - **Choose a tag**: 选择 `v2.1.0`
   - **Release title**: `v2.1.0 - PyPI 打包支持`
   - **Description**: 见下方

3. 上传文件：
   - `dist/mcp_yashan-2.1.0-py3-none-any.whl`
   - `dist/mcp_yashan-2.1.0.tar.gz`

4. 点击 "Publish release"

### Release 描述（复制使用）

```markdown
## 🎉 v2.1.0 - PyPI 打包支持

现在可以通过 PyPI 一键安装 mcp-yashan！

### 安装方式

```bash
# 使用 uvx（推荐）
uvx mcp-yashan

# 使用 pip
pip install mcp-yashan
```

### 集成到 AI 工具

```json
{
  "mcpServers": {
    "yashan": {
      "command": "uvx",
      "args": ["mcp-yashan"]
    }
  }
}
```

---

## ✨ 新增功能

### PyPI 打包支持
- ✅ 发布到 PyPI：https://pypi.org/project/mcp-yashan/
- ✅ 一键安装：`pip install mcp-yashan`
- ✅ 命令行工具：`mcp-yashan`

### STDIO 模式（推荐）
- ✅ 按需启动，用完即退
- ✅ 资源占用低
- ✅ 适合本地开发和 AI 工具集成
- ✅ 详细文档：[STDIO 模式指南](./docs/STDIO_MODE.md)

### HTTP 模式
- ✅ 常驻服务
- ✅ 支持远程访问
- ✅ 适合多用户场景
- ✅ 详细文档：[HTTP 模式指南](./docs/HTTP_MODE.md)

### 稳定性增强
- ✅ 输入验证（SQL 非空，max_rows 1-10000）
- ✅ 超时保护（可配置，默认 60 秒）
- ✅ 增强的异常处理
- ✅ Base64 解码容错

### 文档完善
- ✅ [5 分钟快速上手指南](./docs/QUICK_START.md)
- ✅ [STDIO 模式文档](./docs/STDIO_MODE.md)（3000+ 字）
- ✅ [HTTP 模式文档](./docs/HTTP_MODE.md)（2500+ 字）
- ✅ [贡献指南](./CONTRIBUTING.md)
- ✅ [发布指南](./PUBLISHING_GUIDE.md)

---

## 🔄 重大变更

### 目录结构重构
- `src/` → `mcp_yashan/` (符合 Python 包规范)
- `runtime/` → `mcp_yashan/runtime/` (JAR 文件包含在包内)
- 根目录文件大幅减少，更加清晰

### 移除内置 JRE
- 用户需要自行安装 Java 8+ (JRE 或 JDK)
- 项目体积从 215MB 降至 1.5MB（减少 99.3%）
- 安装说明：
  - macOS: `brew install openjdk@17`
  - Ubuntu: `sudo apt install openjdk-17-jre`
  - CentOS: `sudo yum install java-17-openjdk`

### 导入路径更新
- 所有导入使用 `mcp_yashan` 包名
- 支持打包后的环境

---

## 🐛 修复

- 超时异常处理改进
- Base64 解码容错
- 数值解析异常保护

---

## 🔒 安全性

- 输入验证防止恶意输入
- SQL 执行超时防止长时间阻塞
- 最大行数限制（1-10000）

---

## 📚 文档

- **PyPI**: https://pypi.org/project/mcp-yashan/
- **快速上手**: [docs/QUICK_START.md](./docs/QUICK_START.md)
- **STDIO 模式**: [docs/STDIO_MODE.md](./docs/STDIO_MODE.md)
- **HTTP 模式**: [docs/HTTP_MODE.md](./docs/HTTP_MODE.md)
- **贡献指南**: [CONTRIBUTING.md](./CONTRIBUTING.md)

---

## 📦 下载

- **Wheel 包**: `mcp_yashan-2.1.0-py3-none-any.whl` (555 KB)
- **源码包**: `mcp_yashan-2.1.0.tar.gz` (576 KB)

---

**完整变更日志**: https://github.com/willorn/mcp-yashan/compare/v2.0.0...v2.1.0
```

---

## 不需要提交的文件（已在 .gitignore）

这些是内部文档，不需要提交到 GitHub：
- `PROJECT_ASSESSMENT.md` - 项目评估（内部）
- `PYPI_PACKAGING_ANALYSIS.md` - 打包分析（内部）
- `PYPI_PACKAGING_COMPLETE.md` - 打包完成报告（内部）
- `READY_TO_PUBLISH.md` - 准备发布（内部）
- `PUBLISHED_SUCCESS.md` - 发布成功（内部）
- `FINAL_CHECKLIST.md` - 检查清单（内部）
- `NEXT_STEPS.md` - 下一步（内部）

这些文件对开发过程有用，但对用户没有价值，所以不提交。
