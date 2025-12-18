# Jenkins & Allure 集成项目 - 上下文总结

> 📅 更新时间：2025-12-17  
> 🎯 项目阶段：基础框架完成，准备实施 Allure 数据提取

---

## 🎯 **项目目标**

实现 Django 后端与 Jenkins 的完整集成，包括：
1. Jenkins Job 管理（创建、更新、删除、触发构建）
2. Allure 测试报告的代理展示和数据提取
3. 前端可视化展示测试报告（隐藏 Jenkins 界面）

---

## ✅ **已完成功能**（35% 完成度）

### 1. Jenkins Job 管理 ✅ 100%
- **位置**：`backend/jenkins_integration/`
- **核心文件**：
  - `views.py` - Job CRUD 视图
  - `jenkins_client.py` - Jenkins API 封装
  - `template_manager.py` - Job 模板系统

**已实现接口**：
```python
POST   /api/jenkins/job/           # 创建 Job（支持 config.xml）
GET    /api/jenkins/job/           # 获取 Job 信息/配置
PUT    /api/jenkins/job/           # 更新 Job 配置
DELETE /api/jenkins/job/           # 删除 Job
POST   /api/jenkins/job/build/     # 触发构建
GET    /api/jenkins/build/latest/  # 查询构建状态（轮询）
```

### 2. Allure 报告代理 ✅ 100%
- **位置**：`backend/jenkins_integration/allure_views.py`
- **核心功能**：
  - 代理显示 Allure 报告（完全隐藏 Jenkins 界面）
  - 注入自定义样式
  - 自定义 404/错误页面
  - RESTful 路径参数设计

**已实现接口**：
```python
GET /api/jenkins/build/allure/                      # 获取 Allure URL
GET /api/jenkins/allure-proxy/{job}/{build}/        # 代理显示报告
GET /api/jenkins/allure-proxy/{job}/{build}/{file}  # 代理静态资源
```

---

## ❌ **待实现功能**（65% 未完成）

### 🔴 **高优先级 - Allure 数据提取**

**需求**：从 Jenkins Allure 报告中提取测试数据并保存到数据库

**实施方案**（已确认）：
```
流程：
1. 前端轮询获取构建完成 (/api/jenkins/build/latest/)
2. 前端调用数据提取接口 (POST /api/allure/extract/)
3. 后端自动请求3个JSON：
   - /allure/widgets/summary.json       → 统计数据
   - /allure/data/suites.json            → 用例详情  
   - /allure/widgets/history-trend.json  → 历史趋势
4. 后端转换数据并保存到数据库
5. 返回结果给前端
```

**需要创建**：
```python
# 1. 数据库模型
class AllureReport(models.Model):
    job_name, build_number, total, passed, failed, 
    broken, skipped, pass_rate, duration, allure_url

class AllureTestCase(models.Model):
    report (FK), name, status, duration, 
    error_message, steps (JSON)

# 2. 数据提取接口
POST /api/allure/extract/        # 提取数据
GET  /api/allure/reports/        # 查询报告
GET  /api/allure/test-cases/     # 查询用例

# 3. 解析器
allure_parser.py:
- extract_summary()
- extract_test_cases()
- extract_history_trend()
```

### 🟡 **中优先级**
- Jenkins 服务器配置管理（当前硬编码）
- Node 节点管理
- 定时任务集成

---

## 📁 **项目结构**

```
backend/jenkins_integration/
├── views.py                    # Job 管理视图
├── allure_views.py             # Allure 相关视图  
├── jenkins_client.py           # Jenkins API 客户端
├── template_manager.py         # Job 模板管理
├── urls.py                     # 路由配置
├── utils/                      # 工具类（响应、异常）
├── job_templates/              # Job XML 模板
└── templates/                  # 自定义 404/错误页面
    └── jenkins_integration/
        ├── allure_404.html
        └── allure_error.html
```

---

## 🔧 **技术栈**

- **后端**：Django + Django REST Framework
- **Jenkins API**：`python-jenkins` 库
- **数据库**：Django ORM
- **前端通信**：RESTful API（统一响应格式）

---

## 📝 **重要文档**

| 文档 | 路径 | 用途 |
|------|------|------|
| 需求文档 | `JENKINS.md` | 原始需求 |
| 进度跟踪 | `JENKINS_PROGRESS.md` | 实时进度（含完成标记）|
| 差距分析 | `JENKINS_GAP_ANALYSIS.md` | 详细功能对比 |
| Allure 代理设计 | `ALLURE_PROXY_DESIGN.md` | 代理方案设计 |
| Allure 代理实施 | `ALLURE_PROXY_IMPLEMENTATION.md` | 实施文档 |

---

## 🎯 **下一步行动**

### 立即开始：Allure 数据提取

**步骤**：
1. 创建数据库模型（`models.py`）
2. 创建数据提取视图（`allure_views.py`）
3. 创建解析器（`allure_parser.py`）
4. 配置 URL 路由
5. 测试数据提取功能

**预估时间**：2-3 小时

---

## 💡 **关键决策记录**

1. **Allure 展示方式**：使用后端代理 + iframe（而非提取数据前端渲染）
2. **URL 设计**：路径参数（`/proxy/job/8/`）而非查询字符串
3. **数据提取方式**：方案1 - 从 Jenkins workspace JSON 文件提取
4. **数据提取触发**：前端构建完成后调用后端接口，后端统一处理

---

## 🔗 **相关配置**

**Jenkins 连接**（当前硬编码）：
```python
# jenkins_client.py
JENKINS_URL = 'http://mg.morry.online'
USERNAME = 'admin'
PASSWORD = 'your_token'
```

**前端轮询接口**：
```
GET /api/jenkins/build/latest/?job_name=xxx
```

---

## 📌 **开始新对话时**

告诉 AI：
> "我在开发 Jenkins 和 Allure 集成项目，当前已完成 Job 管理和 Allure 代理展示。
> 现在需要实现 Allure 数据提取功能，从 3 个 JSON 文件提取数据并保存到数据库。
> 请查看 JENKINS_PROGRESS.md 了解详细进度。"

然后从创建数据库模型开始！🚀
