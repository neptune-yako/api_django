# 测试接口沙箱 (Test Sandbox)

这个目录专门用于存放一些用于**自测**的临时接口。

## 🎯 目的
作为一个自动化测试平台，我们需要有被测对象来验证平台的功能（例如：接口测试、用例执行、断言验证等）。为了方便开发和演示，我们直接在后端项目中内置一些简单的测试接口，充当"SUT"（System Under Test）。

## 📝 接口清单 (Base URL: http://localhost:8080)

以下是已实现的 Mock 接口（适用于本地测试环境）：

1.  **用户管理 (User Mock)**
    -   `GET http://localhost:8080/api/test-sandbox/users/` (获取列表)
    -   `POST http://localhost:8080/api/test-sandbox/users/` (创建用户)
    -   `GET http://localhost:8080/api/test-sandbox/users/1/` (获取 ID 为 1 的用户详情)

2.  **状态模拟 (Status Mock)**
    -   `GET http://localhost:8080/api/test-sandbox/status/200/` (返回 200 OK)
    -   `GET http://localhost:8080/api/test-sandbox/status/500/` (返回 500 Error)
    -   `GET http://localhost:8080/api/test-sandbox/delay/3/` (延迟 3 秒响应)

3.  **鉴权模拟 (Auth Mock)**
    -   `POST http://localhost:8080/api/test-sandbox/login/` (Body: `{"username":"admin", "password":"123456"}`)
    -   `GET http://localhost:8080/api/test-sandbox/secure-data/` (需要 Header Authorization)

## 🚀 下一步
1.  创建 Django App `test_django` (如果还未初始化)
2.  定义 `views.py` 实现上述逻辑
3.  配置 `urls.py` 暴露接口
