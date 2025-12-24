# 问题修复: JenkinsServer 模型字段错误

## 🐛 问题描述

在调用获取凭证列表API时出现错误:
```
GET http://127.0.0.1:8000/api/jenkins/credentials/ 400 (Bad Request)
{
    "code": 5006,
    "message": "获取Jenkins服务器配置失败: 'JenkinsServer' object has no attribute 'password'",
    "data": null
}
```

## 🔍 问题原因

在 `jenkins_client.py` 的 `get_credentials_list()` 函数中，错误地使用了 `server.password` 字段，但 `JenkinsServer` 模型实际使用的是 `server.token` 字段。

### 模型定义
```python
class JenkinsServer(models.Model):
    name = models.CharField(max_length=50, verbose_name="服务器名称")
    url = models.URLField(max_length=200, verbose_name="Jenkins URL")
    username = models.CharField(max_length=50, verbose_name="认证用户名")
    token = models.CharField(max_length=255, verbose_name="API Token")  # ✓ 正确
    # password = ...  # ✗ 不存在
```

## ✅ 修复方案

修改 `backend/jenkins_integration/jenkins_client.py` 中的 `get_credentials_list()` 函数:

**修改前 (错误)**:
```python
jenkins_url = server.url.rstrip('/')
username = server.username
password = server.password  # ✗ 错误: 模型没有此字段

auth = (username, password)
```

**修改后 (正确)**:
```python
jenkins_url = server.url.rstrip('/')
username = server.username
token = server.token  # ✓ 正确: 使用 token 字段

auth = (username, token)  # ✓ 正确: 使用 token 进行认证
```

## 📝 修改位置

**文件**: `backend/jenkins_integration/jenkins_client.py`
**函数**: `get_credentials_list()`
**行号**: 1471, 1481

**变更内容**:
- 第1471行: `password = server.password` → `token = server.token`
- 第1481行: `auth = (username, password)` → `auth = (username, token)`

## 🧪 验证

修复后，API应该可以正常工作:

```bash
# 测试API
curl -X GET http://127.0.0.1:8000/api/jenkins/credentials/

# 期望响应
{
  "code": 200,
  "message": "成功获取 N 个凭证",
  "data": [
    {
      "id": "credential-id",
      "description": "...",
      "typeName": "SSH Username with private key",
      ...
    }
  ]
}
```

## 💡 根本原因

Jenkins 认证使用的是 **API Token** 而不是密码:
- **Username + API Token** - Jenkins 推荐的认证方式
- **Username + Password** - 不安全，已逐步废弃

我们的系统正确地使用了 Token 认证，但在新增的凭证查询功能中错误地引用了字段名。

## 🔒 注意事项

在 Jenkins 中:
1. **API Token** 是推荐的认证方式
2. **密码认证** 已逐步被淘汰
3. 所有 API 调用都应使用 `(username, token)` 进行基本认证

---

## 总结

问题已修复，现在可以正常查询Jenkins凭证列表了！✅
