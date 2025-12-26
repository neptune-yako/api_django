from rest_framework.views import APIView
from ..utils import R, ResponseCode, ResponseMessage
import logging

logger = logging.getLogger(__name__)
# 构建管理
class JenkinsBuildLatestView(APIView):
    """查询最新构建状态（用于前端轮询）"""
    
    def get(self, request):
        try:
            job_name = request.query_params.get('job_name')
            if not job_name:
                return R.bad_request(message=ResponseMessage.PARAM_MISSING + ': job_name')
            
            from ..jenkins_client import get_job_info, get_build_info
            
            # 1. 获取 Job 信息
            success, message, data = get_job_info(job_name)
            if not success:
                if 'not exist' in message.lower() or '不存在' in message:
                    return R.error(message=message, code=ResponseCode.JENKINS_JOB_NOT_FOUND)
                return R.jenkins_error(message=message)
            
            # 2. 检查是否有构建记录
            last_build = data.get('lastBuild')
            if not last_build:
                return R.success(message='该 Job 还没有构建记录', data=None)
            
            # 3. 获取最新构建的详细信息
            last_build_number = last_build.get('number')
            build_success, build_msg, build_data = get_build_info(job_name, last_build_number)
            
            if not build_success:
                return R.jenkins_error(message=build_msg)
            
            # 4. 解析构建状态
            result = build_data.get('result')
            building = build_data.get('building')
            duration = build_data.get('duration')
            
            if building:
                status_text = '正在构建中'
            elif result == 'SUCCESS':
                status_text = '构建成功'
            elif result == 'FAILURE':
                status_text = '构建失败'
            elif result == 'ABORTED':
                status_text = '构建已中止'
            elif result == 'UNSTABLE':
                status_text = '构建不稳定'
            else:
                status_text = '未知状态'
            
            return R.success(
                message=f'最新构建 #{last_build_number} - {status_text}',
                data={
                    'build_number': last_build_number,
                    'result': result,
                    'building': building,
                    'duration': duration,
                    'duration_text': f"{duration / 1000:.2f}秒" if duration else None,
                    'status_text': status_text,
                    'url': build_data.get('url'),
                    'timestamp': build_data.get('timestamp')
                }
            )
        except Exception as e:
            return R.internal_error(message=str(e))


class JenkinsBuildAllureView(APIView):
    """获取 Allure 报告 URL (Wrapper)"""
    def get(self, request):
        # 委托给 allure_views 中的 Allure URL 生成逻辑
        # 但既然用户希望 build_views 包含 Allure Report logic, 
        # 我们这里直接调用 jenkins_client.get_allure_report_url (或者保持一致性)
        # 这里为了保持 clean，我直接把 logic 搬过来，不再依赖 allure_views.
        # 不过 allure_views.py 还有 AllureProxyView.
        # 让我们把 generate url logic 放在这里.
        try:
            job_name = request.query_params.get('job_name')
            build_number = request.query_params.get('build_number')
            
            if not job_name or not build_number:
                return R.bad_request(message=ResponseMessage.PARAM_MISSING + ': job_name 或 build_number')
            
            try:
                build_number = int(build_number)
            except ValueError:
                return R.bad_request(message='build_number 必须是整数')
            
            from ..jenkins_client import get_allure_report_url
            success, message, data = get_allure_report_url(job_name, build_number)
            
            if success:
                return R.success(message=message, data=data)
            else:
                return R.jenkins_error(message=message, data=data)
        except Exception as e:
            return R.internal_error(message=str(e))


class JenkinsJobCheckParamsView(APIView):
    """检查 Job 的动态参数 - 用于参数化构建"""
    
    def get(self, request, job_id):
        """
        获取指定 Job 的动态参数列表
        
        Args:
            job_id: Job 的数据库 ID (从 URL 路径获取)
            
        Returns:
            成功: {"code": 200, "data": {"params": ["score", "env"]}}
            失败: {"code": xxx, "message": "错误信息"}
        """
        try:
            from ..services.job_param_service import JobParamService
            from ..models import JenkinsJob
            
            # 获取动态参数列表
            try:
                # 先获取 Job 信息
                job = JenkinsJob.objects.get(id=job_id)
                
                params = JobParamService.get_job_params(job_id)
                
                logger.info(f"获取 Job {job_id} 的动态参数: {params}")
                return R.success(
                    message=f"检测到 {len(params)} 个动态参数",
                    data={'params': params}
                )
                
            except JenkinsJob.DoesNotExist:
                logger.error(f"Job ID {job_id} 不存在")
                return R.error(
                    message=f"Job ID {job_id} 不存在",
                    code=ResponseCode.JENKINS_JOB_NOT_FOUND
                )
                
        except Exception as e:
            error_msg = f"检查参数失败: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return R.internal_error(message=error_msg)
