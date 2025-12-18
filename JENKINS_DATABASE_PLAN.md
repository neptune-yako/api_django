# Jenkins 数据库模型 - 完整实施方案

## 目标
为 Jenkins 集成模块创建完整的数据库模型，支持：
1. Jenkins 服务器配置管理
2. Jenkins Job 任务管理
3. Jenkins Node 节点管理
4. Allure 报告统计数据存储
5. 测试用例详情记录
6. 与现有系统（Project、Plan、Environment）深度集成

---

## 📊 **需求分析总览**

基于 **JENKINS.md** 的完整需求梳理：

### ✅ **1.1 Jenkins 服务器管理** (第 27-37 行)
- 添加 Jenkins 服务器配置
- 测试连接状态
- 查看 Job 列表
- 启用/禁用管理

### ✅ **1.2 Jenkins 任务管理** (第 39-64 行)
- **创建 Jenkins 任务（关联测试计划）** ⭐
- 配置任务参数（环境 ID、测试计划 ID）
- 手动触发构建
- 查看构建历史
- 同步任务状态
- 融合到现有任务管理

### ✅ **1.3 Jenkins Node 节点管理** (第 66-87 行)
- 从 Jenkins 同步获取所有 Node 节点
- 获取节点信息（名称、IP、标签、状态）
- 在环境管理中配置可用节点
- 创建任务时选择执行节点

### ✅ **1.4 定时构建任务管理** (第 89-96 行)
- 融合到现有定时任务系统
- Cron 表达式配置
- 启用/禁用定时构建

### ✅ **2.1 Allure 报告数据提取** (第 110-145 行)
- 提取基础统计数据
- 提取测试用例详情
- 附件（日志）下载

---

## 🗂️ **完整数据库表设计**

### **表 1：JenkinsServer** - Jenkins 服务器配置

**业务需求：**
- 支持配置多个 Jenkins 服务器
- 动态切换服务器连接
- 测试服务器连接状态
- 启用/禁用服务器

**数据字段：**
| 字段 | 类型 | 说明 |
|------|------|------|
| id | AutoField | 主键 |
| name | CharField(50) | 服务器名称 |
| url | URLField | Jenkins URL |
| username | CharField(50) | 认证用户名 |
| token | CharField(255) | API Token（加密存储）|
| is_active | BooleanField | 是否启用 |
| description | TextField | 服务器描述（可选）|
| last_check_time | DateTimeField | 最后连接测试时间 |
| connection_status | CharField(20) | 连接状态（connected/failed/unknown）|
| create_time | DateTimeField | 创建时间 |
| update_time | DateTimeField | 更新时间 |
| created_by | CharField(20) | 创建人 |

**索引设计：**
- 普通索引：`is_active` - 快速筛选启用的服务器

---

### **表 2：JenkinsNode** - Jenkins 节点管理

**业务需求：**
- 从 Jenkins 同步节点信息
- 支持在环境管理中配置可用节点
- 创建任务时选择执行节点

**数据字段：**
| 字段 | 类型 | 说明 |
|------|------|------|
| id | AutoField | 主键 |
| server | ForeignKey(JenkinsServer) | 所属 Jenkins 服务器 |
| name | CharField(100) | 节点名称 |
| display_name | CharField(100) | 显示名称 |
| description | TextField | 节点描述（可选）|
| num_executors | IntegerField | 执行器数量 |
| labels | CharField(200) | 节点标签（逗号分隔）|
| is_online | BooleanField | 是否在线 |
| is_idle | BooleanField | 是否空闲 |
| offline_cause | TextField | 离线原因（可选）|
| last_sync_time | DateTimeField | 最后同步时间 |
| create_time | DateTimeField | 创建时间 |
| update_time | DateTimeField | 更新时间 |

**索引设计：**
- 外键索引：`server_id` - 提高关联查询效率
- 唯一索引：`(server, name)` - 防止重复同步同一节点

---

### **表 3：JenkinsJob** - Jenkins 任务管理 ⭐⭐⭐

**业务需求：**
- 创建和管理 Jenkins 任务
- 支持在平台中手动创建或绑定已存在的 Job
- 查看任务的所有构建历史
- 同步任务状态
- **预留后期与现有系统集成的扩展性**

**设计策略：**
- ✅ **当前阶段**：隔离开发，独立功能验证
- 🔄 **后期扩展**：根据需求逐步集成现有系统（Project、Plan、Environment）

