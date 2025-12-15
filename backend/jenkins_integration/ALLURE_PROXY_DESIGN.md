# Allure 报告代理方案设计

## 📋 **需求分析**

### 客户需求
1. ✅ 使用 iframe 显示 Allure 报告
2. ✅ UI 风格与前端系统一致（需要修改样式）
3. ✅ **不能让用户看到任何 Jenkins 页面**
4. ✅ 没有 Allure 时显示自定义 404 页面

---

## 🎯 **解决方案：后端代理 + 样式注入**

### 架构设计

```
前端 iframe                后端 Django                    Jenkins
────────────────────────────────────────────────────────────────
iframe src="/allure-proxy/  
  item-test/8/"
                    ↓
                代理视图 (AllureProxyView)
                    ↓
                1. 检查 Allure 是否存在
                    ↓
                有？ ────→ 2. 请求 Jenkins Allure
                              ↓
                         3. 修改 HTML（注入自定义样式）
                              ↓
                         4. 返回修改后的 HTML
                              
                无？ ────→ 返回自定义 404 页面
```

### ⭐ **URL 设计：使用路径参数**

**优势**：
- ✅ RESTful 风格，URL 更美观
- ✅ **Allure 内部链接自动生效**（无需修改 HTML）
- ✅ 浏览器缓存更友好
- ✅ 符合资源层级结构

**URL 格式**：
```
/api/jenkins/allure-proxy/{job_name}/{build_number}/{file_path}

示例：
- /api/jenkins/allure-proxy/item-test/8/                    # 主页
- /api/jenkins/allure-proxy/item-test/8/index.html          # 首页
- /api/jenkins/allure-proxy/item-test/8/data/suites.json    # 数据文件
- /api/jenkins/allure-proxy/item-test/8/styles/main.css     # 样式文件
```

**为什么路径参数更好？**

当 Allure 报告内部有相对链接时：
```html
<!-- Allure HTML 中的相对链接 -->
<a href="data/suites.json">查看套件</a>
```

浏览器会自动基于当前 URL 补全：
```
当前页面: /api/jenkins/allure-proxy/item-test/8/index.html
相对链接: data/suites.json
         ↓
自动补全: /api/jenkins/allure-proxy/item-test/8/data/suites.json ✅ 完美！
```

如果用查询字符串 `?job_name=xxx`，相对链接会失效！❌

---

## 🔧 **实现方案**

### 方案 1：完全代理（推荐）⭐⭐⭐⭐⭐

**优点**：
- ✅ 完全控制：可以修改任何内容
- ✅ 安全：用户完全看不到 Jenkins
- ✅ 自定义 404：返回自己的错误页面
- ✅ 样式注入：可以覆盖 Allure 样式

**实现步骤**：

#### 1. 新增代理视图

```python
# views.py
import requests
from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.views import APIView
from urllib.parse import unquote

class AllureProxyView(APIView):
    """
    Allure 报告代理
    - 隐藏 Jenkins 界面
    - 注入自定义样式
    - 处理 404
    - 使用路径参数设计
    """
   
    def get(self, request, job_name, build_number, file_path=''):
        """
        使用路径参数接收参数
        
        参数:
            job_name: Job 名称（路径参数）
            build_number: 构建编号（路径参数）
            file_path: Allure 内部文件路径（可选路径参数）
        
        URL 示例:
            - /api/jenkins/allure-proxy/item-test/8/
            - /api/jenkins/allure-proxy/item-test/8/index.html
            - /api/jenkins/allure-proxy/item-test/8/data/suites.json
        """
        # URL 解码（处理 Job 名称中的特殊字符）
        job_name = unquote(job_name)
        
        # 1. 构造完整 URL
        from .jenkins_client import JENKINS_URL
        allure_url = f"{JENKINS_URL}/job/{job_name}/{build_number}/allure/{file_path}"
        
        # 2. 请求 Jenkins
        try:
            response = requests.get(allure_url, timeout=10, allow_redirects=False)
            
            if response.status_code == 404:
                # 返回自定义 404（仅对主页面）
                if not file_path or file_path == 'index.html':
                    return render(request, 'jenkins_integration/allure_404.html', status=404)
                else:
                    # 其他资源直接返回 404
                    return HttpResponse('Not Found', status=404)
            
            # 3. 处理响应
            content_type = response.headers.get('Content-Type', '')
            
            if 'text/html' in content_type:
                # HTML 内容：注入自定义样式
                html = response.text
                custom_html = self.inject_custom_style(html)
                return HttpResponse(custom_html, content_type='text/html')
            else:
                # 其他资源（CSS、JS、图片等）直接返回
                resp = HttpResponse(response.content, content_type=content_type)
                # 静态资源缓存 1 天
                resp['Cache-Control'] = 'public, max-age=86400'
                return resp
                
        except requests.RequestException as e:
            logger.error(f"请求 Allure 报告失败: {str(e)}")
            return render(request, 'jenkins_integration/allure_error.html', {
                'error': str(e)
            }, status=500)
    
    def inject_custom_style(self, html):
        """
        在 Allure HTML 中注入自定义样式
        """
        custom_css = """
        <style>
            /* 隐藏 Allure 默认的 header/footer */
            .app__header { display: none !important; }
            
            /* 自定义主题色 */
            :root {
                --primary-color: #1890ff;  /* 替换为你的主色调 */
                --bg-color: #f5f5f5;
            }
            
            /* 其他自定义样式 */
            .pane__section { 
                background: var(--bg-color);
            }
        </style>
        """
        
        # 在 </head> 前插入
        if '</head>' in html:
            html = html.replace('</head>', f'{custom_css}</head>')
        
        return html
```

