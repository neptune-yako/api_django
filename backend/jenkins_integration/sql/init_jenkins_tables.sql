-- Jenkins 集成模块 - 数据库初始化 SQL
-- 生成时间: 2025-12-17
-- 用途: 快速初始化 Jenkins 集成相关的数据库表结构

-- ==============================================================================
-- 表 1: jenkins_server - Jenkins 服务器配置
-- ==============================================================================
CREATE TABLE IF NOT EXISTS jenkins_server (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) NOT NULL,
    url VARCHAR(200) NOT NULL,
    username VARCHAR(50) NOT NULL,
    token VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    description TEXT,
    last_check_time DATETIME,
    connection_status VARCHAR(20) DEFAULT 'unknown',
    create_time DATETIME NOT NULL,
    update_time DATETIME NOT NULL,
    created_by VARCHAR(20) NOT NULL
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_jenkins_server_active ON jenkins_server(is_active);

-- ==============================================================================
-- 表 2: jenkins_node - Jenkins 节点管理
-- ==============================================================================
CREATE TABLE IF NOT EXISTS jenkins_node (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    server_id INTEGER NOT NULL,
    name VARCHAR(100) NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    num_executors INTEGER DEFAULT 1,
    labels VARCHAR(200),
    is_online BOOLEAN DEFAULT 1,
    is_idle BOOLEAN DEFAULT 1,
    offline_cause TEXT,
    last_sync_time DATETIME,
    create_time DATETIME NOT NULL,
    update_time DATETIME NOT NULL,
    FOREIGN KEY (server_id) REFERENCES jenkins_server(id) ON DELETE CASCADE,
    UNIQUE(server_id, name)
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_jenkins_node_server ON jenkins_node(server_id);

-- ==============================================================================
-- 表 3: jenkins_job - Jenkins 任务管理
-- ==============================================================================
CREATE TABLE IF NOT EXISTS jenkins_job (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    server_id INTEGER NOT NULL,
    name VARCHAR(100) NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    -- 与现有系统集成（可选）
    project_id INTEGER,
    plan_id INTEGER,
    environment_id INTEGER,
    -- Job 配置
    config_xml TEXT,
    parameters JSON,
    -- 状态信息
    is_active BOOLEAN DEFAULT 1,
    is_buildable BOOLEAN DEFAULT 1,
    job_type VARCHAR(20) DEFAULT 'freestyle',
    -- 构建信息
    last_build_number INTEGER,
    last_build_status VARCHAR(20),
    last_build_time DATETIME,
    last_sync_time DATETIME,
    -- 审计字段
    created_by VARCHAR(20) NOT NULL,
    create_time DATETIME NOT NULL,
    update_time DATETIME NOT NULL,
    FOREIGN KEY (server_id) REFERENCES jenkins_server(id) ON DELETE CASCADE,
    FOREIGN KEY (project_id) REFERENCES project(id) ON DELETE SET NULL,
    FOREIGN KEY (plan_id) REFERENCES plan(id) ON DELETE SET NULL,
    FOREIGN KEY (environment_id) REFERENCES environment(id) ON DELETE SET NULL,
    UNIQUE(server_id, name)
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_jenkins_job_server ON jenkins_job(server_id);
CREATE INDEX IF NOT EXISTS idx_jenkins_job_project ON jenkins_job(project_id);
CREATE INDEX IF NOT EXISTS idx_jenkins_job_plan ON jenkins_job(plan_id);
CREATE INDEX IF NOT EXISTS idx_jenkins_job_env ON jenkins_job(environment_id);
CREATE INDEX IF NOT EXISTS idx_jenkins_job_active ON jenkins_job(is_active);
CREATE INDEX IF NOT EXISTS idx_jenkins_job_build_time ON jenkins_job(last_build_time);

-- ==============================================================================
-- 表 4: jenkins_job_nodes - Job 与 Node 的多对多关联（中间表）
-- ==============================================================================
CREATE TABLE IF NOT EXISTS jenkins_job_nodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id INTEGER NOT NULL,
    node_id INTEGER NOT NULL,
    FOREIGN KEY (job_id) REFERENCES jenkins_job(id) ON DELETE CASCADE,
    FOREIGN KEY (node_id) REFERENCES jenkins_node(id) ON DELETE CASCADE,
    UNIQUE(job_id, node_id)
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_jenkins_job_nodes_job ON jenkins_job_nodes(job_id);
CREATE INDEX IF NOT EXISTS idx_jenkins_job_nodes_node ON jenkins_job_nodes(node_id);

-- ==============================================================================
-- 表 5: allure_report - Allure 报告统计数据
-- ==============================================================================
CREATE TABLE IF NOT EXISTS allure_report (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id INTEGER NOT NULL,
    build_number INTEGER NOT NULL,
    -- 统计数据
    total INTEGER DEFAULT 0,
    passed INTEGER DEFAULT 0,
    failed INTEGER DEFAULT 0,
    broken INTEGER DEFAULT 0,
    skipped INTEGER DEFAULT 0,
    pass_rate DECIMAL(5, 2) DEFAULT 0,
    duration INTEGER DEFAULT 0,
    -- 测试执行时间
    start_timestamp BIGINT NOT NULL,
    stop_timestamp BIGINT NOT NULL,
    -- Allure 报告 URL
    allure_url VARCHAR(200) NOT NULL,
    -- 数据入库时间
    create_time DATETIME NOT NULL,
    FOREIGN KEY (job_id) REFERENCES jenkins_job(id) ON DELETE CASCADE,
    UNIQUE(job_id, build_number)
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_allure_report_job ON allure_report(job_id);
CREATE INDEX IF NOT EXISTS idx_allure_report_create ON allure_report(create_time);
CREATE INDEX IF NOT EXISTS idx_allure_report_start ON allure_report(start_timestamp);

-- ==============================================================================
-- 表 6: allure_test_case - Allure 测试用例详情
-- ==============================================================================
CREATE TABLE IF NOT EXISTS allure_test_case (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id INTEGER NOT NULL,
    -- 用例唯一标识（用于日志下载）
    uid VARCHAR(64) UNIQUE NOT NULL,
    -- 历史 ID（用于趋势分析）
    history_id VARCHAR(64) NOT NULL,
    -- 用例基本信息
    name VARCHAR(200) NOT NULL,
    full_name VARCHAR(500),
    status VARCHAR(20) NOT NULL,
    duration INTEGER DEFAULT 0,
    description TEXT,
    -- 错误信息
    error_message TEXT,
    error_trace TEXT,
    -- JSON 字段
    steps JSON,
    attachments JSON,
    labels JSON,
    parameters JSON,
    -- 创建时间
    create_time DATETIME NOT NULL,
    FOREIGN KEY (report_id) REFERENCES allure_report(id) ON DELETE CASCADE
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_allure_testcase_report ON allure_test_case(report_id);
CREATE INDEX IF NOT EXISTS idx_allure_testcase_uid ON allure_test_case(uid);
CREATE INDEX IF NOT EXISTS idx_allure_testcase_history ON allure_test_case(history_id);
CREATE INDEX IF NOT EXISTS idx_allure_testcase_status ON allure_test_case(status);

-- ==============================================================================
-- 说明
-- ==============================================================================
-- 1. 本 SQL 适用于 SQLite 数据库
-- 2. 如需用于 MySQL/PostgreSQL，请根据具体数据库语法调整
-- 3. JSON 字段在 SQLite 3.9.0+ 支持，MySQL 5.7.8+ 支持
-- 4. 所有表都包含适当的外键约束和索引优化
-- 5. 多对多关系通过中间表 jenkins_job_nodes 实现

-- 使用方法:
-- SQLite: sqlite3 your_database.db < init_jenkins_tables.sql
-- MySQL: mysql -u username -p database_name < init_jenkins_tables.sql