**数据字段：**
| 字段 | 类型 | 说明 |
|------|------|------|
| id | AutoField | 主键 |
| server | ForeignKey(JenkinsServer) | 所属 Jenkins 服务器 |
| name | CharField(100) | Job 名称（与 Jenkins 一致）|
| display_name | CharField(100) | 显示名称（平台自定义）|
| description | TextField | Job 描述（可选）|
| **project** | **ForeignKey(Project, null=True, blank=True)** | **关联项目（可选）** 💡 |
| **plan** | **ForeignKey(Plan, null=True, blank=True)** | **关联测试计划（可选，预留扩展）** 💡 |
| **environment** | **ForeignKey(Environment, null=True, blank=True)** | **关联测试环境（可选，预留扩展）** 💡 |
| **nodes** | **ManyToManyField(JenkinsNode, blank=True)** | **执行节点列表（可选，预留扩展）** 💡 |
| config_xml | TextField | Job 配置 XML（可选）|
| parameters | JSONField | 构建参数（默认参数配置）|
| is_active | BooleanField | 是否启用 |
| is_buildable | BooleanField | 是否可构建 |
| job_type | CharField(20) | Job 类型（freestyle/pipeline/maven）|
| last_build_number | IntegerField | 最后构建编号（可选）|
| last_build_status | CharField(20) | 最后构建状态（可选）|
| last_build_time | DateTimeField | 最后构建时间（可选）|
| last_sync_time | DateTimeField | 最后同步时间（可选）|
| created_by | CharField(20) | 创建人 |
| create_time | DateTimeField | 创建时间 |
| update_time | DateTimeField | 更新时间 |

**关键设计说明：**

1. **简化初期开发** ✅
   - `project`、`plan`、`environment`、`nodes` - 全部设为**可选**（`null=True, blank=True` 或 `blank=True`）
   - **当前环境**：所有任务都运行在主服务器（JenkinsServer）上，单节点环境
   - **当前阶段**：可以不填，允许独立开发测试
   - Token 明文存储，简化开发流程

2. **预留扩展性**（最佳实践）🔄
   - **字段已存在**：后期启用时无需添加字段，避免数据库 migration
   - **数据完整性**：字段结构清晰，便于理解业务模型
   - **灵活使用**：
     - `project`/`plan`/`environment` - 需要时直接填值即可
     - `nodes` - 需要时使用 `job.nodes.add(node)` 添加节点

3. **Node 关联说明** 💡
   - **当前阶段**：所有任务运行在主服务器上，不需要选择节点
   - **中间表**：`jenkins_job_nodes` 会在第一次 migration 时创建
   - **后期扩展**：需要多节点执行时，直接使用 `job.nodes.add(node1, node2)`
   - **使用场景**：跨平台测试、负载均衡、环境隔离等

**索引设计：**
- 外键索引：`server_id`, `project_id`, `plan_id`, `environment_id`（Django 自动创建）
- 唯一索引：`(server, name)` - 防止重复创建同名 Job
- 普通索引：`is_active`, `last_build_time`

---

### **表 4：AllureReport** - Allure 报告统计数据

**业务需求：**
- 存储每次构建的 Allure 报告统计数据
- 支持查询报告列表和详情
- 记录报告 URL 便于跳转
- **记录测试真实执行时间（非数据入库时间）**

**数据字段：**
| 字段 | 类型 | 说明 |
|------|------|------|
| id | AutoField | 主键 |
| **job** | **ForeignKey(JenkinsJob)** | **所属 Job** ⭐ |
| build_number | IntegerField | 构建编号 |
| total | IntegerField | 总用例数 |
| passed | IntegerField | 通过数量 |
| failed | IntegerField | 失败数量 |
| broken | IntegerField | 损坏数量（Broken）|
| skipped | IntegerField | 跳过数量 |
| pass_rate | DecimalField(5, 2) | 通过率（%）|
| duration | IntegerField | 总耗时（毫秒）|
| **start_timestamp** | **BigIntegerField** | **测试开始时间戳** ⭐ |
| **stop_timestamp** | **BigIntegerField** | **测试结束时间戳** ⭐ |
| allure_url | URLField | Allure 报告 URL |
| create_time | DateTimeField | 数据入库时间 |

**关键设计说明：**
- 外键从 `server + job_name` 改为 `job`，规范化设计
- 可以通过 `job.plan` 关联到测试计划
- 可以通过 `job.project` 关联到项目

**索引设计：**
- 唯一索引：`(job, build_number)` - 防止重复提取同一构建
- 外键索引：`job_id`
- 普通索引：`create_time`, `start_timestamp`

---

### **表 5：AllureTestCase** - 测试用例详情

