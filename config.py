# -*- coding: utf-8 -*-
"""
崖山数据库 MCP Server 配置文件

将敏感信息放在这里，不要提交到 GitHub
"""

# 数据库连接配置
# 请修改为你的实际数据库配置
DATABASE_CONFIG = {
    "driver_class": "com.yashandb.jdbc.Driver",
    "jdbc_url": "jdbc:yasdb://***REMOVED***:1688/yashandb?failover=on&failoverType=session&failoverMethod=basic&failoverRetries=5&failoverDelay=1",
    "username": "***REMOVED***",
    "password": "***REMOVED***",
    # JVM 路径，根据你的系统修改
    # macOS: /Library/Java/JavaVirtualMachines/xxx/Contents/Home/lib/server/libjvm.dylib
    # Linux: /usr/lib/jvm/java-17-openjdk/lib/server/libjvm.so
    # Windows: C:\Program Files\Java\jdk-17\bin\server\jvm.dll
    "jvm_lib": "",  # 自动检测
}
