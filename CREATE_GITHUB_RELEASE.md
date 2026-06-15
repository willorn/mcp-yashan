# 创建 GitHub Release 指南

## ✅ 已完成的步骤

1. ✅ 代码已提交到 GitHub
2. ✅ Tag v2.1.0 已创建并推送
3. ✅ 构建产物已准备好

## 📦 需要上传的文件

在 `dist/` 目录下：
- `mcp_yashan-2.1.0-py3-none-any.whl` (555 KB)
- `mcp_yashan-2.1.0.tar.gz` (576 KB)

## 🚀 创建 Release 步骤

### 1. 访问 GitHub Release 页面

打开浏览器，访问：
```
https://github.com/willorn/mcp-yashan/releases/new
```

### 2. 选择 Tag

- **Choose a tag**: 从下拉菜单选择 `v2.1.0`（已经存在）

### 3. 填写 Release 信息

- **Release title**: 
  ```
  v2.1.0 - PyPI 打包支持
  ```

- **Description**: 复制下面的内容

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

### 4. 上传构建产物

在页面底部的 "Attach binaries by dropping them here or selecting them." 区域：

1. 点击或拖拽上传 `dist/mcp_yashan-2.1.0-py3-none-any.whl`
2. 点击或拖拽上传 `dist/mcp_yashan-2.1.0.tar.gz`

### 5. 发布

- 确认所有信息无误
- 点击 **"Publish release"** 按钮

## ✅ 完成后

Release 将出现在：
```
https://github.com/willorn/mcp-yashan/releases
```

用户可以：
- 查看 Release 说明
- 下载构建产物
- 通过 PyPI 安装：`pip install mcp-yashan`

## 📝 注意事项

- Release 一旦发布，tag 就不能修改（但可以编辑 Release 描述）
- 构建产物会永久保存在 GitHub
- PyPI 上的包已经发布，用户可以直接安装
