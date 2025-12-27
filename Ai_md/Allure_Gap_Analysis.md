# 差异分析：当前 Report 页面 vs 标准 Allure 报告

## 1. 背景
**目标**：开发一个类似 Allure 报告的详情页面。  
**现状**：`frontend/src/views/jenkins/report/ReportDetail.vue` 提供了一个基于统计数据的仪表盘。

本文档详细分析当前实现与目标（仿 Allure 报告）之间的差异，识别核心缺失部分。

## 2. 现状分析 (`ReportDetail.vue`)
目前页面主要展示的是**宏观统计数据**，数据来源仅限于 `test_suites` 和 `feature_scenarios` 这样的汇总表。

*   **展示维度**：
    *   📊 **概览**：通过率、总数、时间。
    *   📋 **套件列表 (Tab)**：仅显示套件名称和该套件的统计（通过x个/失败x个）。**无法点击进入**。
    *   🏷️ **类别/场景 (Tab)**：分类统计列表。
*   **核心缺陷**：数据截止到“文件级”，用户无法看到“方法级”详情。

## 3. 标准 Allure 报告的核心特性
一个标准的 Allure 报告核心价值在于从“宏观”到“微观”的丝滑体验：

1.  **Overview (概览)**: 丰富的图表（趋势图、分布图、时间线）。
2.  **Tree View (树状导航)**: Suites/Packages 树，支持多级展开 (Package -> Class -> Method)。
3.  **Test Body (用例详情)**:
    *   **Description**: 用例描述。
    *   **Steps**: 执行步骤（每一步的输入输出）。
    *   **Attachments**: 截图、日志、HTML 源码、视频。
    *   **Parameters**: 如果是参数化用例，显示具体的参数值。
    *   **Links**: 关联的 Jira/TMS 链接。

## 4. 差距分析 (Gap Analysis) - 缺失的部分

我们将差距分为 **致命缺失 (Critical)** 和 **体验缺失 (UX)**。

### 🚨 致命缺失 (必须补充)
1.  **用例列表 (Test Cases List)**
    *   **现状**：只有 Suite 行，无法展开。
    *   **目标**：在 Suite 点击后，应展示该 Suite 下的所有 `TestCase` (使用我们新加的 `TestSuiteDetail` 表)。
2.  **用例执行详情 (Execution Details)**
    *   **现状**：无。
    *   **目标**：点击某个 TestCase，右侧或弹窗展示具体的报错信息 (Stacktrace)、断言结果。
3.  **步骤与附件 (Steps & Attachments)**
    *   **现状**：无。
    *   **目标**：Allure 的灵魂。需要展示测试步骤 (`@allure.step`) 和 失败截图/日志附件。
    *   *注：这需要后端解析 Allure 的 `attachments` 目录下文件，并在前端提供下载或预览接口。*

### 🎨 体验缺失 (优化项)
1.  **层级导航 (Hierarchy)**
    *   Allure 使用左侧树状导航，当前使用的是平铺的 Table。树状结构更适合管理大量用例。
2.  **时间线试图 (Timeline)**
    *   直观展示并发执行的情况，当前只有数字统计。
3.  **高级过滤 (Filtering)**
    *   Allure 支持一键只看 "Failed" 或 "Broken" 的用例，当前只有静态表格。

## 5. 改造建议 roadmap

为了达到“仿 Allure”的效果，建议按以下阶段进行修改：

### Phase 1: 基础下钻 (Drill-down)
*   **后端**: 完善 API，支持根据 Suite ID 查询 `TestSuiteDetail` 列表。
*   **前端**: 改造 Suite 表格，支持“展开行”或“点击跳转”。
*   **效果**: 用户可以点开一个套件，看到里面的具体用例，以及每个用例的**耗时**和**状态**。

### Phase 2: 详情展示 (Detail View)
*   **页面**: 增加一个 Drawer (抽屉) 或 Dialog。
*   **内容**: 点击用例时弹出，展示 `Name`, `Status`, `Duration`, `Error Log` (Stacktrace)。
*   **数据源**: `TestSuiteDetail` 表目前已包含这些基础信息。

### Phase 3: 完美复刻 (Steps & Attachments)
*   **后端**: 需要进一步解析 Allure 的 `attachments` 和 `steps` 数据（目前可能未入库，需要存在文件服务器或对象存储中）。
*   **前端**: 在详情抽屉中渲染步骤树和图片/日志预览。

## 6. 总结
目前的 `ReportDetail.vue` 相当于 Allure 的 **"Overview" 面板**。要变成完整的 Allure 报告，我们需要**基于 `TestSuiteDetail` 表开发 "Suites" 面板和 "Test Body" 面板**。
