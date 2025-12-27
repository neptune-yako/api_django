# 修改计划：Debug 页面接口请求失败修复

## 1. 报错 (Error)
在前台 **Debug (接口调试)** 页面运行接口用例（例如 `https://jsonplaceholder.typicode.com/posts/1`）时，系统报错：
> `SyntaxError: Unexpected token " in JSON at position 0`

同时，**Case (接口用例)** 页面运行相同的接口和参数却能成功。

## 2. 问题分析 (Problem Analysis)
通过对比 `Debug.vue` 和 `CaseEditor.vue` 的代码以及后端处理逻辑，发现问题的根本原因在于 **数据类型的初始化不一致**。

1.  **前端差异**：
    *   **Case 页面**：数据是从后端 API 获取的，Django `JSONField` 序列化会将 JSON 字符串转为 **Python 字典 (Dict)**，最终以 **Javascript 对象 (Object)** 的形式传递给前端。因此 `CaseEditor.vue` 中的 `request.json` 等字段是对象 `{}`。
    *   **Debug 页面**：在 `Debug.vue` 中，`caseData` 是硬编码初始化的，其中 `headers`, `json`, `data`, `params` 被初始化为了 **字符串** `"{}"`。

2.  **后端影响** (`backend/ApiEngine/basecase.py`)：
    *   后端接收参数时，如果字段是字符串，`requests` 库在发送请求时（特别是 `json` 参数），会将在这个字符串再次编码。
    *   **结果**：原本应该是 JSON 对象 `{...}` 的 Request Body，变成了一个包含 JSON 字符串的字符串 `"{\"...\"}"`。
    *   **后果**：目标服务器（如 `jsonplaceholder`）无法解析这个错误的 Payload 格式，返回了 500 或 400 错误（通常返回 HTML 报错页面）。

3.  **报错原因**：
    *   前端 `Editor.vue` 或 `Result.vue` 尝试用 `JSON.parse()` 解析目标接口返回的 HTML 报错页面（而非预期的 JSON 响应），从而抛出 `SyntaxError`。

## 3. 解决思路 (Solution Approach)
需将 `Debug.vue` 中的数据初始化逻辑与 `CaseEditor.vue` 保持一致，即使用 **对象 (Object)** 而非 **字符串 (String)** 来初始化请求参数。

*   `Editor.vue` 组件通过 `lang="json"` 属性已经能够很好地处理 Object 类型（会自动 `JSON.stringify` 显示，编辑后 `JSON.parse` 返回）。
*   只要传入的是 Object，组件交互和后端接口序列化都能正常工作。

## 4. 修改方案 (Modification Scheme)

**目标文件**：`frontend/src/views/debug/Debug.vue`

**修改内容**：
找到 `caseData` 的 `reactive` 初始化代码块，将所有 JSON 相关字段的默认值从字符串 `"{}"` 修改为对象 `{}`。

```javascript
/* 修改前 */
const caseData = reactive({
  // ...
  headers: "{}",
  request: {
    json: '{}',
    data: '{}',
    params: '{}'
  },
  // ...
})

/* 修改后 */
const caseData = reactive({
  // ...
  headers: {},        // 改为对象
  request: {
    json: {},         // 改为对象
    data: {},         // 改为对象
    params: {}        // 改为对象
  },
  // ...
})
```

**验证计划**：
1.  修改代码后，刷新 Debug 页面。
2.  输入 `https://jsonplaceholder.typicode.com/posts/1`。
3.  点击“运行”。
4.  确认不再报错，且能看到正确的 JSON 响应结果。


### 完整报错
```
SyntaxError: Unexpected token " in JSON at position 0
    at JSON.parse (<anonymous>)
    at createStrictSyntaxError (/app/node_modules/body-parser/lib/types/json.js:158:10)
    at parse (/app/node_modules/body-parser/lib/types/json.js:83:15)
    at /app/node_modules/body-parser/lib/read.js:121:18
    at invokeCallback (/app/node_modules/body-parser/node_modules/raw-body/index.js:224:16)
    at done (/app/node_modules/body-parser/node_modules/raw-body/index.js:213:7)
    at IncomingMessage.onEnd (/app/node_modules/body-parser/node_modules/raw-body/index.js:273:7)
    at IncomingMessage.emit (node:events:525:35)
    at endReadableNT (node:internal/streams/readable:1358:12)
    at processTicksAndRejections (node:internal/process/task_queues:83:21)
```