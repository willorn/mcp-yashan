# HTTP 模式使用指南

## 概述

HTTP 模式提供常驻的 HTTP 服务，适合远程访问和多用户场景。

### 优势

- ✅ **远程访问**：局域网或互联网访问
- ✅ **多用户共享**：多个客户端同时连接
- ✅ **无启动开销**：服务常驻，响应更快
- ✅ **健康检查**：提供 `/healthz` 端点

### 对比 STDIO 模式

| 特性 | HTTP 模式 | STDIO 模式 |
|------|----------|-----------|
| 启动方式 | 常驻服务 | 按需启动 |
| 资源占用 | 中（持续运行） | 低（用完即退） |
| 适用场景 | 远程访问、多用户 | 本地 AI 工具 |
| 配置复杂度 | 中等 | 简单 |
| 网络暴露 | 有（需配置防火墙） | 无 |

---

## 快速开始

### 1. 配置数据库连接

```bash
cp .env.example .env
```

编辑 `.env`：

```env
DB_HOST=localhost
DB_PORT=1688
DB_NAME=yashandb
DB_USER=your_username
DB_PASSWORD=your_password
```

### 2. 启动服务

```bash
# 使用启动脚本（推荐）
./start.sh

# 或直接运行
python3 server.py --host 0.0.0.0 --port 20302
```

### 3. 验证服务

```bash
# 健康检查
curl http://localhost:20302/healthz

# 预期返回
{"ok":true,"service":"yashan-mcp-server","version":"2.1.0","protocols":["sse","streamable-http"]}
```

---

## 服务端点

### 1. MCP 端点（推荐）

**URL**: `http://localhost:20302/mcp`  
**协议**: Streamable HTTP  
**方法**: POST

### 2. SSE 端点（旧版）

**URL**: `http://localhost:20302/sse`  
**协议**: Server-Sent Events  
**方法**: GET

### 3. 健康检查

**URL**: `http://localhost:20302/healthz`  
**方法**: GET

---

## 远程访问配置

### 局域网访问

服务启动后会自动显示局域网 IP：

```
局域网可访问地址：
  MCP: http://192.168.1.100:20302/mcp
  SSE: http://192.168.1.100:20302/sse
```

### 客户端配置

在另一台机器的 MCP 客户端配置：

```json
{
  "mcpServers": {
    "yashan": {
      "type": "streamable-http",
      "url": "http://192.168.1.100:20302/mcp"
    }
  }
}
```

---

## 命令行参数

```bash
python3 server.py [OPTIONS]

选项：
  --host HOST    监听地址，默认 0.0.0.0
  --port PORT    监听端口，默认 20302
```

### 示例

```bash
# 仅本地访问
python3 server.py --host 127.0.0.1 --port 20302

# 局域网访问
python3 server.py --host 0.0.0.0 --port 20302

# 自定义端口
python3 server.py --host 0.0.0.0 --port 8080
```

---

## 日志

### 日志位置

`logs/yashan_mcp_YYYY-MM-DD.log`（按天滚动）

### 查看日志

```bash
# 实时查看
tail -f logs/yashan_mcp_$(date +%Y-%m-%d).log

# 查看最近 100 行
tail -n 100 logs/yashan_mcp_$(date +%Y-%m-%d).log

# 搜索错误
grep ERROR logs/yashan_mcp_*.log
```

### 日志级别

在 `.env` 中配置：

```bash
# DEBUG, INFO, WARNING, ERROR
LOG_LEVEL=INFO
```

---

## 进程管理

### 后台运行

```bash
# 使用 nohup
nohup python3 server.py --host 0.0.0.0 --port 20302 > /dev/null 2>&1 &

# 查看进程
ps aux | grep server.py

# 停止服务
kill <PID>
```

### 使用 systemd（Linux）

创建 `/etc/systemd/system/yashan-mcp.service`：

```ini
[Unit]
Description=Yashan MCP Server
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/mcp-yashan
Environment="PATH=/usr/bin:/usr/local/bin"
ExecStart=/usr/bin/python3 /path/to/mcp-yashan/server.py --host 0.0.0.0 --port 20302
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable yashan-mcp
sudo systemctl start yashan-mcp
sudo systemctl status yashan-mcp
```