#### 2. 创建模板目录

在 `jenkins_integration/` 下创建 `templates/jenkins_integration/` 目录：

```
jenkins_integration/
├── templates/
│   └── jenkins_integration/
│       ├── allure_404.html
│       └── allure_error.html
```

#### 3. 自定义 404 页面

```html
<!-- templates/jenkins_integration/allure_404.html -->
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>报告不存在</title>
    <style>
        body {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .error-container {
            text-align: center;
            color: white;
            padding: 40px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            backdrop-filter: blur(10px);
        }
        .error-icon {
            font-size: 120px;
            margin: 0;
        }
        .error-message {
            font-size: 24px;
            margin: 20px 0;
            font-weight: 500;
        }
        .error-hint {
            font-size: 16px;
            opacity: 0.8;
            line-height: 1.6;
        }
        .back-button {
            margin-top: 30px;
            padding: 12px 24px;
            background: white;
            color: #667eea;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
        }
        .back-button:hover {
            background: #f0f0f0;
        }
    </style>
</head>
<body>
    <div class="error-container">
        <div class="error-icon">📊</div>
        <p class="error-message">该构建没有生成 Allure 报告</p>
        <p class="error-hint">
            请确保构建配置中包含 Allure 插件<br>
            并且测试已成功执行
        </p>
        <a href="javascript:window.parent.postMessage('close-allure', '*')" class="back-button">
            返回
        </a>
    </div>
</body>
</html>
```

#### 4. 错误页面

```html
<!-- templates/jenkins_integration/allure_error.html -->
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>加载失败</title>
    <style>
        body {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
        }
        .error-container {
            text-align: center;
            color: white;
            padding: 40px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            backdrop-filter: blur(10px);
        }
        .error-icon {
            font-size: 120px;
            margin: 0;
        }
        .error-message {
            font-size: 24px;
            margin: 20px 0;
        }
        .error-details {
            font-size: 14px;
            opacity: 0.8;
            margin-top: 10px;
            padding: 10px;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <div class="error-container">
        <div class="error-icon">⚠️</div>
        <p class="error-message">报告加载失败</p>
        <div class="error-details">
            错误信息: {{ error }}
        </div>
    </div>
</body>
</html>
```

#### 5. URL 配置

```python
# urls.py
from django.urls import path, re_path

urlpatterns = [
    # ... 其他路由
    
    # Allure 代理 - 使用路径参数
    # 主页（无文件路径）
    path('api/jenkins/allure-proxy/<str:job_name>/<int:build_number>/',
         views.AllureProxyView.as_view(), 
         name='allure-proxy-index'),
    
    # 带文件路径（匹配任意路径，包括多级目录）
    re_path(r'^api/jenkins/allure-proxy/(?P<job_name>[^/]+)/(?P<build_number>\d+)/(?P<file_path>.+)$',
            views.AllureProxyView.as_view(), 
            name='allure-proxy-file'),
]
```

**路由说明**：
- 第一条路由：匹配主页 `/api/jenkins/allure-proxy/item-test/8/`
- 第二条路由：匹配所有文件 `/api/jenkins/allure-proxy/item-test/8/data/suites.json`
- 使用 `re_path` 支持任意深度的文件路径（`file_path` 可以包含 `/`）

**处理特殊字符**：
```python
# 如果 Job 名称包含特殊字符（如斜杠）
# 前端需要 URL 编码
const jobName = 'project/sub-project';
const encodedJobName = encodeURIComponent(jobName);
const url = `/api/jenkins/allure-proxy/${encodedJobName}/8/`;

# 后端在 view 中自动解码（已处理）
job_name = unquote(job_name)
```

#### 6. 前端使用

```html
<!-- 前端代码 -->
<div class="allure-report-container">
    <iframe 
        id="allure-iframe"
        src="/api/jenkins/allure-proxy/item-test-allure/8/"
        width="100%" 
        height="800px"
        frameborder="0"
    ></iframe>
</div>

<script>
// 动态构造 URL
function showAllureReport(jobName, buildNumber) {
    // 如果 Job 名称包含特殊字符，需要编码
    const encodedJobName = encodeURIComponent(jobName);
    const url = `/api/jenkins/allure-proxy/${encodedJobName}/${buildNumber}/`;
    
    document.getElementById('allure-iframe').src = url;
}

// 监听 iframe 内的消息（如"返回"按钮）
window.addEventListener('message', (event) => {
    if (event.data === 'close-allure') {
        // 关闭 Allure 展示
        document.querySelector('.allure-report-container').style.display = 'none';
    }
});

// 使用示例
showAllureReport('item-test-allure', 8);
</script>
```

