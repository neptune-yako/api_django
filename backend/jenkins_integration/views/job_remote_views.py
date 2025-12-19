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

class JenkinsJobManageView(APIView):
    """Jenkins Job 远程管理 - CRUD 操作"""
    
    def get(self, request):
        """获取 Job 信息或配置"""
        try:
            job_name = request.query_params.get('job_name')
            get_config = request.query_params.get('get_config', 'false').lower() == 'true'
            
            if not job_name:
                return R.bad_request(message=ResponseMessage.PARAM_MISSING + ': job_name')
            
            if get_config:
                from ..jenkins_client import get_job_config
                success, message, data = get_job_config(job_name)
            else:
                from ..jenkins_client import get_job_info
                success, message, data = get_job_info(job_name)
            
            if success:
                return R.success(message=message, data=data)
            else:
                if 'not exist' in message.lower() or '不存在' in message:
                    return R.error(
                        message=message,
                        code=ResponseCode.JENKINS_JOB_NOT_FOUND
                    )
                return R.jenkins_error(message=message)
                
        except Exception as e:
            return R.internal_error(message=str(e))
    
    def post(self, request):
        """创建 Job"""
        try:
            job_name = request.data.get('job_name')
            config_xml = request.data.get('config_xml')
            force = request.data.get('force', False)
            
            if not job_name or not config_xml:
                return R.bad_request(
                    message=ResponseMessage.PARAM_MISSING + ': job_name 或 config_xml'
                )
            
            from ..jenkins_client import validate_xml, create_job
            
            is_valid, errors = validate_xml(config_xml)
            if not is_valid and not force:
                return R.error(
                    message=ResponseMessage.XML_INVALID + '，请修复后重试或使用 force=true 强制创建',
                    code=ResponseCode.JENKINS_XML_INVALID,
                    data={'errors': errors}
                )
            
            success, message, data = create_job(job_name, config_xml)
            
            if success:
                return R.success(message=ResponseMessage.JOB_CREATED, data=data)
            else:
                if '已存在' in message or 'exists' in message.lower():
                    return R.error(
                        message=message,
                        code=ResponseCode.JENKINS_JOB_ALREADY_EXISTS
                    )
                return R.jenkins_error(message=message)
                
        except Exception as e:
            return R.internal_error(message=str(e))
    
    def put(self, request):
        """更新 Job 配置"""
        try:
            job_name = request.data.get('job_name')
            config_xml = request.data.get('config_xml')
            force = request.data.get('force', False)
            
            if not job_name or not config_xml:
                return R.bad_request(
                    message=ResponseMessage.PARAM_MISSING + ': job_name 或 config_xml'
                )
            
            from ..jenkins_client import validate_xml, update_job
            
            is_valid, errors = validate_xml(config_xml)
            if not is_valid and not force:
                return R.error(
                    message=ResponseMessage.XML_INVALID,
                    code=ResponseCode.JENKINS_XML_INVALID,
                    data={'errors': errors}
                )
            
            success, message, data = update_job(job_name, config_xml)
            
            if success:
                return R.success(message=ResponseMessage.JOB_UPDATED, data=data)
            else:
                if '不存在' in message or 'not exist' in message.lower():
                    return R.error(
                        message=message,
                        code=ResponseCode.JENKINS_JOB_NOT_FOUND
                    )
                return R.jenkins_error(message=message)
                
        except Exception as e:
            return R.internal_error(message=str(e))
    
    def delete(self, request):
        """删除 Job"""
        try:
            job_name = request.query_params.get('job_name')
            if not job_name:
                return R.bad_request(message=ResponseMessage.PARAM_MISSING + ': job_name')
            
            from ..jenkins_client import delete_job
            success, message, data = delete_job(job_name)
            
            if success:
                return R.success(message=ResponseMessage.JOB_DELETED, data=data)
            else:
                if '不存在' in message or 'not exist' in message.lower():
                    return R.error(
                        message=message,
                        code=ResponseCode.JENKINS_JOB_NOT_FOUND
                    )
                return R.jenkins_error(message=message)
        except Exception as e:
            return R.internal_error(message=str(e))


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
    """触发 Job 构建"""
    def post(self, request):
        try:
            job_name = request.data.get('job_name')
            parameters = request.data.get('parameters')
            
            if not job_name:
                return R.bad_request(message=ResponseMessage.PARAM_MISSING + ': job_name')
            
            from ..jenkins_client import build_job
            success, message, data = build_job(job_name, parameters)
            
            if success:
                return R.success(message=ResponseMessage.BUILD_TRIGGERED, data=data)
            else:
                return R.error(message=message, code=ResponseCode.JENKINS_BUILD_FAILED)
        except Exception as e:
            return R.internal_error(message=str(e))
