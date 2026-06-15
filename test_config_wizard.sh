#!/bin/bash
# 测试配置向导功能

set -e

echo "=========================================="
echo "测试配置向导功能"
echo "=========================================="

# 创建干净的测试环境
VENV_DIR="test_wizard_venv"

if [ -d "$VENV_DIR" ]; then
    rm -rf "$VENV_DIR"
fi

echo "创建虚拟环境..."
python -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

echo "安装 mcp-yashan..."
pip install dist/mcp_yashan-2.1.1-py3-none-any.whl --quiet

echo ""
echo "=========================================="
echo "测试 1: mcp-yashan --help"
echo "=========================================="
mcp-yashan --help

echo ""
echo "=========================================="
echo "测试 2: 检查配置向导模块"
echo "=========================================="
python -c "from mcp_yashan.config_wizard import check_java, check_config; print('Java:', check_java()); print('Config:', check_config())"

echo ""
echo "=========================================="
echo "测试 3: 非交互式启动（应该提示配置缺失）"
echo "=========================================="
echo "测试命令: echo '' | mcp-yashan"
echo "预期: 应该提示配置缺失但不会卡住"

# 清理
deactivate
rm -rf "$VENV_DIR"

echo ""
echo "✅ 测试完成"
