# Jenkins 集成模块 - SQL 文件说明

## 📁 目录说明

本目录包含 Jenkins 集成模块的 SQL 初始化脚本，用于快速初始化数据库表结构。

---

## 📝 文件列表

### 1. `init_jenkins_tables.sql`
- **用途**：创建所有 Jenkins 集成相关的数据库表
- **包含表**：
  - `jenkins_server` - Jenkins 服务器配置
  - `jenkins_node` - Jenkins 节点管理
  - `jenkins_job` - Jenkins 任务管理
  - `jenkins_job_nodes` - Job 与 Node 的多对多关联
  - `allure_report` - Allure 报告统计
  - `allure_test_case` - Allure 测试用例详情

---

## 🚀 使用方法

### SQLite（开发环境）
```bash
# 在 backend 目录执行
cd backend
sqlite3 db.sqlite3 < jenkins_integration/sql/init_jenkins_tables.sql
```

### MySQL（生产环境）
```bash
mysql -u username -p database_name < jenkins_integration/sql/init_jenkins_tables.sql
```

### PostgreSQL（生产环境）
```bash
psql -U username -d database_name -f jenkins_integration/sql/init_jenkins_tables.sql
```

---

## ⚠️ 注意事项

1. **Django Migration 优先**
   - 正常开发流程建议使用 Django 的 migration 机制
   - 本 SQL 文件主要用于快速对接或数据库迁移场景

2. **数据库兼容性**
   - SQL 语法基于 SQLite
   - 如需用于 MySQL/PostgreSQL，请根据具体数据库调整语法
   - JSON 字段支持：SQLite 3.9.0+, MySQL 5.7.8+, PostgreSQL 9.2+

3. **外键约束**
   - SQLite 需要启用外键约束：`PRAGMA foreign_keys = ON;`
   - MySQL 默认启用外键约束
   - PostgreSQL 默认启用外键约束

---

## 🔄 与 Django Migration 的关系

| 场景 | 推荐方式 |
|------|---------|
| 开发环境 | 使用 Django Migration |
| 生产部署 | 使用 Django Migration |
| 数据库迁移 | 可使用 SQL 脚本快速初始化 |
| 紧急恢复 | 使用 SQL 脚本 + 数据备份 |

---

## 📊 表关系图

```
JenkinsServer (1) ─┬─→ (N) JenkinsNode
                   │
                   └─→ (N) JenkinsJob ─┬─→ (N) AllureReport ─→ (N) AllureTestCase
                                       │
                                       └─↔ (M:N) JenkinsNode
                                            (通过 jenkins_job_nodes)
```

---

## 🛠️ 维护说明

- **更新时机**：每次修改 `models.py` 后，同步更新 SQL 脚本
- **版本控制**：SQL 文件纳入 Git 版本控制
- **命名规范**：使用 `init_` 前缀表示初始化脚本

---

## 📌 相关文档

- 数据库设计方案：`JENKINS_DATABASE_PLAN.md`
- 模型定义：`models.py`
- 需求文档：`JENKINS.md`
