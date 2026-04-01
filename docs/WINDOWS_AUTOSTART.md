# Windows 开机自动启动配置

本文档介绍如何在 Windows 系统上配置崖山 MCP Server 开机自动启动。

## 方法：任务计划程序（推荐）

使用 Windows 内置的任务计划程序，无需额外安装软件。

### 一键配置

1. **以管理员身份打开 PowerShell**
   - 右键点击 PowerShell → "以管理员身份运行"

2. **进入项目目录并运行脚本**
   ```powershell
   cd C:\Users\coden\mcp2\yashan\mcp-yashan
   .\create_autostart_task.ps1
   ```

3. **完成！** 下次登录 Windows 时会自动启动服务。

### 手动配置（可选）

如果脚本无法运行，可手动创建任务：

1. 按 `Win + R`，输入 `taskschd.msc` 打开任务计划程序
2. 点击右侧"创建任务"
3. **常规**选项卡：
   - 名称：`YashanMcpServer`
   - 勾选"使用最高权限运行"
4. **触发器**选项卡：
   - 新建 → 开始任务："登录时"
5. **操作**选项卡：
   - 新建 → 操作："启动程序"
   - 程序：`python`（或 python 的完整路径）
   - 参数：`server.py --host 0.0.0.0 --port 20302`
   - 起始于：`C:\Users\coden\mcp2\yashan\mcp-yashan`
6. 点击确定保存

### 管理任务

```powershell
# 查看任务状态
Get-ScheduledTask YashanMcpServer

# 手动启动
Start-ScheduledTask YashanMcpServer

# 停止任务
Stop-ScheduledTask YashanMcpServer

# 删除任务
Unregister-ScheduledTask YashanMcpServer -Confirm:$false
```

### 验证服务

任务运行后，访问以下地址验证：

- 健康检查：http://localhost:20302/healthz
- MCP 端点：http://localhost:20302/mcp
- SSE 端点：http://localhost:20302/sse

### 局域网访问

其他机器访问时，使用服务器 IP 地址：

```json
{
  "mcpServers": {
    "yashan-db": {
      "url": "http://192.168.1.100:20302/mcp"
    }
  }
}
```

**注意：**
- 将 `192.168.1.100` 替换为服务器的实际 IP
- 确保防火墙允许 20302 端口

### 故障排除

**任务无法启动？**
- 检查 Python 是否已添加到 PATH
- 查看任务历史记录：`taskschd.msc` → 找到任务 → 右侧"查看历史记录"

**端口被占用？**
- 修改脚本中的端口号（如 28080）
- 或修改 `create_autostart_task.ps1` 中的 `$Port` 变量

**服务无法访问？**
- 检查防火墙设置
- 确保 `--host 0.0.0.0` 参数已设置（允许远程访问）