**业务需求：**
- 存储每个测试用例的详细信息
- 支持查询用例列表和失败原因
- 记录测试步骤（JSON）
- **支持日志下载功能**
- **支持单用例历史趋势分析**

**数据字段：**
| 字段 | 类型 | 说明 |
|------|------|------|
| id | AutoField | 主键 |
| report | ForeignKey(AllureReport) | 所属报告 |
| **uid** | **CharField(64, unique=True)** | **🌟 Allure 用例唯一标识（用于日志下载）** |
| **history_id** | **CharField(64)** | **🌟 用例历史 ID（用于趋势分析）** |
| name | CharField(200) | 用例名称 |
| full_name | CharField(500) | 用例完整路径（可选）|
| status | CharField(20) | 状态（passed/failed/broken/skipped）|
| duration | IntegerField | 执行时长（毫秒）|
| description | TextField | 用例描述（可选）|
| error_message | TextField | 失败原因（可选）|
| error_trace | TextField | 错误堆栈（可选）|
| steps | JSONField | 测试步骤（JSON）|
| **attachments** | **JSONField** | **🌟 附件信息（日志、截图等）** |
| labels | JSONField | 标签信息（JSON）|
| parameters | JSONField | 参数信息（JSON）|
| create_time | DateTimeField | 创建时间 |

**关键字段说明：**

1. **uid** (极重要) 🌟🌟🌟
   - 来源：Allure 内部为每个用例生成的唯一标识（如 `c36b6eaf-...`）
   - 用途：下载日志的核心钥匙，配合 `get_log_content_by_uid()` 函数使用
   - 注意：必须设置为 **unique=True**，确保全局唯一

2. **history_id** (重要) 🌟🌟
   - 来源：Allure 用于识别"同一个用例"的 ID
   - 用途：实现单用例历史趋势分析（如：查看 LoginTest 在过去 10 次构建中的表现）

3. **attachments** (极重要) 🌟🌟🌟
   - 来源：Allure 用例附件信息（从 suites.json 中提取）
   - 格式：`[{"name": "log", "source": "abc.txt", "type": "text/plain"}, ...]`
   - 用途：前端直接渲染"下载日志"按钮，无需实时请求 Jenkins

**索引设计：**
- 唯一索引：`uid` - 确保用例全局唯一
- 外键索引：`report_id` - 提高关联查询效率
- 普通索引：`status`, `history_id` - 支持按状态筛选和历史趋势查询

---

## 🔗 **表关系图（当前阶段 - 可选关联）**

```
                    ┌─────────────────┐
                    │  JenkinsServer  │
                    │  (服务器配置)    │
                    └────────┬────────┘
                             │ 1:N
              ┌──────────────┼──────────────┐
              │              │              │
              ↓              ↓              ↓
     ┌────────────┐  ┌────────────┐  ┌────────────┐
     │JenkinsNode │  │ JenkinsJob │  │  (可选关联)│
     │ (节点管理) │  │ (任务管理) │  └────────────┘
     └────────────┘  └─────┬──────┘
                           │
                    ┌──────┼──────┐
                    │ ··   │ ··   │ ··
                    ↓      ↓      ↓
              ┌─────────┐ ┌────┐ ┌────────────┐
              │ Project │ │Plan│ │Environment │
              │(可选)   │ │(可选)│(可选)      │
              └─────────┘ └────┘ └────────────┘
                           │
                           │ 1:N
                           ↓
                   ┌──────────────┐
                   │AllureReport  │
                   │ (报告统计)   │
                   └──────┬───────┘
                          │ 1:N
                          ↓
                ┌──────────────────┐
                │ AllureTestCase   │
                │ (用例详情)       │
                └──────────────────┘

图例：
─── 实线：强制外键（必填）
··· 虚线：可选外键（null=True, blank=True）
```

**关键关联（当前阶段）：**
1. `JenkinsServer` → `JenkinsJob` (1:N) - 一个服务器有多个 Job ✅
2. `JenkinsServer` → `JenkinsNode` (1:N) - 一个服务器有多个 Node ✅
3. `JenkinsJob` ··→ `Project` (N:1, nullable) - Job 可选关联项目 💡
4. `JenkinsJob` ··→ `Plan` (N:1, nullable) - Job 可选关联测试计划 💡
5. `JenkinsJob` ··→ `Environment` (N:1, nullable) - Job 可选关联测试环境 💡
6. `JenkinsJob` ··↔ `JenkinsNode` (M:N, optional) - Job 可选关联多个执行节点 💡
7. `JenkinsJob` → `AllureReport` (1:N) - 一个 Job 有多个构建报告 ✅
8. `AllureReport` → `AllureTestCase` (1:N) - 一个报告有多个用例 ✅

