#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用 JayDeBeApi + JDBC 驱动连接崖山数据库 - 测试脚本

请修改下面的数据库连接信息后再运行
"""
import jaydebeapi
import os
import jpype

def main():
    print("=" * 50)
    print("崖山数据库连接测试 - JDBC 方式")
    print("=" * 50)

    jdbc_driver = "/Users/tianyi/devproj/mcp-yashan/yashandb-jdbc-1.7.19-21.jar"

    if not os.path.exists(jdbc_driver):
        print(f"❌ JDBC 驱动文件不存在: {jdbc_driver}")
        return

    # 使用 GraalVM 的 libjvm.dylib 完整路径
    jvm_lib = "/Users/tianyi/Library/Java/JavaVirtualMachines/graalvm-jdk-21.0.7/Contents/Home/lib/server/libjvm.dylib"

    # ===== 请修改以下数据库连接信息 =====
    DB_HOST = "your_host"
    DB_PORT = "1688"
    DB_NAME = "yashandb"
    DB_USER = "your_username"
    DB_PASSWORD = "your_password"
    # ===================================

    jdbc_url = f"jdbc:yasdb://{DB_HOST}:{DB_PORT}/{DB_NAME}?failover=on&failoverType=session&failoverMethod=basic&failoverRetries=5&failoverDelay=1"

    print(f"\nJVM Lib: {jvm_lib}")
    print(f"JDBC 驱动: {jdbc_driver}")
    print(f"\n正在连接 {DB_HOST}:{DB_PORT} ...")

    try:
        # 先启动 JVM
        if not jpype.isJVMStarted():
            jpype.startJVM(
                jvm_lib,
                "-Djava.class.path=" + jdbc_driver,
                ignoreUnrecognized=True
            )
            print("✅ JVM 启动成功")

        conn = jaydebeapi.connect(
            "com.yashandb.jdbc.Driver",
            jdbc_url,
            [DB_USER, DB_PASSWORD],
            jdbc_driver
        )

        print("✅ JDBC 连接成功！\n")

        cursor = conn.cursor()
        cursor.execute("SELECT USER FROM DUAL")
        result = cursor.fetchone()
        print(f"当前用户: {result[0]}")

        cursor.close()
        conn.close()
        print("\n✅ 连接测试完成")

    except Exception as e:
        print(f"\n❌ 连接失败: {e}")

if __name__ == "__main__":
    main()
