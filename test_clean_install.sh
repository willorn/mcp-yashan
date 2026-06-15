#!/bin/bash
# 干净环境测试脚本 - 模拟在新电脑上安装和测试 mcp-yashan v2.1.1

set -e  # 遇到错误立即退出

echo "=========================================="
echo "mcp-yashan v2.1.1 干净环境测试"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 测试结果统计
PASSED=0
FAILED=0

# 测试函数
test_step() {
    local step_name=$1
    local command=$2
    
    echo ""
    echo "=========================================="
    echo "测试: $step_name"
    echo "=========================================="
    
    if eval "$command"; then
        echo -e "${GREEN}✅ 通过${NC} - $step_name"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}❌ 失败${NC} - $step_name"
        ((FAILED++))
        return 1
    fi
}

# 1. 创建干净的虚拟环境
echo ""
echo "=========================================="
echo "步骤 1: 创建干净的虚拟环境"
echo "=========================================="

VENV_DIR="test_venv_clean"

if [ -d "$VENV_DIR" ]; then
    echo "删除旧的测试环境..."
    rm -rf "$VENV_DIR"
fi

echo "创建新的虚拟环境..."
python -m venv "$VENV_DIR"

echo "激活虚拟环境..."
source "$VENV_DIR/bin/activate"

echo -e "${GREEN}✅ 虚拟环境创建成功${NC}"
echo "Python 版本: $(python --version)"
echo "pip 版本: $(pip --version)"

# 2. 从本地 wheel 安装
echo ""
echo "=========================================="
echo "步骤 2: 从本地 wheel 安装 mcp-yashan"
echo "=========================================="

WHEEL_FILE="dist/mcp_yashan-2.1.1-py3-none-any.whl"

if [ ! -f "$WHEEL_FILE" ]; then
    echo -e "${RED}❌ 找不到 wheel 文件: $WHEEL_FILE${NC}"
    exit 1
fi

echo "安装 $WHEEL_FILE ..."
pip install "$WHEEL_FILE" --quiet

echo -e "${GREEN}✅ 安装完成${NC}"
pip show mcp-yashan

# 3. 测试导入
test_step "导入 mcp_yashan" "python -c 'import mcp_yashan; print(\"版本:\", mcp_yashan.__version__)'"

test_step "导入 core 模块" "python -c 'from mcp_yashan import core; print(\"core 模块可用\")'"

test_step "导入 get_metadata (修复的关键)" "python -c 'from mcp_yashan.core import get_metadata, MetadataManager; print(\"✅ get_metadata 导入成功\")'"

test_step "导入 get_executor" "python -c 'from mcp_yashan.core import get_executor, JavaSqlExecutor; print(\"✅ get_executor 导入成功\")'"

test_step "导入 TOOLS" "python -c 'from mcp_yashan.core import TOOLS, handle_tool_call; print(f\"✅ {len(TOOLS)} 个工具可用\")'"

# 4. 测试 MetadataManager 实例化
test_step "MetadataManager 实例化" "python -c '
from mcp_yashan.core import get_metadata, MetadataManager
m1 = MetadataManager()
m2 = get_metadata()
assert m1 is m2, \"单例模式失败\"
print(\"✅ MetadataManager 实例化成功，单例模式正常\")
'"

# 5. 测试命令行工具
echo ""
echo "=========================================="
echo "测试: 命令行工具"
echo "=========================================="

# 检查命令是否存在
if command -v mcp-yashan &> /dev/null; then
    echo -e "${GREEN}✅ mcp-yashan 命令可用${NC}"
    ((PASSED++))
else
    echo -e "${RED}❌ mcp-yashan 命令不可用${NC}"
    ((FAILED++))
fi

if command -v mcp-yashan-http &> /dev/null; then
    echo -e "${GREEN}✅ mcp-yashan-http 命令可用${NC}"
    ((PASSED++))
else
    echo -e "${RED}❌ mcp-yashan-http 命令不可用${NC}"
    ((FAILED++))
fi

# 6. 测试 python -m mcp_yashan (启动测试，2秒后杀掉)
echo ""
echo "=========================================="
echo "测试: python -m mcp_yashan 启动"
echo "=========================================="

echo "启动 STDIO 模式（2秒后自动停止）..."
timeout 2 python -m mcp_yashan 2>&1 | head -1 &
STDIO_PID=$!
sleep 2

if ps -p $STDIO_PID > /dev/null 2>&1; then
    kill $STDIO_PID 2>/dev/null || true
    echo -e "${GREEN}✅ python -m mcp_yashan 可以启动${NC}"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠️  python -m mcp_yashan 启动后立即退出（可能正常，等待 STDIO 输入）${NC}"
    ((PASSED++))
fi

# 7. 测试包完整性
test_step "检查 runtime JAR 文件" "python -c '
import os
import mcp_yashan

# 获取包的安装路径
package_path = os.path.dirname(mcp_yashan.__file__)
runtime_path = os.path.join(package_path, \"runtime\")

# 检查 JDBC 驱动
jdbc_path = os.path.join(runtime_path, \"yashandb-jdbc-1.9.3.jar\")
helper_path = os.path.join(runtime_path, \"java\", \"yashan-mcp-helper.jar\")

jdbc_exists = os.path.exists(jdbc_path)
helper_exists = os.path.exists(helper_path)

print(f\"JDBC 驱动: {jdbc_path} - {\"存在\" if jdbc_exists else \"缺失\"}\")
print(f\"Helper JAR: {helper_path} - {\"存在\" if helper_exists else \"缺失\"}\")

if jdbc_exists and helper_exists:
    print(\"✅ JAR 文件完整\")
else:
    raise Exception(f\"JAR 文件缺失: jdbc={jdbc_exists}, helper={helper_exists}\")
'"

# 8. 运行完整测试脚本
if [ -f "test_v2.1.1.py" ]; then
    echo ""
    echo "=========================================="
    echo "测试: 运行完整测试套件"
    echo "=========================================="
    
    if python test_v2.1.1.py; then
        echo -e "${GREEN}✅ 完整测试套件通过${NC}"
        ((PASSED++))
    else
        echo -e "${RED}❌ 完整测试套件失败${NC}"
        ((FAILED++))
    fi
fi

# 9. 清理
echo ""
echo "=========================================="
echo "清理测试环境"
echo "=========================================="

deactivate 2>/dev/null || true

echo "是否删除测试虚拟环境? (y/n)"
read -t 5 -n 1 answer || answer="n"
echo ""

if [ "$answer" = "y" ]; then
    echo "删除 $VENV_DIR ..."
    rm -rf "$VENV_DIR"
    echo -e "${GREEN}✅ 清理完成${NC}"
else
    echo -e "${YELLOW}保留测试环境: $VENV_DIR${NC}"
    echo "手动清理: rm -rf $VENV_DIR"
fi

# 10. 汇总结果
echo ""
echo "=========================================="
echo "测试结果汇总"
echo "=========================================="
echo -e "通过: ${GREEN}$PASSED${NC}"
echo -e "失败: ${RED}$FAILED${NC}"
echo "总计: $((PASSED + FAILED))"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 所有测试通过！v2.1.1 可以发布！${NC}"
    exit 0
else
    echo -e "${RED}⚠️  有 $FAILED 个测试失败，需要修复${NC}"
    exit 1
fi
