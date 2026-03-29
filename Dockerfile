# 崖山数据库 MCP Server Dockerfile
FROM python:3.12-slim

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用文件
COPY yashandb-jdbc-1.7.19-21.jar /app/
COPY yashan_mcp_server.py /app/

# 设置环境变量（请通过 .env 文件或运行时传入）
# ENV DB_HOST=your_host
# ENV DB_PORT=1688
# ENV DB_USER=your_username
# ENV DB_PASSWORD=your_password
# ENV DB_NAME=yashandb
ENV JVM_LIB=/usr/lib/jvm/default-java/lib/server/libjvm.so

# 暴露端口（MCP SSE 模式）
EXPOSE 8080

# 启动命令
CMD ["python", "-u", "yashan_mcp_server.py"]
