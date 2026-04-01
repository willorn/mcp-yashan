# -*- coding: utf-8 -*-
"""
测试 MCP Streamable HTTP 端点
"""

import json
import requests
import sys

BASE_URL = "http://localhost:18080"

def test_health():
    """测试健康检查"""
    print("=" * 50)
    print("测试健康检查 /healthz")
    try:
        resp = requests.get(f"{BASE_URL}/healthz", timeout=5)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.json()}")
        return resp.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_initialize():
    """测试 initialize"""
    print("\n" + "=" * 50)
    print("测试 initialize")
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test-client", "version": "1.0.0"}
        }
    }
    try:
        resp = requests.post(f"{BASE_URL}/mcp", json=payload, timeout=5)
        print(f"Status: {resp.status_code}")
        print(f"Response: {json.dumps(resp.json(), indent=2, ensure_ascii=False)}")
        return resp.status_code == 200 and "result" in resp.json()
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_tools_list():
    """测试 tools/list"""
    print("\n" + "=" * 50)
    print("测试 tools/list")
    payload = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }
    try:
        resp = requests.post(f"{BASE_URL}/mcp", json=payload, timeout=5)
        print(f"Status: {resp.status_code}")
        result = resp.json()
        print(f"Tools count: {len(result.get('result', {}).get('tools', []))}")
        tool_names = [t['name'] for t in result.get('result', {}).get('tools', [])]
        print(f"Tools: {tool_names}")
        return resp.status_code == 200 and "tools" in result.get("result", {})
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_tools_call():
    """测试 tools/call - get_database_info"""
    print("\n" + "=" * 50)
    print("测试 tools/call - get_database_info")
    payload = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "get_database_info",
            "arguments": {}
        }
    }
    try:
        resp = requests.post(f"{BASE_URL}/mcp", json=payload, timeout=5)
        print(f"Status: {resp.status_code}")
        result = resp.json()
        print(f"Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
        return resp.status_code == 200 and "result" in result
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    print("MCP Streamable HTTP 端点测试")
    print(f"Base URL: {BASE_URL}")

    results = []
    results.append(("healthz", test_health()))
    results.append(("initialize", test_initialize()))
    results.append(("tools/list", test_tools_list()))
    results.append(("tools/call", test_tools_call()))

    print("\n" + "=" * 50)
    print("测试结果汇总:")
    all_passed = True
    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"  {name}: {status}")
        if not passed:
            all_passed = False

    if all_passed:
        print("\n✅ 所有测试通过!")
        return 0
    else:
        print("\n❌ 部分测试失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())