### 使用 launchd（macOS）

创建 `~/Library/LaunchAgents/com.yashan.mcp.plist`：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.yashan.mcp</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/python3</string>
        <string>/path/to/mcp-yashan/server.py</string>
        <string>--host</string>
        <string>0.0.0.0</string>
        <string>--port</string>
        <string>20302</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/path/to/mcp-yashan</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/yashan-mcp.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/yashan-mcp.error.log</string>
</dict>
</plist>
```

加载服务：

```bash
launchctl load ~/Library/LaunchAgents/com.yashan.mcp.plist
launchctl start com.yashan.mcp
launchctl list | grep yashan
```

---

## 安全配置

### 1. 防火墙配置

```bash
# Linux (ufw)
sudo ufw allow 20302/tcp

# macOS
# 系统偏好设置 -> 安全性与隐私 -> 防火墙 -> 防火墙选项
# 添加 Python 到允许列表
```

### 2. 仅局域网访问

```bash
# 绑定到局域网 IP
python3 server.py --host 192.168.1.100 --port 20302
```

### 3. 反向代理（Nginx）

```nginx
server {
    listen 80;
    server_name yashan-mcp.example.com;

    location / {
        proxy_pass http://127.0.0.1:20302;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 4. HTTPS 配置

使用 Nginx + Let's Encrypt：

```bash
# 安装 certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d yashan-mcp.example.com
```

---

## 性能优化

### 1. 调整超时时间

```bash
# .env
SQL_TIMEOUT=120
```

### 2. 限制并发连接

修改 `server.py`：

```python
# 使用 uvicorn 的 limit_concurrency 参数
uvicorn.run(app, host=args.host, port=args.port, limit_concurrency=10)
```

### 3. 启用 gzip 压缩

修改 `server.py`：

```python
from starlette.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)
```

---

## 监控

### 健康检查

```bash
# 定期检查服务状态
*/5 * * * * curl -f http://localhost:20302/healthz || systemctl restart yashan-mcp
```

### 日志监控

```bash
# 监控错误日志
tail -f logs/yashan_mcp_*.log | grep ERROR
```

### 性能监控

```bash
# 查看进程资源占用
ps aux | grep server.py

# 查看端口连接数
netstat -an | grep 20302 | wc -l
```

---

## 故障排查

### 问题 1：端口被占用

**错误**：`Address already in use`

**解决**：
```bash
# 查找占用端口的进程
lsof -i :20302

# 杀死进程
kill <PID>

# 或使用其他端口
python3 server.py --port 20303
```

### 问题 2：无法远程访问

**检查**：
1. 防火墙是否开放端口
2. 服务是否绑定到 `0.0.0.0`
3. 网络是否可达

```bash
# 测试端口连通性
telnet 192.168.1.100 20302

# 查看监听地址
netstat -an | grep 20302
```

### 问题 3：服务频繁重启

**检查日志**：
```bash
tail -f logs/yashan_mcp_*.log
```

**常见原因**：
- 数据库连接失败
- 配置文件错误
- 内存不足

---

## 与 STDIO 模式对比

### 何时使用 HTTP 模式

- ✅ 需要远程访问
- ✅ 多用户共享
- ✅ 高频查询（> 100 次/分钟）
- ✅ 需要 Web UI

### 何时使用 STDIO 模式

- ✅ 本地开发和使用
- ✅ 集成到 AI 工具
- ✅ 不需要远程访问
- ✅ 希望节省资源

详见 [STDIO 模式文档](./STDIO_MODE.md)

---

## 常见问题

### Q: HTTP 模式是否更快？

A: 是的。HTTP 模式常驻，无启动开销，响应更快。但会持续占用资源。

### Q: 如何保证安全？

A: 建议使用反向代理 + HTTPS，并配置防火墙限制访问。

### Q: 支持多少并发连接？

A: 默认无限制，建议根据服务器配置设置 `limit_concurrency`。

### Q: 如何实现高可用？

A: 使用 Nginx 负载均衡 + 多个服务实例。

---

## 总结

HTTP 模式适合需要远程访问或高频查询的场景。如果只是本地使用，推荐使用 [STDIO 模式](./STDIO_MODE.md)。
