"""
Allure 报告相关视图
- Allure 报告 URL 生成
- Allure 报告代理（隐藏 Jenkins 界面）
"""
import requests
import logging
from urllib.parse import unquote
from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.views import APIView

from .utils import R, ResponseCode, ResponseMessage

logger = logging.getLogger(__name__)


class JenkinsBuildAllureView(APIView):
    """获取 Allure 报告 URL"""
    
    def get(self, request):
        """
        获取指定构建的 Allure 报告 URL
        
        Query Parameters:
            job_name: Job 名称（必需）
            build_number: 构建编号（必需）
            
        Returns:
            {
                "code": 200,
                "message": "Allure 报告 URL 已生成",
                "data": {
                    "allure_url": "...",
                    "job_name": "...",
                    "build_number": ...
                }
            }
        """
        try:
            job_name = request.query_params.get('job_name')
            build_number = request.query_params.get('build_number')
            
            # 参数验证
            if not job_name or not build_number:
                return R.bad_request(
                    message=ResponseMessage.PARAM_MISSING + ': job_name 或 build_number'
                )
            
            try:
                build_number = int(build_number)
            except ValueError:
                return R.bad_request(message='build_number 必须是整数')
            
            # 获取 Allure 报告 URL
            from .jenkins_client import get_allure_report_url
            success, message, data = get_allure_report_url(job_name, build_number)
            
            if success:
                return R.success(message=message, data=data)
            else:
                return R.jenkins_error(message=message, data=data)
                
        except Exception as e:
            error_msg = f"获取 Allure 报告失败: {str(e)}"
            logger.error(error_msg)
            return R.internal_error(message=error_msg)


class AllureProxyView(APIView):
    """
    Allure 报告代理
    - 隐藏 Jenkins 界面
    - 注入自定义样式
    - 自定义 404 页面
    - 使用路径参数设计
    """
    
    def get(self, request, job_name, build_number, file_path=''):
        """
        代理 Jenkins Allure 报告
        
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
        
        # 构造 Jenkins Allure URL
        from .jenkins_client import JENKINS_URL
        allure_url = f"{JENKINS_URL}/job/{job_name}/{build_number}/allure/{file_path}"
        
        try:
            # 请求 Jenkins
            response = requests.get(allure_url, timeout=10, allow_redirects=False)
            
            if response.status_code == 404:
                # 返回自定义 404（仅对主页面）
                if not file_path or file_path == 'index.html':
                    return render(request, 'jenkins_integration/allure_404.html', status=404)
                else:
                    # 其他资源直接返回 404
                    return HttpResponse('Not Found', status=404)
            
            # 处理响应
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
                --primary-color: #1890ff;
                --bg-color: #f5f5f5;
            }
            
            /* 自定义样式 */
            .pane__section { 
                background: var(--bg-color);
            }
        </style>
        """
        
        # 在 </head> 前插入
        if '</head>' in html:
            html = html.replace('</head>', f'{custom_css}</head>')
        
        return html


class SyncBuildResultView(APIView):
    """
    同步构建结果 API
    当 Jenkins 构建完成后调用此接口，触发 Allure 数据解析和入库
    """
    
    def post(self, request):
        """
        接收 job_name 和 build_number，同步 Allure 数据
        """
        job_name = request.data.get('job_name')
        build_number = request.data.get('build_number')
        
        # 验证参数
        if not job_name or not build_number:
            return R.bad_request("Missing job_name or build_number")
            
        try:
            # 1. 获取对应的 Job
            # 注意：这里假设 Job 已经存在于数据库中
            from .models import JenkinsJob, AllureReport
            job = JenkinsJob.objects.filter(name=job_name).first()
            if not job:
                return R.error(
                    code=ResponseCode.JENKINS_JOB_NOT_FOUND,
                    message=f"Job '{job_name}' not found in database"
                )
            
            # 2. 获取 Allure URL
            allure_url = job.get_allure_url(build_number)
            
            # 3. 调用服务进行同步
            from .services.allure_sync import AllureSyncService
            # 注意：AllureReport 的 build_number 是 IntegerField
            success, msg = AllureSyncService.sync_report_data(job, int(build_number), allure_url)
            
            if success:
                # 获取同步后的报告数据
                report = AllureReport.objects.filter(job=job, build_number=build_number).first()
                data = None
                if report:
                    data = {
                        "report_id": report.id,
                        "job_name": job.name,
                        "build_number": report.build_number,
                        "total": report.total,
                        "passed": report.passed,
                        "failed": report.failed,
                        "broken": report.broken,
                        "skipped": report.skipped,
                        "pass_rate": report.pass_rate,
                        "duration": report.duration,
                        "created_at": report.create_time.strftime('%Y-%m-%d %H:%M:%S') if report.create_time else None
                    }
                return R.success(message=f"Allure data synced successfully for build #{build_number}", data=data)
            else:
                return R.error(message=f"Failed to sync Allure data: {msg}")
                
        except Exception as e:
            logger.error(f"Sync API Error: {str(e)}")
            return R.internal_error(str(e))