**说明：**
- ✅ 实线：强制外键（必须填写）
- 💡 虚线：可选外键/关联（`null=True, blank=True` 或 `blank=True`）- **字段已存在，后期启用无需修改表结构**
- **当前环境**：所有任务运行在主服务器（JenkinsServer）上，单节点环境，不需要选择节点

---

## 📊 **数据库表结构预览**

```sql
-- jenkins_server
CREATE TABLE jenkins_server (
    id INTEGER PRIMARY KEY,
    name VARCHAR(50),
    url VARCHAR(200),
    username VARCHAR(50),
    token VARCHAR(255),
    is_active BOOLEAN,
    description TEXT,
    last_check_time DATETIME,
    connection_status VARCHAR(20),
    create_time DATETIME,
    update_time DATETIME,
    created_by VARCHAR(20)
);
CREATE INDEX idx_jenkins_server_active ON jenkins_server(is_active);

-- jenkins_node
CREATE TABLE jenkins_node (
    id INTEGER PRIMARY KEY,
    server_id INTEGER REFERENCES jenkins_server(id),
    name VARCHAR(100),
    display_name VARCHAR(100),
    description TEXT,
    num_executors INTEGER,
    labels VARCHAR(200),
    is_online BOOLEAN,
    is_idle BOOLEAN,
    offline_cause TEXT,
    last_sync_time DATETIME,
    create_time DATETIME,
    update_time DATETIME,
    UNIQUE(server_id, name)
);

-- jenkins_job (包含可选外键)
CREATE TABLE jenkins_job (
    id INTEGER PRIMARY KEY,
    server_id INTEGER REFERENCES jenkins_server(id),
    name VARCHAR(100),
    display_name VARCHAR(100),
    description TEXT,
    project_id INTEGER REFERENCES project(id),           -- 可选 💡
    plan_id INTEGER REFERENCES plan(id),                 -- 可选（预留扩展）💡
    environment_id INTEGER REFERENCES environment(id),   -- 可选（预留扩展）💡
    config_xml TEXT,
    parameters JSON,
    is_active BOOLEAN DEFAULT TRUE,
    is_buildable BOOLEAN DEFAULT TRUE,
    job_type VARCHAR(20) DEFAULT 'freestyle',
    last_build_number INTEGER,
    last_build_status VARCHAR(20),
    last_build_time DATETIME,
    last_sync_time DATETIME,
    created_by VARCHAR(20),
    create_time DATETIME,
    update_time DATETIME,
    UNIQUE(server_id, name)
);
CREATE INDEX idx_jenkins_job_server ON jenkins_job(server_id);
CREATE INDEX idx_jenkins_job_project ON jenkins_job(project_id);
CREATE INDEX idx_jenkins_job_plan ON jenkins_job(plan_id);
CREATE INDEX idx_jenkins_job_env ON jenkins_job(environment_id);
CREATE INDEX idx_jenkins_job_active ON jenkins_job(is_active);

-- jenkins_job_nodes (多对多中间表 - Job 与 Node 的关联)
CREATE TABLE jenkins_job_nodes (
    id INTEGER PRIMARY KEY,
    job_id INTEGER REFERENCES jenkins_job(id) ON DELETE CASCADE,
    node_id INTEGER REFERENCES jenkins_node(id) ON DELETE CASCADE,
    UNIQUE(job_id, node_id)
);
CREATE INDEX idx_jenkins_job_nodes_job ON jenkins_job_nodes(job_id);
CREATE INDEX idx_jenkins_job_nodes_node ON jenkins_job_nodes(node_id);

-- allure_report
CREATE TABLE allure_report (
    id INTEGER PRIMARY KEY,
    job_id INTEGER REFERENCES jenkins_job(id),          -- 外键指向 Job ⭐
    build_number INTEGER,
    total INTEGER,
    passed INTEGER,
    failed INTEGER,
    broken INTEGER,
    skipped INTEGER,
    pass_rate DECIMAL(5, 2),
    duration INTEGER,
    start_timestamp BIGINT,
    stop_timestamp BIGINT,
    allure_url VARCHAR(200),
    create_time DATETIME,
    UNIQUE(job_id, build_number)                         -- 唯一约束修改 ⭐
);
CREATE INDEX idx_allure_report_start_time ON allure_report(start_timestamp);

-- allure_test_case
CREATE TABLE allure_test_case (
    id INTEGER PRIMARY KEY,
    report_id INTEGER REFERENCES allure_report(id),
    uid VARCHAR(64) UNIQUE NOT NULL,
    history_id VARCHAR(64),
    name VARCHAR(200),
    full_name VARCHAR(500),
    status VARCHAR(20),
    duration INTEGER,
    description TEXT,
    error_message TEXT,
    error_trace TEXT,
    steps JSON,
    attachments JSON,
    labels JSON,
    parameters JSON,
    create_time DATETIME
);
CREATE UNIQUE INDEX idx_allure_testcase_uid ON allure_test_case(uid);
CREATE INDEX idx_allure_testcase_history ON allure_test_case(history_id);
CREATE INDEX idx_allure_testcase_status ON allure_test_case(status);
```

