import requests
from requests.auth import HTTPBasicAuth

# 1. 你的配置
JENKINS_URL = "http://mg.morry.online"  # 注意：不带尾部斜杠
USERNAME = "akko"
TOKEN = "112f35231e8ffe20994a406815179d8a68"  # 务必是刚才新生成的那个

# 构造 API 地址 (Jenkins 的标准测试接口)
api_url = f"{JENKINS_URL}/api/json"

print(f"正在尝试连接: {api_url} ...")

try:
    # 2. 发送原生请求
    # 使用 Basic Auth，这和 python-jenkins 内部机制一样
    response = requests.get(
        api_url, 
        auth=HTTPBasicAuth(USERNAME, TOKEN),
        timeout=10
    )
    
    # 3. 打印“真相”
    print("\n-------- 服务器响应结果 --------")
    print(f"HTTP 状态码: {response.status_code}")
    print(f"响应头 (Headers): {response.headers}")
    
    if response.status_code == 200:
        print("✅ 连接成功！用户验证通过。")
        print(f"Jenkins 版本: {response.headers.get('X-Jenkins')}")
    elif response.status_code == 401:
        print("❌ 401 认证失败：用户名或 Token 依然不对。")
    elif response.status_code == 403:
        print("❌ 403 禁止访问：可能是 CSRF 问题，或者是 Nginx 拦截了爬虫请求。")
        print("尝试读取返回内容看详细原因...")
        print(response.text[:500])  # 打印前500个字符
    elif response.status_code == 502:
        print("❌ 502 Bad Gateway：Nginx 连不上后面的 Docker 容器。")
    else:
        print(f"❌ 未知错误 ({response.status_code})")
        print(response.text[:500])

except Exception as e:
    print(f"\n❌ 网络连接直接中断: {e}")