#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
配置向导 - 交互式配置助手
"""

import os
import sys
from pathlib import Path


def check_java() -> bool:
    """检查 Java 是否可用"""
    import shutil
    java_cmd = shutil.which("java")
    if java_cmd:
        try:
            import subprocess
            result = subprocess.run(
                [java_cmd, "-version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False
    return False


def check_config() -> tuple[bool, dict]:
    """检查配置是否完整"""
    required = ["DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD"]
    config = {}
    missing = []
    
    for key in required:
        value = os.getenv(key, "").strip()
        if value:
            config[key] = value
        else:
            missing.append(key)
    
    return len(missing) == 0, config


def create_config_file(config: dict, path: Path) -> bool:
    """创建配置文件"""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        
        content = """# mcp-yashan 配置文件
# 由配置向导自动生成

# 数据库连接配置
DB_HOST={host}
DB_PORT={port}
DB_NAME={db_name}
DB_USER={user}
DB_PASSWORD={password}

# 可选配置
SQL_TIMEOUT=60

# Java 配置（如果需要指定）
# JAVA_HOME=/path/to/java
""".format(
            host=config.get("DB_HOST", "localhost"),
            port=config.get("DB_PORT", "1688"),
            db_name=config.get("DB_NAME", "yashandb"),
            user=config.get("DB_USER", ""),
            password=config.get("DB_PASSWORD", "")
        )
        
        path.write_text(content, encoding="utf-8")
        return True
    except Exception as e:
        print(f"❌ 创建配置文件失败: {e}")
        return False


def run_wizard(silent: bool = False) -> bool:
    """运行配置向导"""
    if silent:
        return False
    
    print("\n" + "=" * 60)
    print("🔧 mcp-yashan 配置向导")
    print("=" * 60)
    
    # 1. 检查 Java
    print("\n[1/3] 检查 Java 环境...")
    if check_java():
        print("✅ Java 已安装")
    else:
        print("❌ 未检测到 Java")
        print("\n请先安装 Java 8 或更高版本：")
        print("  - macOS:   brew install openjdk@17")
        print("  - Ubuntu:  sudo apt install openjdk-17-jre")
        print("  - CentOS:  sudo yum install java-17-openjdk")
        print("  - Windows: https://adoptium.net/")
        print("\n安装后请重新运行。")
        return False
    
    # 2. 检查配置
    print("\n[2/3] 检查数据库配置...")
    has_config, existing_config = check_config()
    
    if has_config:
        print("✅ 配置已存在")
        print(f"   主机: {existing_config['DB_HOST']}")
        print(f"   端口: {existing_config['DB_PORT']}")
        print(f"   数据库: {existing_config['DB_NAME']}")
        print(f"   用户: {existing_config['DB_USER']}")
        return True
    
    print("⚠️  配置不完整，需要设置数据库连接信息")
    
    # 3. 交互式配置
    print("\n[3/3] 配置数据库连接")
    print("-" * 60)
    
    try:
        config = {}
        
        # 数据库主机
        default_host = "localhost"
        host = input(f"数据库主机 [{default_host}]: ").strip()
        config["DB_HOST"] = host if host else default_host
        
        # 数据库端口
        default_port = "1688"
        port = input(f"数据库端口 [{default_port}]: ").strip()
        config["DB_PORT"] = port if port else default_port
        
        # 数据库名称
        default_db = "yashandb"
        db_name = input(f"数据库名称 [{default_db}]: ").strip()
        config["DB_NAME"] = db_name if db_name else default_db
        
        # 用户名
        user = input("数据库用户名: ").strip()
        if not user:
            print("❌ 用户名不能为空")
            return False
        config["DB_USER"] = user
        
        # 密码
        import getpass
        password = getpass.getpass("数据库密码: ").strip()
        if not password:
            print("❌ 密码不能为空")
            return False
        config["DB_PASSWORD"] = password
        
        # 4. 选择保存位置
        print("\n配置文件保存位置：")
        print("  1. 当前目录 (.env)")
        print("  2. 用户主目录 (~/.mcp_yashan/.env) [推荐]")
        
        choice = input("\n请选择 [2]: ").strip()
        
        if choice == "1":
            config_path = Path.cwd() / ".env"
        else:
            config_path = Path.home() / ".mcp_yashan" / ".env"
        
        # 5. 保存配置
        print(f"\n保存配置到: {config_path}")
        if create_config_file(config, config_path):
            print("✅ 配置保存成功！")
            print("\n" + "=" * 60)
            print("🎉 配置完成！现在可以使用 mcp-yashan 了")
            print("=" * 60)
            
            # 设置环境变量（当前会话）
            for key, value in config.items():
                os.environ[key] = value
            
            return True
        else:
            return False
            
    except KeyboardInterrupt:
        print("\n\n❌ 配置已取消")
        return False
    except Exception as e:
        print(f"\n❌ 配置失败: {e}")
        return False


def check_and_prompt() -> bool:
    """检查配置，如果缺失则提示用户"""
    # 检查 Java
    if not check_java():
        print("\n" + "=" * 60)
        print("❌ 错误: 未检测到 Java 环境")
        print("=" * 60)
        print("\nmcp-yashan 需要 Java 8 或更高版本才能运行。")
        print("\n安装方法：")
        print("  - macOS:   brew install openjdk@17")
        print("  - Ubuntu:  sudo apt install openjdk-17-jre")
        print("  - CentOS:  sudo yum install java-17-openjdk")
        print("  - Windows: https://adoptium.net/")
        print("\n安装后请重新运行。")
        return False
    
    # 检查配置
    has_config, config = check_config()
    if not has_config:
        print("\n" + "=" * 60)
        print("⚠️  警告: 数据库配置不完整")
        print("=" * 60)
        print("\nmcp-yashan 需要数据库连接信息才能工作。")
        print("\n你可以：")
        print("  1. 运行配置向导: mcp-yashan --configure")
        print("  2. 手动创建 .env 文件")
        print("  3. 在 MCP 配置中设置环境变量")
        print("\n详细说明: https://github.com/willorn/mcp-yashan")
        
        # 询问是否运行配置向导
        if sys.stdin.isatty():  # 只在交互式终端中询问
            print("\n是否现在运行配置向导? (y/n) ", end="", flush=True)
            try:
                answer = input().strip().lower()
                if answer in ["y", "yes", "是"]:
                    return run_wizard(silent=False)
            except (KeyboardInterrupt, EOFError):
                print("\n")
        
        return False
    
    return True


if __name__ == "__main__":
    # 直接运行配置向导
    success = run_wizard(silent=False)
    sys.exit(0 if success else 1)
