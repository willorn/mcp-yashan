#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用 JayDeBeApi + JDBC 驱动连接崖山数据库 - 测试脚本

请修改下面的数据库连接信息后再运行
"""
import os
from pathlib import Path

import jaydebeapi
import jpype


def main():
    print("=" * 50)
    print("崖山数据库连接测试 - JDBC 方式")
    print("=" * 50)

    project_root = Path(__file__).resolve().parent.parent
    jdbc_driver = project_root / "yashandb-jdbc-1.9.3.jar"

    if not jdbc_driver.exists():
        print(f"❌ JDBC 驱动文件不存在: {jdbc_driver}")
        return

    jvm_candidates = [
        project_root / "runtime" / "jre" / "lib" / "server" / "libjvm.dylib",
        project_root / "runtime" / "jre" / "lib" / "server" / "libjvm.so",
        project_root / "runtime" / "jre" / "bin" / "server" / "jvm.dll",
    ]
    jvm_lib = next((path for path in jvm_candidates if path.exists()), None)
    if jvm_lib is None:
        print("❌ 未找到内置 JVM，请先准备 runtime/jre")
        return

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
                os.fspath(jvm_lib),
                "-Djava.class.path=" + os.fspath(jdbc_driver),
                ignoreUnrecognized=True
            )
            print("✅ JVM 启动成功")

        conn = jaydebeapi.connect(
            "com.yashandb.jdbc.Driver",
            jdbc_url,
            [DB_USER, DB_PASSWORD],
            os.fspath(jdbc_driver)
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