---

## 🎨 **样式定制示例**

### 完全自定义主题

```python
def inject_custom_style(self, html):
    """完整的样式定制"""
    custom_css = """
    <style>
        /* ========== 1. 隐藏不需要的元素 ========== */
        .app__header,
        .app__sidebar { 
            display: none !important; 
        }
        
        /* ========== 2. 调整布局 ========== */
        .app__content {
            margin-left: 0 !important;
            padding: 20px;
        }
        
        /* ========== 3. 自定义颜色 ========== */
        :root {
            --primary-color: #1890ff;
            --success-color: #52c41a;
            --error-color: #ff4d4f;
            --warning-color: #faad14;
            --bg-color: #ffffff;
            --border-color: #d9d9d9;
        }
        
        /* ========== 4. 按钮样式 ========== */
        .button,
        button {
            background: var(--primary-color) !important;
            border-radius: 4px !important;
            border: none !important;
        }
        
        .button:hover,
        button:hover {
            opacity: 0.8;
        }
        
        /* ========== 5. 卡片样式 ========== */
        .widget,
        .pane {
            border-radius: 8px !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
            border: 1px solid var(--border-color) !important;
        }
        
        /* ========== 6. 表格样式 ========== */
        table {
            border-radius: 4px !important;
            overflow: hidden !important;
        }
        
        /* ========== 7. 图标颜色 ========== */
        .status-passed {
            color: var(--success-color) !important;
        }
        
        .status-failed {
            color: var(--error-color) !important;
        }
        
        .status-broken {
            color: var(--warning-color) !important;
        }
    </style>
    """
    
    return html.replace('</head>', f'{custom_css}</head>')
```

---

## ⚡ **性能优化**

### 1. 静态资源缓存

```python
class AllureProxyView(APIView):
    def get(self, request):
        # ...
        
        # 静态资源（CSS/JS/图片）缓存 1 天
        if not 'text/html' in content_type:
            response = HttpResponse(response.content, content_type=content_type)
            response['Cache-Control'] = 'public, max-age=86400'
            return response
```

### 2. HTML 缓存（可选）

```python
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

class AllureProxyView(APIView):
    @method_decorator(cache_page(60 * 5))  # 缓存 5 分钟
    def get(self, request):
        # ...
```

---

## 🔒 **安全考虑**

### 1. 防止 SSRF 攻击

```python
from urllib.parse import urlparse

class AllureProxyView(APIView):
    ALLOWED_JENKINS_HOST = 'mg.morry.online'
    
    def get(self, request):
        # 验证请求的 URL
        from .jenkins_client import JENKINS_URL
        parsed_url = urlparse(JENKINS_URL)
        
        if parsed_url.hostname != self.ALLOWED_JENKINS_HOST:
            return HttpResponse('Invalid Jenkins host', status=403)
        
        # ...
```

### 2. 路径遍历防护

```python
def get(self, request):
    path = request.GET.get('path', '')
    
    # 禁止路径遍历
    if '..' in path or path.startswith('/'):
        return HttpResponse('Invalid path', status=403)
    
    # 只允许 Allure 相关路径
    allowed_extensions = ['.html', '.css', '.js', '.json', '.png', '.svg']
    if path and not any(path.endswith(ext) for ext in allowed_extensions):
        return HttpResponse('Invalid file type', status=403)
```

### 3. 添加请求超时

```python
response = requests.get(
    allure_url, 
    timeout=10,  # 10秒超时
    allow_redirects=False  # 禁止重定向
)
```

---

## 📊 **完整流程**

```
1. 用户点击"查看 Allure 报告"
   ↓
2. 前端加载 iframe: /api/jenkins/allure-proxy/?job_name=xxx&build_number=8
   ↓
3. Django AllureProxyView 处理请求
   ↓
4. 请求 Jenkins: http://mg.morry.online/job/xxx/8/allure/
   ↓
5. Jenkins 响应
   ├─ 200 → 注入自定义样式 → 返回修改后的 HTML
   └─ 404 → 返回自定义 404 页面
   ↓
6. iframe 显示内容（用户看不到任何 Jenkins 界面）
```

---

## ✅ **优势总结**

| 需求 | 解决方案 | 状态 |
|------|----------|------|
| iframe 显示 | 通过代理实现 | ✅ |
| UI 统一 | 注入自定义 CSS | ✅ |
| 隐藏 Jenkins | 完全代理，用户看不到 | ✅ |
| 自定义 404 | 返回自己的页面 | ✅ |
| 功能完整 | Allure 所有功能都可用 | ✅ |
| 安全性 | SSRF 防护、路径验证 | ✅ |
| 性能 | 静态资源缓存 | ✅ |

---

## 🚀 **实施步骤**

1. ✅ 创建 `AllureProxyView` 视图
2. ✅ 创建 `templates/jenkins_integration/` 目录
3. ✅ 添加 `allure_404.html` 和 `allure_error.html`
4. ✅ 配置 URL 路由
5. ✅ 前端集成 iframe
6. ✅ 测试功能
7. ✅ 优化样式
8. ✅ 部署上线

---

**准备好开始实施了吗？** 🎉
