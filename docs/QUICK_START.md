# Quick Start

这个文档面向“下载压缩包后马上开始使用”的场景。

## 1. 配置 `.env`

复制模板：

```bash
cp .env.example .env
```

编辑 `.env`：

```env
DB_HOST=your_database_host
DB_PORT=1688
DB_NAME=yashandb
DB_USER=your_username
DB_PASSWORD=your_password
```

如果你已经有完整 JDBC 连接串，也可以直接配置：

```env
DB_JDBC_URL=jdbc:yasdb://host:port/dbname?param=value
```

## 2. 安装 Python 依赖

```bash
python3 -m pip install -r requirements.txt
```

说明：

- 普通使用场景下不需要额外安装 Java
- 服务会优先使用项目内置的 `runtime/jre/bin/java`

## 3. 启动服务

推荐：

```bash
./start.sh
```

或者：

```bash
python3 server.py --host 0.0.0.0 --port 20302
```

## 4. 启动成功后会看到什么

终端会打印：

- MCP 地址
- SSE 地址
- 健康检查地址
- 局域网 IP
- 另一台机器可参考的 MCP 配置 JSON

日志会写到：

```text
logs/yashan_mcp_YYYY-MM-DD.log
```

## 5. 另一台机器如何配置 MCP

如果另一台机器的 MCP 客户端支持 `streamable-http`，可参考：

```json
{
  "mcpServers": {
    "yashan": {
      "type": "streamable-http",
      "url": "http://你的服务IP:20302/mcp"
    }
  }
}
```

也可以先访问健康检查确认服务可达：

```text
http://你的服务IP:20302/healthz
```

## 6. 如果你要打包给别人

可以执行：

```bash
./scripts/package_release.sh
```

打包产物会放到 `release/` 目录。
