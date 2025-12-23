"""
测试 Jenkins 节点 API 是否正常
"""
import requests

print("测试 Jenkins 节点 API...")
print("=" * 60)

# 1. 测试获取节点列表
print("\n1. 测试 GET /api/jenkins/nodes/")
try:
    response = requests.get('http://127.0.0.1:8000/api/jenkins/nodes/')
    print(f"状态码: {response.status_code}")
    print(f"响应内容:")
    import json
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
except Exception as e:
    print(f"错误: {e}")

print("\n" + "=" * 60)
