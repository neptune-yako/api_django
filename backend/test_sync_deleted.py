import requests

# 测试同步接口是否已删除
print("测试: 验证同步接口已被删除...")
try:
    response = requests.post('http://127.0.0.1:8000/api/jenkins/nodes/sync/', json={})
    print(f"状态码: {response.status_code}")
    if response.status_code == 404:
        print("✅ 成功：接口已被删除 (404 Not Found)")
    else:
        print(f"❌ 警告：接口仍然可访问，响应码 {response.status_code}")
        print(f"响应: {response.text}")
except Exception as e:
    print(f"请求出错: {str(e)}")
