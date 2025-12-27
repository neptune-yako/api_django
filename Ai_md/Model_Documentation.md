# Test Report 数据模型完整文档

## 一、数据来源概述

本系统从 **Allure 测试报告** 中提取数据并存储到 MySQL 数据库。Allure 报告包含以下关键文件：

```
allure-report/
├── widgets/
│   ├── summary.json       → TestExecution (总览数据)
│   ├── categories.json    → Category (缺陷分类)
│   └── behaviors.json     → FeatureScenario (BDD场景)
└── data/
    └── suites.csv         → TestSuite + TestSuiteDetail (套件和用例数据)
```

---

## 二、数据模型详解

### 2.1 TestExecution (测试执行总览表)

#### 表的作用
存储**单次测试执行的整体统计信息**，相当于一个测试报告的"封面页"。每次 Jenkins 构建或本地执行测试后，会生成一条 `TestExecution` 记录。

#### 数据来源
**文件**: `allure-report/widgets/summary.json`

**JSON 结构示例**:
```json
{
  "reportName": "自动化测试报告",
  "testRuns": [],
  "statistic": {
    "total": 100,
    "passed": 85,
    "failed": 10,
    "skipped": 3,
    "broken": 2,
    "unknown": 0
  },
  "time": {
    "start": 1703664000000,
    "stop": 1703664900000,
    "duration": 900000,
    "minDuration": 100,
    "maxDuration": 5000,
    "sumDuration": 85000
  }
}
```

#### 字段映射表

| Django 模型字段 | JSON 路径 | 说明 | 示例值 |
|----------------|-----------|------|--------|
| `timestamp` | (外部传入) | 报告唯一标识 | "20241227001" |
| `report_title` | `reportName` | 报告标题 | "自动化测试报告" |
| `total_cases` | `statistic.total` | 总用例数 | 100 |
| `passed_cases` | `statistic.passed` | 通过数 | 85 |
| `failed_cases` | `statistic.failed` | 失败数 | 10 |
| `skipped_cases` | `statistic.skipped` | 跳过数 | 3 |
| `broken_cases` | `statistic.broken` | 中断数 | 2 |
| `unknown_cases` | `statistic.unknown` | 未知数 | 0 |
| `pass_rate` | (计算) | `passed / total * 100` | 85.00 |
| `min_duration` | `time.minDuration` | 最短用例耗时(ms) | 100 |
| `max_duration` | `time.maxDuration` | 最长用例耗时(ms) | 5000 |
| `sum_duration` | `time.sumDuration` | 总耗时(ms) | 85000 |
| `execution_time` | (计算) | 格式化时长 | "15m 0s" |
| `start_time` | `time.start` | 开始时间戳(ms转datetime) | "2024-12-27 10:00:00" |
| `end_time` | `time.stop` | 结束时间戳(ms转datetime) | "2024-12-27 10:15:00" |
| `status` | (推断) | 整体状态 | "success" / "failed" |
| `job` | (业务关联) | 关联的 Jenkins Job | ForeignKey |

#### 业务逻辑
- **唯一性约束**: `timestamp` 字段唯一，防止重复导入。
- **状态推断**: 如果 `failed_cases > 0` 或 `broken_cases > 0`，则 `status = 'failed'`，否则为 `'success'`。

---

### 2.2 TestSuite (测试套件汇总表)

#### 表的作用
存储**每个测试套件的统计信息**。一个 `TestExecution` 下可以有多个 `TestSuite`（如 `LoginSuite`, `PaymentSuite`）。

#### 数据来源
**文件**: `allure-report/data/suites.csv`

**CSV 结构示例**:
```csv
STATUS,START TIME,STOP TIME,DURATION IN MS,PARENT SUITE,SUITE,SUB SUITE,TEST CLASS,TEST METHOD,NAME,DESCRIPTION
passed,1703664000,1703664001,1200,LoginSuite,UserAuth,,,test_login_success,测试登录成功,验证正确用户名密码登录
failed,1703664002,1703664003,800,LoginSuite,UserAuth,,,test_login_fail,测试登录失败,验证错误密码登录
```

#### 字段映射表

