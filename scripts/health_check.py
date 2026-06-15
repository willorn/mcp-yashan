#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mcp-yashan 健康检查脚本
一键检查环境、依赖和配置是否正确
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path


class HealthChecker:
    """健康检查器"""

    def __init__(self):
        self.issues = []
        self.warnings = []

    def check_all(self) -> bool:
        """运行所有检查"""
        print("=" * 70)
        print("🏥 mcp-yashan 健康检查")
        print("=" * 70)

        checks = [
            ("Python 版本", self.check_python),
            ("Java 环境", self.check_java),
            ("Python 依赖", self.check_python_deps),
            ("JDBC 驱动", self.check_jdbc_driver),
            ("数据库配置", self.check_config),
            ("数据库连接", self.check_db_connection),
        ]

        for name, check_func in checks:
            print(f"\n[检查] {name}...")
            try:
                check_func()
            except Exception as e:
                self.issues.append(f"{name}: {str(e)}")
                print(f"   ❌ 错误: {e}")

        # 汇总结果
        print("\n" + "=" * 70)
        print("📊 检查结果")
        print("=" * 70)

        if not self.issues and not self.warnings:
            print("\n✅ 所有检查通过！系统健康，可以正常使用。")
            return True

        if self.warnings:
            print(f"\n⚠️  发现 {len(self.warnings)} 个警告：")
            for i, warning in enumerate(self.warnings, 1):
                print(f"   {i}. {warning}")

        if self.issues:
            print(f"\n❌ 发现 {len(self.issues)} 个问题：")
            for i, issue in enumerate(self.issues, 1):
                print(f"   {i}. {issue}")

            print("\n💡 建议：")
            print("   - 查看上方的详细错误信息")
            print("   - 运行配置向导: mcp-yashan --configure")
            print("   - 查看文档: https://github.com/willorn/mcp-yashan")

            return False

        return True

    def check_python(self):
        """检查 Python 版本"""
        version = sys.version_info
        if version < (3, 10):
            self.issues.append(f"Python 版本过低 ({version.major}.{version.minor}，需要 3.10+)")
            print(f"   ❌ Python {version.major}.{version.minor} (需要 3.10+)")
        else:
            print(f"   ✅ Python {version.major}.{version.minor}")

    def check_java(self):
        """检查 Java 环境"""
        java_cmd = shutil.which("java")

        if not java_cmd:
            self.issues.append("未找到 Java，请安装 Java 8+")
            print("   ❌ Java 未安装")
            print("      安装方法：")
            print("        - macOS:   brew install openjdk@17")
            print("        - Ubuntu:  sudo apt install openjdk-17-jre")
            print("        - CentOS:  sudo yum install java-17-openjdk")
            print("        - Windows: https://adoptium.net/")
            return

        try:
            result = subprocess.run(
                [java_cmd, "-version"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                # 解析版本号
                version_text = result.stderr if result.stderr else result.stdout
                print(f"   ✅ Java 已安装")
                for line in version_text.split('\n'):
                    if 'version' in line.lower():
                        print(f"      {line.strip()}")
                        break
            else:
                self.issues.append("Java 命令执行失败")
                print("   ❌ Java 命令执行失败")

        except subprocess.TimeoutExpired:
            self.issues.append("Java 命令超时")
            print("   ❌ Java 命令超时")
        except Exception as e:
            self.issues.append(f"Java 检查出错: {e}")
            print(f"   ❌ 检查出错: {e}")

    def check_python_deps(self):
        """检查 Python 依赖"""
        requirements_file = Path("requirements.txt")

        if not requirements_file.exists():
            self.warnings.append("requirements.txt 不存在")
            print("   ⚠️  requirements.txt 不存在")
            return

        try:
            required_packages = []
            for line in requirements_file.read_text().splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    # 提取包名（去掉版本号）
                    pkg = line.split(">=")[0].split("==")[0].split("<")[0].strip()
                    required_packages.append(pkg)

            missing = []
            for pkg in required_packages:
                try:
                    __import__(pkg.replace("-", "_"))
                except ImportError:
                    missing.append(pkg)

            if missing:
                self.issues.append(f"缺少依赖: {', '.join(missing)}")
                print(f"   ❌ 缺少依赖: {', '.join(missing)}")
                print(f"      安装命令: pip install -r requirements.txt")
            else:
                print(f"   ✅ 所有依赖已安装 ({len(required_packages)} 个)")

        except Exception as e:
            self.warnings.append(f"依赖检查出错: {e}")
            print(f"   ⚠️  检查出错: {e}")

    def check_jdbc_driver(self):
        """检查 JDBC 驱动文件"""
        # 尝试查找 JDBC 驱动
        possible_paths = [
            Path("mcp_yashan/runtime/yashandb-jdbc-1.9.3.jar"),
            Path("runtime/yashandb-jdbc-1.9.3.jar"),
        ]

        helper_paths = [
            Path("mcp_yashan/runtime/java/yashan-mcp-helper.jar"),
            Path("runtime/java/yashan-mcp-helper.jar"),
        ]

        jdbc_found = any(p.exists() for p in possible_paths)
        helper_found = any(p.exists() for p in helper_paths)

        if not jdbc_found:
            self.issues.append("JDBC 驱动文件不存在")
            print("   ❌ JDBC 驱动文件不存在 (yashandb-jdbc-1.9.3.jar)")
        else:
            print("   ✅ JDBC 驱动文件存在")

        if not helper_found:
            self.issues.append("Java Helper 文件不存在")
            print("   ❌ Java Helper 文件不存在 (yashan-mcp-helper.jar)")
        else:
            print("   ✅ Java Helper 文件存在")

    def check_config(self):
        """检查数据库配置"""
        # 加载 .env 文件
        env_paths = [
            Path(".env"),
            Path.home() / ".mcp_yashan" / ".env",
        ]

        env_found = False
        for env_path in env_paths:
            if env_path.exists():
                env_found = True
                print(f"   ℹ️  找到配置文件: {env_path}")
                for line in env_path.read_text(encoding="utf-8").splitlines():
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        os.environ.setdefault(key.strip(), value.strip())
                break

        if not env_found:
            self.warnings.append("未找到 .env 配置文件")
            print("   ⚠️  未找到 .env 配置文件")

        # 检查必需的环境变量
        required = ["DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD"]
        missing = []

        for key in required:
            value = os.getenv(key, "").strip()
            if not value:
                missing.append(key)

        if missing:
            self.issues.append(f"缺少配置: {', '.join(missing)}")
            print(f"   ❌ 缺少配置: {', '.join(missing)}")
            print(f"      运行配置向导: mcp-yashan --configure")
        else:
            print("   ✅ 数据库配置完整")
            print(f"      主机: {os.getenv('DB_HOST')}")
            print(f"      端口: {os.getenv('DB_PORT')}")
            print(f"      数据库: {os.getenv('DB_NAME')}")
            print(f"      用户: {os.getenv('DB_USER')}")

    def check_db_connection(self):
        """检查数据库连接"""
        # 检查配置是否完整
        required = ["DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD"]
        if not all(os.getenv(key, "").strip() for key in required):
            print("   ⏭️  跳过（配置不完整）")
            return

        java_cmd = shutil.which("java")
        if not java_cmd:
            print("   ⏭️  跳过（Java 未安装）")
            return

        print("   🔄 正在测试连接...")

        try:
            # 尝试导入执行器
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from mcp_yashan.core.executor import get_executor

            executor = get_executor()
            result = executor.execute("SELECT 1 FROM DUAL", max_rows=1)

            if result.get("success"):
                exec_time = result.get("execution_time", 0)
                print(f"   ✅ 数据库连接成功 (耗时: {exec_time:.2f}s)")
            else:
                error = result.get("error", "未知错误")
                self.issues.append(f"数据库连接失败: {error}")
                print(f"   ❌ 连接失败: {error}")

        except Exception as e:
            self.issues.append(f"连接测试出错: {e}")
            print(f"   ❌ 测试出错: {e}")


def main():
    """主函数"""
    checker = HealthChecker()
    success = checker.check_all()

    print("\n" + "=" * 70 + "\n")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
