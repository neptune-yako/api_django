import requests
import json

# 测试同步节点API已被删除
# print("测试1: 同步Jenkins节点...")
# response = requests.post('http://127.0.0.1:8000/api/jenkins/nodes/sync/', json={})
# print(f"状态码: {response.status_code}")
# print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
# print()

# 测试查询节点列表API
print("测试2: 查询Jenkins节点列表...")
response = requests.get('http://127.0.0.1:8000/api/jenkins/nodes/')
print(f"状态码: {response.status_code}")
result = response.json()
print(f"节点数量: {len(result.get('data', []))}")
if result.get('data'):
    print("\n第一个节点信息:")
    first_node = result['data'][0]
    for key, value in first_node.items():
        print(f"  {key}: {value}")
