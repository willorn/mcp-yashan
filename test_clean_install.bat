@echo off
REM 干净环境测试脚本 - Windows 版本
REM 模拟在新 Windows 电脑上安装和测试 mcp-yashan v2.1.1

setlocal enabledelayedexpansion

echo ==========================================
echo mcp-yashan v2.1.1 干净环境测试 (Windows)
echo ==========================================
echo.

set PASSED=0
set FAILED=0
set VENV_DIR=test_venv_clean

REM 1. 创建干净的虚拟环境
echo ==========================================
echo 步骤 1: 创建干净的虚拟环境
echo ==========================================

if exist "%VENV_DIR%" (
    echo 删除旧的测试环境...
    rmdir /s /q "%VENV_DIR%"
)

echo 创建新的虚拟环境...
python -m venv "%VENV_DIR%"

echo 激活虚拟环境...
call "%VENV_DIR%\Scripts\activate.bat"

echo [OK] 虚拟环境创建成功
python --version
pip --version

REM 2. 从本地 wheel 安装
echo.
echo ==========================================
echo 步骤 2: 从本地 wheel 安装 mcp-yashan
echo ==========================================

set WHEEL_FILE=dist\mcp_yashan-2.1.1-py3-none-any.whl

if not exist "%WHEEL_FILE%" (
    echo [ERROR] 找不到 wheel 文件: %WHEEL_FILE%
    exit /b 1
)

echo 安装 %WHEEL_FILE% ...
pip install "%WHEEL_FILE%" --quiet

echo [OK] 安装完成
pip show mcp-yashan

REM 3. 测试导入
echo.
echo ==========================================
echo 测试: 导入 mcp_yashan
echo ==========================================
python -c "import mcp_yashan; print('版本:', mcp_yashan.__version__)" && (
    echo [OK] 导入 mcp_yashan
    set /a PASSED+=1
) || (
    echo [FAIL] 导入 mcp_yashan
    set /a FAILED+=1
)

echo.
echo ==========================================
echo 测试: 导入 get_metadata (修复的关键)
echo ==========================================
python -c "from mcp_yashan.core import get_metadata, MetadataManager; print('[OK] get_metadata 导入成功')" && (
    echo [OK] 导入 get_metadata
    set /a PASSED+=1
) || (
    echo [FAIL] 导入 get_metadata
    set /a FAILED+=1
)

echo.
echo ==========================================
echo 测试: 导入 TOOLS
echo ==========================================
python -c "from mcp_yashan.core import TOOLS, handle_tool_call; print(f'[OK] {len(TOOLS)} 个工具可用')" && (
    echo [OK] 导入 TOOLS
    set /a PASSED+=1
) || (
    echo [FAIL] 导入 TOOLS
    set /a FAILED+=1
)

echo.
echo ==========================================
echo 测试: MetadataManager 实例化
echo ==========================================
python -c "from mcp_yashan.core import get_metadata, MetadataManager; m1 = MetadataManager(); m2 = get_metadata(); assert m1 is m2; print('[OK] MetadataManager 实例化成功，单例模式正常')" && (
    echo [OK] MetadataManager 实例化
    set /a PASSED+=1
) || (
    echo [FAIL] MetadataManager 实例化
    set /a FAILED+=1
)

echo.
echo ==========================================
echo 测试: 命令行工具
echo ==========================================
where mcp-yashan >nul 2>&1 && (
    echo [OK] mcp-yashan 命令可用
    set /a PASSED+=1
) || (
    echo [FAIL] mcp-yashan 命令不可用
    set /a FAILED+=1
)

where mcp-yashan-http >nul 2>&1 && (
    echo [OK] mcp-yashan-http 命令可用
    set /a PASSED+=1
) || (
    echo [FAIL] mcp-yashan-http 命令不可用
    set /a FAILED+=1
)

echo.
echo ==========================================
echo 测试: 检查 runtime JAR 文件
echo ==========================================
python -c "import os; import mcp_yashan; package_path = os.path.dirname(mcp_yashan.__file__); runtime_path = os.path.join(package_path, 'runtime'); jdbc_path = os.path.join(runtime_path, 'yashandb-jdbc-1.9.3.jar'); helper_path = os.path.join(runtime_path, 'java', 'yashan-mcp-helper.jar'); jdbc_exists = os.path.exists(jdbc_path); helper_exists = os.path.exists(helper_path); print(f'JDBC 驱动: {jdbc_path} - {\"存在\" if jdbc_exists else \"缺失\"}'); print(f'Helper JAR: {helper_path} - {\"存在\" if helper_exists else \"缺失\"}'); assert jdbc_exists and helper_exists, f'JAR 文件缺失: jdbc={jdbc_exists}, helper={helper_exists}'; print('[OK] JAR 文件完整')" && (
    echo [OK] 检查 runtime JAR 文件
    set /a PASSED+=1
) || (
    echo [FAIL] 检查 runtime JAR 文件
    set /a FAILED+=1
)

REM 运行完整测试脚本
if exist "test_v2.1.1.py" (
    echo.
    echo ==========================================
    echo 测试: 运行完整测试套件
    echo ==========================================
    python test_v2.1.1.py && (
        echo [OK] 完整测试套件通过
        set /a PASSED+=1
    ) || (
        echo [FAIL] 完整测试套件失败
        set /a FAILED+=1
    )
)

REM 清理
echo.
echo ==========================================
echo 清理测试环境
echo ==========================================
call deactivate 2>nul

echo 保留测试环境: %VENV_DIR%
echo 手动清理: rmdir /s /q %VENV_DIR%

REM 汇总结果
echo.
echo ==========================================
echo 测试结果汇总
echo ==========================================
echo 通过: %PASSED%
echo 失败: %FAILED%
set /a TOTAL=%PASSED%+%FAILED%
echo 总计: %TOTAL%
echo.

if %FAILED% equ 0 (
    echo [SUCCESS] 所有测试通过！v2.1.1 可以发布！
    exit /b 0
) else (
    echo [WARNING] 有 %FAILED% 个测试失败，需要修复
    exit /b 1
)
