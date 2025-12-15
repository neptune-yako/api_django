# OpenAPI 导入指南

## 📦 文件说明

我们提供了两种格式的 OpenAPI/Swagger 规范文件：

| 文件 | 格式 | 版本 | 推荐用途 |
|------|------|------|----------|
| `openapi.yaml` | YAML | OpenAPI 3.0.3 | ✅ **推荐** - Postman、Apifox、Swagger UI |
| `openapi.json` | JSON | OpenAPI 3.0.3 | Apifox、其他支持 JSON 的工具 |

---

## 🔧 导入到各类接口测试工具

### 1. Postman

#### 方式一：直接导入文件

1. 打开 Postman
2. 点击左上角 **Import** 按钮
3. 选择 **File** 标签
4. 点击 **Choose Files**
5. 选择 `openapi.yaml` 或 `openapi.json`
6. 点击 **Import**

#### 方式二：拖拽导入

1. 打开 Postman
2. 直接将 `openapi.yaml` 文件拖拽到 Postman 窗口
3. 确认导入

**导入后：**
- 会创建新的 Collection：**Jenkins Job Management API**
- 包含 11 个接口请求
- 按标签分组：Connection、Job Management、Job Operations

---

### 2. Apifox

#### 导入步骤

1. 打开 Apifox
2. 在项目中点击 **项目设置** → **导入数据**
3. 选择 **OpenAPI (Swagger)** 格式
4. 点击 **选择文件** 或 **URL 导入**
5. 选择 `openapi.yaml` 或 `openapi.json`
6. 选择导入模式（推荐：**智能导入**）
7. 点击 **确定**

**优势：**
- 自动生成接口文档
- 支持 Mock 数据
- 可以直接运行测试

---

### 3. Swagger UI（在线查看）

#### 方式一：本地文件

1. 访问 [Swagger Editor](https://editor.swagger.io/)
2. 点击 **File** → **Import file**
3. 选择 `openapi.yaml`
4. 在右侧查看 API 文档

#### 方式二：URL 导入（需要文件托管）

```
https://editor.swagger.io/?url=<你的openapi.yaml的URL>
```

---

### 4. Insomnia

#### 导入步骤

1. 打开 Insomnia
2. 点击 **Create** → **Import**
3. 选择 **From File**
4. 选择 `openapi.yaml` 或 `openapi.json`
5. 点击 **Import**

---

### 5. Hoppscotch（在线工具）

1. 访问 [Hoppscotch](https://hoppscotch.io/)
2. 点击 **Collections** → **Import**
3. 选择 **OpenAPI**
4. 粘贴 `openapi.yaml` 的内容或上传文件
5. 点击 **Import**

---

## ✅ 导入后的操作

### 1. 配置基础 URL

导入后，默认服务器地址是 `http://localhost:8000`

**如果端口不同：**
- Postman: 在 Collection 设置中修改 Variables → `baseUrl`
- Apifox: 在环境管理中修改服务器地址

### 2. 测试连接

导入后第一个测试：

```
GET /api/jenkins/test/
```

**预期响应**:
```json
{
    "code": 200,
    "message": "Jenkins连接成功",
    "data": { ... }
}
```

### 3. 快速测试流程

1. **测试连接** → `GET /api/jenkins/test/`
2. **获取 Jobs** → `GET /api/jenkins/jobs/`
3. **创建 Job** → `POST /api/jenkins/job/`
4. **获取 Job 信息** → `GET /api/jenkins/job/?job_name=xxx`
5. **删除 Job** → `DELETE /api/jenkins/job/?job_name=xxx`

---

## 📝 接口分组说明

导入后，接口会按以下标签分组：

### Connection（连接测试）
- 测试 Jenkins 连接

### Job Management（Job 管理）
- 获取所有 Jobs
- 创建 Job
- 获取 Job 信息/配置
- 更新 Job
- 删除 Job

### Job Operations（Job 操作）
- 校验 XML
- 复制 Job
- 启用/禁用 Job
- 触发构建

---

## 🔍 示例请求说明

### 创建 Job 示例

导入后，`POST /api/jenkins/job/` 接口已包含示例数据：

```json
{
    "job_name": "my-test-job",
    "config_xml": "<?xml version='1.1' encoding='UTF-8'?><project><description>测试</description></project>",
    "force": false
}
```

**可以直接点击 Send 测试！**

---

## ⚠️ 注意事项

### 1. 服务器必须运行

确保 Django 服务器正在运行：
```bash
cd backend
python manage.py runserver
```

### 2. 依赖已安装

确保已安装必要的依赖：
```bash
pip install python-jenkins lxml
```

### 3. XML 格式

在 JSON 中使用 XML 时，需要注意转义：
- 使用 `\n` 表示换行
- 或者将 XML 压缩为单行

---

## 🎯 推荐工具对比

| 工具 | 易用性 | 功能完整性 | Mock 支持 | 推荐度 |
|------|--------|-----------|-----------|--------|
| **Postman** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Apifox** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Insomnia** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| **Swagger UI** | ⭐⭐⭐ | ⭐⭐⭐ | ❌ | ⭐⭐⭐ |

---

## 📚 相关文档

- **详细测试指南**: [`POSTMAN_GUIDE.md`](./POSTMAN_GUIDE.md)
- **API 使用示例**: [`USAGE.md`](./USAGE.md)
- **依赖安装**: [`DEPENDENCIES.md`](./DEPENDENCIES.md)

---

祝测试顺利！🎉
