"""
Allure 报告相关视图
- Allure 报告代理（隐藏 Jenkins 界面）
"""
import requests
import logging
from urllib.parse import unquote
from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.views import APIView
from ..utils import R, ResponseCode, ResponseMessage

logger = logging.getLogger(__name__)

# Allure 报告代理
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
        """
        # URL 解码
        job_name = unquote(job_name)
        
        # 构造 Jenkins Allure URL
        from ..jenkins_client import JENKINS_URL
        allure_url = f"{JENKINS_URL}/job/{job_name}/{build_number}/allure/{file_path}"
        
        try:
            # 请求 Jenkins
            response = requests.get(allure_url, timeout=10, allow_redirects=False)
            
            if response.status_code == 404:
                # 返回自定义 404
                if not file_path or file_path == 'index.html':
                    return render(request, 'jenkins_integration/allure_404.html', status=404)
                else:
                    return HttpResponse('Not Found', status=404)
            
            # 处理响应
            content_type = response.headers.get('Content-Type', '')
            
            if 'text/html' in content_type:
                # 注入自定义样式
                html = response.text
                custom_html = self.inject_custom_style(html)
                return HttpResponse(custom_html, content_type='text/html')
            else:
                resp = HttpResponse(response.content, content_type=content_type)
                resp['Cache-Control'] = 'public, max-age=86400'
                return resp
                
        except requests.RequestException as e:
            logger.error(f"请求 Allure 报告失败: {str(e)}")
            return render(request, 'jenkins_integration/allure_error.html', {
                'error': str(e)
            }, status=500)
    
    def inject_custom_style(self, html):
        custom_css = """
        <style>
            .app__header { display: none !important; }
            :root {
                --primary-color: #1890ff;
                --bg-color: #f5f5f5;
            }
            .pane__section { background: var(--bg-color); }
        </style>
        """
        if '</head>' in html:
            html = html.replace('</head>', f'{custom_css}</head>')
        return html


class SyncBuildResultView(APIView):
    """
    同步构建结果 API
    当 Jenkins 构建完成后调用此接口，触发 Allure 数据解析和入库
    """
    
    def post(self, request):
        job_name = request.data.get('job_name')
        build_number = request.data.get('build_number')
        
        if not job_name or not build_number:
            return R.bad_request("Missing job_name or build_number")
            
        try:
            from ..models import JenkinsJob, AllureReport
            job = JenkinsJob.objects.filter(name=job_name).first()
            if not job:
                return R.error(
                    code=ResponseCode.JENKINS_JOB_NOT_FOUND,
                    message=f"Job '{job_name}' not found in database"
                )
            
            allure_url = job.get_allure_url(build_number)
            
            from ..services.allure_sync import AllureSyncService
            success, msg = AllureSyncService.sync_report_data(job, int(build_number), allure_url)
            
            if success:
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
                        "pass_rate": report.pass_rate,
                        "created_at": report.create_time.strftime('%Y-%m-%d %H:%M:%S') if report.create_time else None
                    }
                return R.success(message=f"Allure data synced successfully for build #{build_number}", data=data)
            else:
                return R.error(message=f"Failed to sync Allure data: {msg}")
                
        except Exception as e:
            logger.error(f"Sync API Error: {str(e)}")
            return R.internal_error(str(e))