| Django 模型字段 | CSV 列名 | 说明 | 聚合逻辑 |
|----------------|----------|------|----------|
| `suite_name` | `PARENT SUITE` | 套件名称 | 按 `PARENT SUITE` 分组 |
| `total_cases` | - | 该套件的用例总数 | COUNT(*) |
| `passed_cases` | `STATUS` | 通过数 | COUNT(WHERE STATUS='passed') |
| `failed_cases` | `STATUS` | 失败数 | COUNT(WHERE STATUS='failed') |
| `skipped_cases` | `STATUS` | 跳过数 | COUNT(WHERE STATUS='skipped') |
| `broken_cases` | `STATUS` | 中断数 | COUNT(WHERE STATUS='broken') |
| `unknown_cases` | `STATUS` | 未知数 | COUNT(WHERE STATUS NOT IN (...)) |
| `pass_rate` | - | 通过率 | `passed / total * 100` |
| `min_duration` | `DURATION IN MS` | 最短用例耗时 | MIN(DURATION IN MS) |
| `max_duration` | `DURATION IN MS` | 最长用例耗时 | MAX(DURATION IN MS) |
| `sum_duration` | `DURATION IN MS` | 总耗时 | SUM(DURATION IN MS) |
| `duration_seconds` | `DURATION IN MS` | 总耗时(秒) | SUM(DURATION IN MS) / 1000 |

#### 业务逻辑
- **聚合计算**: `report_parser.py` 中的 `extract_suites_data_from_allure_report()` 函数会读取 CSV，按 `PARENT SUITE` 分组统计。
- **关联关系**: `execution` 字段关联到 `TestExecution`，形成一对多关系。

---

### 2.3 TestSuiteDetail (测试用例详情表) ⭐

#### 表的作用
存储**每个测试用例的详细信息**。这是最细粒度的数据，每一行代表一个具体的测试方法执行结果。

#### 数据来源
**文件**: `allure-report/data/suites.csv` (与 TestSuite 来源相同，但不聚合)

**CSV 行示例**:
```csv
passed,1703664000,1703664001,1200,LoginSuite,UserAuth,,TestLogin,test_login_success,测试登录成功,验证正确用户名密码登录
```

#### 字段映射表

| Django 模型字段 | CSV 列名 | 说明 | 示例值 |
|----------------|----------|------|--------|
| `name` | `NAME` | 用例名称 | "测试登录成功" |
| `description` | `DESCRIPTION` | 用例描述 | "验证正确用户名密码登录" |
| `parent_suite` | `PARENT SUITE` | 父套件 | "LoginSuite" |
| `suite` | `SUITE` | 套件 | "UserAuth" |
| `sub_suite` | `SUB SUITE` | 子套件 | "" (可为空) |
| `test_class` | `TEST CLASS` | 测试类 | "TestLogin" |
| `test_method` | `TEST METHOD` | 测试方法 | "test_login_success" |
| `status` | `STATUS` | 状态 | "passed" / "failed" / "skipped" / "broken" |
| `start_time` | `START TIME` | 开始时间戳 | "1703664000" |
| `stop_time` | `STOP TIME` | 结束时间戳 | "1703664001" |
| `duration_in_ms` | `DURATION IN MS` | 耗时(毫秒) | 1200 |

#### 业务逻辑
- **层级结构**: `parent_suite` → `suite` → `sub_suite` → `test_class` → `test_method` 形成五级层级。
- **关联关系**: `execution` 字段关联到 `TestExecution`。
- **用途**: 前端可以通过这个表实现"点击套件 → 展开用例列表"的交互。

---

### 2.4 Category (缺陷分类表)

#### 表的作用
存储**失败用例的分类统计**。Allure 可以根据错误信息自动将失败用例归类（如 "Product defects", "Test defects"）。

#### 数据来源
**文件**: `allure-report/widgets/categories.json`

**JSON 结构示例**:
```json
{
  "categories": [
    {
      "name": "Product defects",
      "children": [
        {"uid": "case1"},
        {"uid": "case2"}
      ],
      "description": "产品缺陷导致的失败"
    }
  ]
}
```

#### 字段映射表

| Django 模型字段 | JSON 路径 | 说明 | 示例值 |
|----------------|-----------|------|--------|
| `category_name` | `categories[].name` | 分类名称 | "Product defects" |
| `count` | `categories[].children.length` | 该分类下的用例数 | 2 |
| `severity` | (推断) | 严重程度 | "critical" / "major" / "minor" |
| `description` | `categories[].description` | 分类描述 | "产品缺陷导致的失败" |

#### 业务逻辑
- **严重程度推断**: 根据 `category_name` 中的关键词（如 "critical", "严重"）自动判断 `severity`。
- **关联关系**: `execution` 字段关联到 `TestExecution`。

---

### 2.5 FeatureScenario (特性场景表)

#### 表的作用
存储 **BDD (Behavior-Driven Development) 风格的场景统计**。如果测试代码使用了 `@allure.feature` 和 `@allure.story` 注解，会生成这个数据。

#### 数据来源
**文件**: `allure-report/widgets/behaviors.json`

