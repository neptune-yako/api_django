# Jenkins Integration - Project Context Summary

## 🚀 核心目标 (Objective)
在测试平台中集成 Jenkins，实现：
1.  **管理**：在平台配置 Jenkins 服务器，管理/触发构建任务。
2.  **查看**：在平台内直接查看 Allure 测试报告（代理模式）。
3.  **数据**：解析 Allure 报告统计数据（通过率、耗时等）并存入数据库，用于统计分析。

## ✅ 已完成任务 (Completed)

### 1. 后端重构 (Backend Refactoring)
*   **结构优化**：将臃肿的 `jenkins_integration/views.py` 拆分为模块化包：
    *   `server_views.py`: 服务器 CRUD。
    *   `job_remote_views.py`: 远程 Job 操作 (CRUD, Build, Copy)。
    *   `job_local_views.py`: 本地 Job 关联。
    *   `build_views.py`: 构建状态查询。
    *   `allure_views.py`: Allure 代理与同步。
    *   `template_views.py`: XML 模板管理。
*   **修复问题**：修复了拆分文件后 `urls.py` 中的 `ImportError: cannot import name 'allure_views'`。

### 2. 功能实现 (Feature Implementation)
*   **Jenkins 连接**：实现了服务器连接测试 (`JenkinsTestView`)。
*   **API 文档**：全量更新 `openapi.json`，覆盖所有新接口。
*   **Allure 代理**：实现了 `AllureProxyView`，支持路径参数代理，隐藏 Jenkins 界面。
*   **同步逻辑**：
    *   `services/allure_sync.py`: 包含解析 Allure JSON、事务写入 `AllureReport`/`AllureTestCase` 的完整逻辑。
    *   `utils/allure_parser.py`: 封装了从 Jenkins 获取并解析 `summary.json` 和 `suites.json` 的工具类。

### 3. 基础设施 (Infrastructure)
*   **Models**: `models.py` 中已定义 `AllureReport` 和 `AllureTestCase` 模型。
*   **环境**: 后端 Server 已成功启动，Jenkins 连通性测试通过。

## 📍 当前上下文焦点 (Current Focus)

目前处于 **数据层验证 (Data Verification)** 阶段。
代码逻辑（Service/Parser/View）看起来已经就绪，但尚未验证数据能否真正写入数据库。

### 待解决/待验证 (To-Do):
1.  **数据库迁移 (Critical)**:
    *   虽然 `models.py` 有代码，但不确定数据库里是否已经创建了 `allure_report` 表。
    *   **Action**: 运行 `makemigrations` 和 `migrate`。
2.  **端到端验证 (Validation)**:
    *   手动调用 `/api/jenkins/build/sync/` 接口，验证能否成功解析并存储一条 Allure 报告数据。
3.  **前端对接 (Next Phase)**:
    *   开发页面展示存储下来的统计数据（图表）。

## 📂 关键文件索引
*   **Models**: `backend/jenkins_integration/models.py`
*   **Sync Logic**: `backend/jenkins_integration/services/allure_sync.py`
*   **Parser**: `backend/jenkins_integration/utils/allure_parser.py`
*   **Views**: `backend/jenkins_integration/views/allure_views.py`
*   **URLs**: `backend/jenkins_integration/urls.py`
