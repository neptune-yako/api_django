# TestSuiteDetail 表结构与价值分析

## 1. 这个表的作用 (Purpose)
`test_suite_details` 表（对应 Django 模型 `TestSuiteDetail`）的主要作用是**存储自动化测试中“用例级”的详细执行日志**。

*   **原子级记录**：与只记录“统计数据”的 `TestSuite` 表不同，`TestSuiteDetail` 为每一个执行的测试方法（Test Method）创建一条独立的记录。
*   **多维数据**：它记录了用例的层级（父件/子件）、定位（类/方法）、状态（通过/失败/跳过）以及精准的耗时。

## 2. 能帮助什么 (Business Value)
引入这张表后，测试平台将具备以下深层分析能力：

1.  **精准定位问题 (Pinpoint Failures)**
    *   **之前**：只能看到“登录套件挂了 2 个用例”，但不知道是哪两个。
    *   **现在**：可以直接查询出“是 `TestLogin` 类下的 `test_wrong_password` 方法失败了”，并且可以直接看到该用例的具体报错信息。

2.  **性能瓶颈分析 (Performance Profiling)**
    *   通过 `duration_in_ms` 字段，可以对所有测试用例的耗时进行排序，找出拖慢整个构建流程的“慢用例”并进行优化。

3.  **构建全景报告 (Full-View Reporting)**
    *   支持生成类似 Allure 的树状图报告，展示 `Parent Suite -> Suite -> Test Class -> Test Method` 的完整层级，提供更好的阅读体验。

## 3. 补充了什么部分 (Supplement)
在现有的数据模型中，这张表填补了**“统计数据”与“具体日志”之间的空白**。

*   **Level 1 - TestExecution**: 任务级（某次构建整体成功/失败）。
*   **Level 2 - TestSuite**: 模块级（某个文件/套件的通过率）。
*   **Level 3 - TestSuiteDetail (新增补充)**: **方法级**（具体某个函数的执行详情）。

它完善了数据颗粒度，使得从宏观统计到微观诊断的链路被打通了。

## 4. 目前的前端使用了什么 Models？ (Current Frontend Usage)
需要注意的是，**目前的**前端页面 (`Report.vue` 和 `Record.vue`) **尚未** 对接这个新添加的表。它们使用的是旧的一套模型：

*   **列表页 (`/record`)**:
    *   使用的是 `backend/plan/models.py` 中的 **`Record`** 模型。
    *   用于展示：计划名称、运行状态、通过率概览。

*   **详情页 (`/record/report/:id`)**:
    *   使用的是 `backend/plan/models.py` 中的 **`Report`** 模型。
    *   机制：`Report` 表中有一个大字段 `info` (JSONField)，测试结果是以 **JSON 字符串** 的形式存储在里面的，而不是拆分成独立的数据库行。

**结论**：`test_report` 应用（包含 `TestSuiteDetail`）是为您未来的**Jenkins 集成**和**新版高级报告**准备的后端架构，目前的前端页面还需要进行相应的重构或开发新页面来展示这些新数据。