**JSON 结构示例**:
```json
{
  "features": [
    {
      "name": "用户登录",
      "children": [...],
      "statistic": {
        "total": 10,
        "passed": 8,
        "failed": 2
      }
    }
  ]
}
```

#### 字段映射表

| Django 模型字段 | JSON 路径 | 说明 | 示例值 |
|----------------|-----------|------|--------|
| `scenario_name` | `features[].name` | 场景名称 | "用户登录" |
| `count` | `features[].children.length` | 该场景下的用例数 | 10 |
| `total` | `features[].statistic.total` | 总数 | 10 |
| `passed` | `features[].statistic.passed` | 通过数 | 8 |
| `failed` | `features[].statistic.failed` | 失败数 | 2 |
| `pass_rate` | (计算) | `passed / total * 100` | 80.00 |

#### 业务逻辑
- **可选数据**: 如果测试代码没有使用 BDD 注解，这个表可能为空。
- **关联关系**: `execution` 字段关联到 `TestExecution`。

---

## 三、表与表之间的关系

### 3.1 ER 图

```
┌─────────────────┐
│  TestExecution  │ (1次测试执行)
│  - timestamp    │
│  - total_cases  │
│  - pass_rate    │
└────────┬────────┘
         │
         │ 1:N
         ├──────────────────────────────────┐
         │                                  │
         ▼                                  ▼
┌─────────────────┐              ┌──────────────────┐
│   TestSuite     │              │ TestSuiteDetail  │
│  - suite_name   │              │  - name          │
│  - total_cases  │              │  - test_method   │
│  - pass_rate    │              │  - status        │
└─────────────────┘              │  - duration_in_ms│
                                 └──────────────────┘
         │
         │ 1:N
         ├──────────────────┬──────────────────┐
         │                  │                  │
         ▼                  ▼                  ▼
┌─────────────┐   ┌──────────────────┐   ┌──────────────┐
│  Category   │   │ FeatureScenario  │   │ (其他扩展表)  │
│ - category  │   │  - scenario_name │   │              │
│ - severity  │   │  - pass_rate     │   │              │
└─────────────┘   └──────────────────┘   └──────────────┘
```

### 3.2 关系说明

1.  **TestExecution (1) → TestSuite (N)**
    *   一次执行包含多个套件。
    *   外键: `TestSuite.execution_id` → `TestExecution.id`

2.  **TestExecution (1) → TestSuiteDetail (N)**
    *   一次执行包含多个用例。
    *   外键: `TestSuiteDetail.execution_id` → `TestExecution.id`
    *   **注意**: `TestSuiteDetail` 和 `TestSuite` 是平行关系，前者是明细，后者是汇总。

3.  **TestExecution (1) → Category (N)**
    *   一次执行可能有多个缺陷分类。
    *   外键: `Category.execution_id` → `TestExecution.id`

4.  **TestExecution (1) → FeatureScenario (N)**
    *   一次执行可能有多个 BDD 场景。
    *   外键: `FeatureScenario.execution_id` → `TestExecution.id`

### 3.3 查询示例

#### 查询某次执行的所有失败用例
```python
execution = TestExecution.objects.get(timestamp='20241227001')
failed_cases = execution.suite_details.filter(status='failed')
```

#### 查询某个套件下的所有用例
```python
suite_name = "LoginSuite"
cases = TestSuiteDetail.objects.filter(
    execution_id=execution_id,
    parent_suite=suite_name
)
```

---

## 四、数据流程图

```
┌──────────────────┐
│  Jenkins 构建    │
│  或本地执行测试   │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  生成 Allure     │
│  测试报告        │
│  (HTML + JSON)   │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  report_parser.py│ ← 解析器脚本
│  读取 JSON/CSV   │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  写入 MySQL      │
│  5张表           │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Django API      │
│  序列化返回前端  │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Vue 前端展示    │
│  ReportDetail.vue│
└──────────────────┘
```

---

## 五、总结

### 核心价值
1.  **TestExecution**: 提供整体视图，快速了解本次测试的健康度。
2.  **TestSuite**: 提供模块级视图，定位哪个模块有问题。
3.  **TestSuiteDetail**: 提供用例级视图，精确定位到失败的测试方法。
4.  **Category**: 提供缺陷分析视图，了解失败原因的分布。
5.  **FeatureScenario**: 提供业务视图，从功能角度看测试覆盖。

### 数据完整性
- 所有子表都通过 `execution_id` 关联到 `TestExecution`。
- 删除 `TestExecution` 时，会级联删除所有关联数据（`on_delete=CASCADE`）。
- `timestamp` 字段保证了每次执行的唯一性。
