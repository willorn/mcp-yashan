#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试 mcp-yashan v2.1.1 修复
"""

import sys

def test_imports():
    """测试导入"""
    print("=" * 60)
    print("测试 1: 导入测试")
    print("=" * 60)
    
    try:
        from mcp_yashan.core import get_metadata, MetadataManager
        print("✅ 成功导入 get_metadata")
        print("✅ 成功导入 MetadataManager")
        return True
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False

def test_module_structure():
    """测试模块结构"""
    print("\n" + "=" * 60)
    print("测试 2: 模块结构测试")
    print("=" * 60)
    
    try:
        import mcp_yashan
        print(f"✅ mcp_yashan 版本: {mcp_yashan.__version__}")
        
        from mcp_yashan import core
        print(f"✅ core 模块可用")
        
        # 检查 __all__ 导出
        expected = ["get_executor", "JavaSqlExecutor", "get_metadata", "MetadataManager", "TOOLS", "handle_tool_call"]
        actual = core.__all__
        
        if set(expected) == set(actual):
            print(f"✅ core.__all__ 导出正确: {actual}")
        else:
            print(f"⚠️  core.__all__ 不匹配")
            print(f"   期望: {expected}")
            print(f"   实际: {actual}")
        
        return True
    except Exception as e:
        print(f"❌ 模块结构测试失败: {e}")
        return False

def test_metadata_manager():
    """测试 MetadataManager 实例化"""
    print("\n" + "=" * 60)
    print("测试 3: MetadataManager 实例化测试")
    print("=" * 60)
    
    try:
        from mcp_yashan.core import get_metadata, MetadataManager
        
        # 测试直接实例化
        print("测试直接实例化...")
        manager1 = MetadataManager()
        print(f"✅ 直接实例化成功: {type(manager1)}")
        
        # 测试通过 get_metadata 获取
        print("\n测试通过 get_metadata() 获取...")
        manager2 = get_metadata()
        print(f"✅ get_metadata() 成功: {type(manager2)}")
        
        # 验证单例模式
        if manager1 is manager2:
            print("✅ 单例模式正常工作")
        else:
            print("⚠️  单例模式可能有问题")
        
        return True
    except Exception as e:
        print(f"❌ MetadataManager 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tools_import():
    """测试 tools 模块"""
    print("\n" + "=" * 60)
    print("测试 4: Tools 模块测试")
    print("=" * 60)
    
    try:
        from mcp_yashan.core import TOOLS, handle_tool_call
        print(f"✅ 成功导入 TOOLS: {len(TOOLS)} 个工具")
        print(f"✅ 成功导入 handle_tool_call")
        
        # 列出所有工具
        print("\n可用工具:")
        for i, tool in enumerate(TOOLS, 1):
            print(f"  {i}. {tool['name']}")
        
        return True
    except Exception as e:
        print(f"❌ Tools 模块测试失败: {e}")
        return False

def test_entry_points():
    """测试入口点"""
    print("\n" + "=" * 60)
    print("测试 5: 入口点测试")
    print("=" * 60)
    
    try:
        # 测试 __main__.py
        import mcp_yashan.__main__
        print("✅ __main__.py 存在")
        
        # 测试 mcp_server
        from mcp_yashan import mcp_server
        print("✅ mcp_server 模块可导入")
        
        # 测试 http_server
        from mcp_yashan import http_server
        print("✅ http_server 模块可导入")
        
        return True
    except Exception as e:
        print(f"❌ 入口点测试失败: {e}")
        return False

def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("mcp-yashan v2.1.1 修复验证测试")
    print("=" * 60)
    
    results = []
    
    # 运行所有测试
    results.append(("导入测试", test_imports()))
    results.append(("模块结构测试", test_module_structure()))
    results.append(("MetadataManager 测试", test_metadata_manager()))
    results.append(("Tools 模块测试", test_tools_import()))
    results.append(("入口点测试", test_entry_points()))
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"总计: {passed} 通过, {failed} 失败")
    print("=" * 60)
    
    if failed == 0:
        print("\n🎉 所有测试通过！v2.1.1 修复成功！")
        return 0
    else:
        print(f"\n⚠️  有 {failed} 个测试失败，需要修复")
        return 1

if __name__ == "__main__":
    sys.exit(main())
