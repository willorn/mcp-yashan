#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
稳定性修复验证测试
单独运行此文件验证修复是否生效
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.executor import get_executor


def test_input_validation():
    """测试输入验证"""
    print("=" * 60)
    print("测试 1: 输入验证")
    print("=" * 60)
    
    executor = get_executor()
    
    # 测试空 SQL
    print("\n1.1 测试空 SQL...")
    result = executor.execute("")
    assert not result["success"], "空 SQL 应该失败"
    assert "不能为空" in result["error"], f"错误信息不正确: {result['error']}"
    print(f"✅ 空 SQL 验证通过: {result['error']}")
    
    # 测试无效 max_rows
    print("\n1.2 测试无效 max_rows...")
    result = executor.execute("SELECT 1", max_rows=0)
    assert not result["success"], "max_rows=0 应该失败"
    assert "1-10000" in result["error"], f"错误信息不正确: {result['error']}"
    print(f"✅ max_rows 下限验证通过: {result['error']}")
    
    result = executor.execute("SELECT 1", max_rows=99999)
    assert not result["success"], "max_rows=99999 应该失败"
    assert "1-10000" in result["error"], f"错误信息不正确: {result['error']}"
    print(f"✅ max_rows 上限验证通过: {result['error']}")
    
    print("\n✅ 所有输入验证测试通过！")


def test_timeout_config():
    """测试超时配置"""
    print("\n" + "=" * 60)
    print("测试 2: 超时配置")
    print("=" * 60)
    
    executor = get_executor()
    
    print(f"\n当前超时配置: {executor.sql_timeout} 秒")
    print("提示: 可通过环境变量 SQL_TIMEOUT 修改")
    
    assert executor.sql_timeout > 0, "超时时间必须大于 0"
    print("✅ 超时配置验证通过！")


def test_parse_robustness():
    """测试解析容错性"""
    print("\n" + "=" * 60)
    print("测试 3: 解析容错性")
    print("=" * 60)
    
    executor = get_executor()
    
    # 测试解析异常数据
    print("\n3.1 测试解析异常输出...")
    result = executor._parse_output("INVALID_OUTPUT", "")
    assert not result["success"], "无效输出应该返回失败"
    print("✅ 异常输出处理正常")
    
    # 测试解析部分有效数据
    print("\n3.2 测试解析部分有效数据...")
    output = """SUCCESS:true
COL:ID
ROW_B64:INVALID_BASE64!!!
ROW_COUNT:invalid_number
EXEC_TIME:100"""
    result = executor._parse_output(output, "")
    assert result["success"], "应该标记为成功"
    print("✅ 部分有效数据处理正常")
    
    print("\n✅ 所有解析容错测试通过！")


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("稳定性修复验证测试")
    print("=" * 60)
    
    try:
        test_input_validation()
        test_timeout_config()
        test_parse_robustness()
        
        print("\n" + "=" * 60)
        print("🎉 所有测试通过！稳定性修复验证成功！")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
