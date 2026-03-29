#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用 JayDeBeApi + JDBC 驱动连接崖山数据库 - ***REMOVED***
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

    print(f"\nJVM Lib: {jvm_lib}")
    print(f"JDBC 驱动: {jdbc_driver}")
    print("\n正在连接 ***REMOVED***:1688 ...")

    # 崖山数据库 JDBC URL
    jdbc_url = "jdbc:yasdb://***REMOVED***:1688/yashandb?failover=on&failoverType=session&failoverMethod=basic&failoverRetries=5&failoverDelay=1"

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
            ["***REMOVED***", "***REMOVED***"],
            jdbc_driver
        )

        print("✅ JDBC 连接成功！\n")

        cursor = conn.cursor()

        # 测试简单查询
        cursor.execute("SELECT 1 AS ID FROM DUAL")
        result = cursor.fetchone()[0]
        print(f"SELECT 1 结果: {result}")

        # 表列表 - 使用 Oracle 兼容语法
        cursor.execute("""
            SELECT TABLE_NAME
            FROM USER_TABLES
            WHERE ROWNUM <= 10
        """)
        tables = cursor.fetchall()
        print(f"\n表列表（前 10 张）：")
        for t in tables:
            print(f"  - {t[0]}")

        cursor.close()
        conn.close()
        jpype.shutdownJVM()
        print("\n✅ 测试通过！")
    except Exception as e:
        print(f"\n❌ 错误: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        try:
            jpype.shutdownJVM()
        except:
            pass

if __name__ == "__main__":
    main()
