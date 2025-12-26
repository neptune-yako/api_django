from rest_framework.views import APIView
from ..utils import R, ResponseCode, ResponseMessage
import logging
import traceback

logger = logging.getLogger(__name__)
# 远程 Job 管理
class JenkinsJobsView(APIView):
    """获取所有 Jobs (Remote)"""
    
    def get(self, request):
        try:
            from ..jenkins_client import get_all_jobs
            
            logger.info("开始获取 Jenkins Jobs (Remote)...")
            success, message, data = get_all_jobs()
            
            if success:
                logger.info(f"获取 Jobs 成功: {message}")
                return R.success(message=message, data=data)
            else:
                logger.error(f"获取 Jobs 失败: {message}")
                return R.jenkins_error(message=message)
                
        except Exception as e:
            error_msg = f"视图异常: {str(e)}"
            error_trace = traceback.format_exc()
            logger.error(f"{error_msg}\n{error_trace}")
            
            return R.internal_error(
                message=error_msg,
                data={'traceback': error_trace}
            )



class JenkinsJobValidateView(APIView):
    """XML 配置校验"""
    def post(self, request):
        try:
            config_xml = request.data.get('config_xml')
            if not config_xml:
                return R.bad_request(message=ResponseMessage.PARAM_MISSING + ': config_xml')
            
            from ..jenkins_client import validate_xml
            is_valid, errors = validate_xml(config_xml)
            
            if is_valid:
                return R.success(message=ResponseMessage.XML_VALID, data={'valid': True, 'errors': []})
            else:
                return R.success(message=ResponseMessage.XML_INVALID, data={'valid': False, 'errors': errors})
        except Exception as e:
            return R.internal_error(message=str(e))


class JenkinsJobCopyView(APIView):
    """复制 Job"""
    def post(self, request):
        try:
            source_job = request.data.get('source_job')
            new_job = request.data.get('new_job')
            if not source_job or not new_job:
                return R.bad_request(message=ResponseMessage.PARAM_MISSING + ': source_job 或 new_job')
            
            from ..jenkins_client import copy_job
            success, message, data = copy_job(source_job, new_job)
            
            if success:
                return R.success(message=message, data=data)
            else:
                if '不存在' in message or 'not exist' in message.lower():
                    return R.error(message=message, code=ResponseCode.JENKINS_JOB_NOT_FOUND)
                elif '已存在' in message or 'exists' in message.lower():
                    return R.error(message=message, code=ResponseCode.JENKINS_JOB_ALREADY_EXISTS)
                return R.jenkins_error(message=message)
        except Exception as e:
            return R.internal_error(message=str(e))


class JenkinsJobToggleView(APIView):
    """启用/禁用 Job"""
    def post(self, request):
        try:
            job_name = request.data.get('job_name')
            action = request.data.get('action')
            if not job_name or action not in ['enable', 'disable']:
                return R.bad_request(message='参数错误，action 必须为 enable 或 disable')
            
            if action == 'enable':
                from ..jenkins_client import enable_job
                success, message, data = enable_job(job_name)
            else:
                from ..jenkins_client import disable_job
                success, message, data = disable_job(job_name)
            
            if success:
                return R.success(message=message, data=data)
            else:
                if '不存在' in message or 'not exist' in message.lower():
                    return R.error(message=message, code=ResponseCode.JENKINS_JOB_NOT_FOUND)
                return R.jenkins_error(message=message)
        except Exception as e:
            return R.internal_error(message=str(e))


class JenkinsJobBuildView(APIView):
    """触发 Job 构建 - 支持动态参数"""
    
    def post(self, request):
        """
        触发 Job 构建
        
        请求参数:
            - job_name: Job 名称（必填）
            - job_id: Job ID（可选，优先级低于 job_name）
            - build_params: 动态参数字典（可选）{"score": "95", "env": "prod"}
            - parameters: Jenkins 原生参数（可选，向后兼容）
            
        Returns:
            成功: {"code": 200, "message": "构建已触发", "data": {...}}
            失败: {"code": xxx, "message": "错误信息"}
        """
        try:
            job_name = request.data.get('job_name')
            job_id = request.data.get('job_id')
            build_params = request.data.get('build_params')  # 新增：动态参数
            parameters = request.data.get('parameters')  # 原有：Jenkins 参数
            
            # 参数校验
            if not job_name and not job_id:
                return R.bad_request(message=ResponseMessage.PARAM_MISSING + ': job_name 或 job_id')
            
            # 如果提供了 build_params，使用参数化构建
            if build_params and isinstance(build_params, dict):
                logger.info(f"检测到动态参数，使用参数化构建: {build_params}")
                
                # 使用 Service 层处理参数化构建
                from ..services.job_param_service import JobParamService
                from ..models import JenkinsJob
                
                # 如果只有 job_name，需要先查询 job_id
                if not job_id:
                    try:
                        job = JenkinsJob.objects.get(name=job_name)
                        job_id = job.id
                    except JenkinsJob.DoesNotExist:
                        return R.error(
                            message=f"Job '{job_name}' 不存在",
                            code=ResponseCode.JENKINS_JOB_NOT_FOUND
                        )
                
                # 调用 Service 层的参数化构建方法
                success, message, data = JobParamService.build_with_params(
                    job_id=job_id,
                    build_params=build_params,
                    validate_missing=True  # 验证参数完整性
                )
                
                if success:
                    return R.success(message=message, data=data)
                else:
                    return R.error(message=message, code=ResponseCode.JENKINS_BUILD_FAILED)
            
            # 原有逻辑：普通构建（无动态参数）
            else:
                logger.info(f"触发普通构建: {job_name}")
                
                from ..jenkins_client import build_job
                success, message, data = build_job(job_name, parameters)
                
                if success:
                    return R.success(message=ResponseMessage.BUILD_TRIGGERED, data=data)
                else:
                    return R.error(message=message, code=ResponseCode.JENKINS_BUILD_FAILED)
                    
        except ValueError as e:
            # 参数验证失败
            logger.error(f"参数验证失败: {str(e)}")
            return R.bad_request(message=str(e))
            
        except Exception as e:
            error_msg = f"触发构建失败: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return R.internal_error(message=error_msg)