---

## 🎯 **设计亮点总结**

### ✅ **1. 渐进式开发策略**
- ✅ **当前阶段**：聚焦核心功能，隔离开发
- ✅ **预留扩展性**：支持后期与现有系统集成
- ✅ **降低复杂度**：避免过早耦合，简化初期开发

### ✅ **2. 完整覆盖核心需求**
- ✅ 服务器管理（JENKINS.md 1.1）
- ✅ 任务管理（JENKINS.md 1.2）
- ✅ 节点管理（JENKINS.md 1.3）- 预留扩展
- ✅ Allure 报告集成（JENKINS.md 2.1, 2.2）

### ✅ **3. 规范的数据库设计**
- ✅ 合理的外键关系（`Server` → `Job` → `Report` → `TestCase`）
- ✅ 唯一约束防止重复数据（`(server, name)`, `uid`）
- ✅ 索引优化查询性能
- ✅ JSONField 存储复杂结构（steps, attachments, parameters）

### ✅ **4. 支持高级功能**
- ✅ 日志下载（`uid` 字段）
- ✅ 历史趋势分析（`history_id` 字段）
- ✅ 附件管理（`attachments` JSONField）
- 🔄 多节点执行（后期扩展）

---

## ✅ **已确认的设计决策**

根据讨论结果，以下设计已确认：

### 1. **project 外键 - 可选** ✅
- 设置为 `null=True, blank=True`
- 允许独立开发和测试
- 后期可按需启用项目关联

### 2. **保留 project、plan、environment 字段，设为可选** ✅
- **最佳实践**：字段已存在，后期启用无需修改表结构
- 全部设置为 `null=True, blank=True`
- 当前阶段：可以不填，允许独立开发
- 后期需要时：直接填值即可，避免数据库 migration
- **优势**：避免后期修改表结构的复杂度和风险

### 3. **不需要 BuildHistory 表** ✅
- 通过 `AllureReport` 表即可查询构建历史
- 避免数据冗余
- 一个报告对应一次构建

### 4. **Token 明文存储** ✅
- 简化开发流程
- 当前环境下安全性可接受
- 生产环境可后续优化

### 5. **保留 nodes 字段（多对多关系）** ✅
- 保留 `nodes = ManyToManyField(JenkinsNode, blank=True)`
- **当前环境**：所有任务运行在主服务器上，单节点环境
- **当前阶段**：留空不用（`blank=True` 允许留空）
- **后期需要时**：直接使用 `job.nodes.add(node1, node2)`
- **优势**：字段已存在，中间表已创建，后期启用无需 migration
- **适用场景**：跨平台测试、负载均衡、环境隔离等

---

## 🗄️ **数据库迁移步骤**

```bash
# 1. 生成迁移文件
cd backend
python manage.py makemigrations jenkins_integration

# 2. 查看迁移 SQL（可选）
python manage.py sqlmigrate jenkins_integration 0001

# 3. 应用迁移
python manage.py migrate jenkins_integration

# 4. 验证表创建成功
python manage.py dbshell
# SQLite: .tables
# MySQL: SHOW TABLES;
```

---

## 🚀 **后续工作**

完成数据库模型创建后，下一步工作：

### 第一阶段：基础管理接口
1. **Jenkins 服务器管理接口**
   - 添加、编辑、删除服务器
   - 测试连接
   
2. **Jenkins Job 管理接口**
   - 创建、编辑、删除 Job
   - 同步 Jenkins 上的 Job
   - 关联测试计划

3. **Jenkins Node 管理接口**
   - 同步节点列表
   - 查询节点状态

### 第二阶段：Allure 数据提取
1. **创建 Allure JSON 解析器**（`allure_parser.py`）
2. **创建数据提取接口** (`POST /api/allure/extract/`)
3. **创建数据查询接口** (`GET /api/allure/reports/`)

### 第三阶段：定时任务集成
1. 扩展现有定时任务系统
2. 支持 Jenkins Job 定时触发
