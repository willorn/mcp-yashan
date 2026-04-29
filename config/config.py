# -*- coding: utf-8 -*-
"""
崖山数据库 MCP Server 配置文件示例

请复制此文件为 config_local.py 并填入实际配置
不要提交包含真实密码的配置文件到 GitHub
"""

# 数据库连接配置示例
DATABASE_CONFIG = {
    "driver_class": "com.yashandb.jdbc.Driver",
    "jdbc_url": "jdbc:yasdb://your_host:1688/yashandb",
    "username": "your_username",
    "password": "your_password",  # 请修改为实际密码
    # JVM 路径，根据你的系统修改
    # macOS: /Library/Java/JavaVirtualMachines/xxx/Contents/Home/lib/server/libjvm.dylib
    # Linux: /usr/lib/jvm/java-17-openjdk/lib/server/libjvm.so
    # Windows: C:\Program Files\Java\jdk-17\bin\server\jvm.dll
    "jvm_lib": "",  # 自动检测
}
