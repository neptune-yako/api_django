# AI 交接文档：Jenkins 集成开发 (前端阶段)

## 1. 项目概述
这是一个基于 **Django (Backend)** + **Vue 3 / Element Plus (Frontend)** 的自动化测试平台。
当前的目标是集成 **Jenkins CI/CD** 功能，允许用户在平台内管理 Jenkins 服务器、同步 Job、触发构建并查看 Allure 报告。

## 2. 当前进度与状态

### 后端 (Backend) - **状态：就绪**
- **代码位置**: `backend/jenkins_integration/`
- **已完成**:
  - 模型 (`JenkinsServer`, `JenkinsJob`, `AllureReport`) 已建立。
  - API 接口已开发并注册在 `urls.py` (前缀为 `/api/jenkins/`)。
  - 解决了 `ImportError` 和 `AttributeError` 问题，服务可正常启动。
  - **关键点**: 后端路由配置包含 `/api` 前缀（例如 `api/jenkins/server/`）。

### 前端 (Frontend) - **状态：基础框架已搭建，功能待开发**
- **代码位置**: `frontend/src/views/jenkins/`
- **已完成**:
  - **路由**: `/jenkins/server`, `/jenkins/job`, `/jenkins/report` 已配置。
  - **菜单**: 侧边栏已配置二级菜单 "CI/CD管理"。
  - **页面**: `ServerList.vue`, `JobList.vue`, `ReportList.vue` **目前仅为占位符 (只有 `<h1>` 标题)**，确保了路由跳转不报错。
- **待修复/缺失**:
  - **API Client**: `src/api/jenkins.js` **已被删除**，需要重新创建。
  - **Vite 代理**: 用户可能误回退了 `vite.config.js` 的配置。后端需要 `/api` 前缀，但代理配置可能包含 `rewrite` 去除前缀的规则，导致 404。

## 3. 下一步开发指令 (Next Steps)

请按照以下顺序进行开发，**务必步步为营**，不要一次性生成所有代码：

### 第一步：环境与基础修复
1.  **检查 `vite.config.js`**:
    - 确认 `/api` 代理配置。如果后端路由是 `api/jenkins/...`，则 **不能** 有 `rewrite: (path) => path.replace(/^\/api/, '')`。如果存在，请删除该重写规则。
2.  **重建 `src/api/jenkins.js`**:
    - 创建该文件，并引入封装好的请求工具 `import request from '@/api/requests'` (注意路径是 `@/api/requests` 而不是 utils)。
    - 仅先添加 **服务器管理** 相关的 API (`getJenkinsServers`, `addJenkinsServer`, `updateJenkinsServer`, `deleteJenkinsServer`, `testJenkinsConnection`)。

### 第二步：开发「服务器管理」页面
1.  **编辑 `src/views/jenkins/server/ServerList.vue`**:
    - 从占位符改为实际功能组件。
    - 使用 Element Plus 实现：
        - 表格展示服务器列表。
        - "添加/编辑" 弹窗。
        - "测试连接" 功能。
    - **注意**: 确保引用刚创建的 API。

### 第三步：验证
1.  在前端页面进行真实操作（添加服务器、测试连接）。
2.  观察浏览器控制台网络请求，确保 URL 正确（应为 `/api/jenkins/server/`）。

## 4. 相关文件路径
- **Backend URLs**: `api_django/backend/jenkins_integration/urls.py`
- **Frontend Config**: `api_django/frontend/vite.config.js`
- **Frontend Router**: `api_django/frontend/src/router/index.js`
- **Frontend Views**: `api_django/frontend/src/views/jenkins/`
