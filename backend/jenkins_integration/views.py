"""
Jenkins API 视图 - 使用统一响应格式

重构使用:
- R 统一响应类 (类似 Spring Boot 的 R<T>)
- ResponseCode 错误码枚举
- ResponseMessage 响应消息常量
"""
from rest_framework.views import APIView
import traceback
import logging

# 导入统一响应工具
from .utils import R, ResponseCode, ResponseMessage

logger = logging.getLogger(__name__)


class JenkinsTestView(APIView):
    """测试 Jenkins 连接"""
    
    def get(self, request):
        try:
            from .jenkins_client import test_connection
            
            logger.info("开始测试 Jenkins 连接...")
            success, message, data = test_connection()
            
            if success:
                logger.info(f"Jenkins 连接成功: {message}")
                return R.success(
                    message=ResponseMessage.JENKINS_CONNECTED,
                    data=data
                )
            else:
                logger.error(f"Jenkins 连接失败: {message}")
                return R.jenkins_error(
                    message=message,
                    code=ResponseCode.JENKINS_CONNECTION_FAILED
                )
                
        except Exception as e:
            error_msg = f"视图异常: {str(e)}"
            error_trace = traceback.format_exc()
            logger.error(f"{error_msg}\n{error_trace}")
            
            return R.internal_error(
                message=error_msg,
                data={'traceback': error_trace}
            )


class JenkinsJobsView(APIView):
    """获取所有 Jobs"""
    
    def get(self, request):
        try:
            from .jenkins_client import get_all_jobs
            
            logger.info("开始获取 Jenkins Jobs...")
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
    """Jenkins Job 管理 - CRUD 操作"""
    
    def get(self, request):
        """获取 Job 信息或配置"""
        try:
            job_name = request.query_params.get('job_name')
            get_config = request.query_params.get('get_config', 'false').lower() == 'true'
            
            if not job_name:
                return R.bad_request(message=ResponseMessage.PARAM_MISSING + ': job_name')
            
            if get_config:
                from .jenkins_client import get_job_config
                success, message, data = get_job_config(job_name)
            else:
                from .jenkins_client import get_job_info
                success, message, data = get_job_info(job_name)
            
            if success:
                return R.success(message=message, data=data)
            else:
                # 判断是否为 Job 不存在
                if 'not exist' in message.lower() or '不存在' in message:
                    return R.error(
                        message=message,
                        code=ResponseCode.JENKINS_JOB_NOT_FOUND
                    )
                return R.jenkins_error(message=message)
                
        except Exception as e:
            error_msg = f"获取 Job 失败: {str(e)}"
            logger.error(error_msg)
            return R.internal_error(message=error_msg)
    
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
            
            from .jenkins_client import validate_xml, create_job
            
            # 校验 XML
            is_valid, errors = validate_xml(config_xml)
            
            if not is_valid and not force:
                return R.error(
                    message=ResponseMessage.XML_INVALID + '，请修复后重试或使用 force=true 强制创建',
                    code=ResponseCode.JENKINS_XML_INVALID,
                    data={'errors': errors}
                )
            
            # 创建 Job
            success, message, data = create_job(job_name, config_xml)
            
            if success:
                return R.success(
                    message=ResponseMessage.JOB_CREATED,
                    data=data
                )
            else:
                # 判断是否为 Job 已存在
                if '已存在' in message or 'exists' in message.lower():
                    return R.error(
                        message=message,
                        code=ResponseCode.JENKINS_JOB_ALREADY_EXISTS
                    )
                return R.jenkins_error(message=message)
                
        except Exception as e:
            error_msg = f"创建 Job 失败: {str(e)}"
            logger.error(error_msg)
            return R.internal_error(message=error_msg)
    
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
            
            from .jenkins_client import validate_xml, update_job
            
            # 校验 XML
            is_valid, errors = validate_xml(config_xml)
            
            if not is_valid and not force:
                return R.error(
                    message=ResponseMessage.XML_INVALID,
                    code=ResponseCode.JENKINS_XML_INVALID,
                    data={'errors': errors}
                )
            
            # 更新 Job
            success, message, data = update_job(job_name, config_xml)
            
            if success:
                return R.success(
                    message=ResponseMessage.JOB_UPDATED,
                    data=data
                )
            else:
                if '不存在' in message or 'not exist' in message.lower():
                    return R.error(
                        message=message,
                        code=ResponseCode.JENKINS_JOB_NOT_FOUND
                    )
                return R.jenkins_error(message=message)
                
        except Exception as e:
            error_msg = f"更新 Job 失败: {str(e)}"
            logger.error(error_msg)
            return R.internal_error(message=error_msg)
    
    def delete(self, request):
        """删除 Job"""
        try:
            job_name = request.query_params.get('job_name')
            
            if not job_name:
                return R.bad_request(message=ResponseMessage.PARAM_MISSING + ': job_name')
            
            from .jenkins_client import delete_job
            success, message, data = delete_job(job_name)
            
            if success:
                return R.success(
                    message=ResponseMessage.JOB_DELETED,
                    data=data
                )
            else:
                if '不存在' in message or 'not exist' in message.lower():
                    return R.error(
                        message=message,
                        code=ResponseCode.JENKINS_JOB_NOT_FOUND
                    )
                return R.jenkins_error(message=message)
                
        except Exception as e:
            error_msg = f"删除 Job 失败: {str(e)}"
            logger.error(error_msg)
            return R.internal_error(message=error_msg)


class JenkinsJobValidateView(APIView):
    """XML 配置校验"""
    
    def post(self, request):
        """校验 XML 配置"""
        try:
            config_xml = request.data.get('config_xml')
            
            if not config_xml:
                return R.bad_request(message=ResponseMessage.PARAM_MISSING + ': config_xml')
            
            from .jenkins_client import validate_xml
            is_valid, errors = validate_xml(config_xml)
            
            if is_valid:
                return R.success(
                    message=ResponseMessage.XML_VALID,
                    data={'valid': True, 'errors': []}
                )
            else:
                return R.success(
                    message=ResponseMessage.XML_INVALID,
                    data={'valid': False, 'errors': errors}
                )
                
        except Exception as e:
            error_msg = f"校验失败: {str(e)}"
            logger.error(error_msg)
            return R.internal_error(message=error_msg)


class JenkinsJobCopyView(APIView):
    """复制 Job"""
    
    def post(self, request):
        """复制 Job"""
        try:
            source_job = request.data.get('source_job')
            new_job = request.data.get('new_job')
            
            if not source_job or not new_job:
                return R.bad_request(
                    message=ResponseMessage.PARAM_MISSING + ': source_job 或 new_job'
                )
            
            from .jenkins_client import copy_job
            success, message, data = copy_job(source_job, new_job)
            
            if success:
                return R.success(message=message, data=data)
            else:
                if '不存在' in message or 'not exist' in message.lower():
                    return R.error(
                        message=message,
                        code=ResponseCode.JENKINS_JOB_NOT_FOUND
                    )
                elif '已存在' in message or 'exists' in message.lower():
                    return R.error(
                        message=message,
                        code=ResponseCode.JENKINS_JOB_ALREADY_EXISTS
                    )
                return R.jenkins_error(message=message)
                
        except Exception as e:
            error_msg = f"复制 Job 失败: {str(e)}"
            logger.error(error_msg)
            return R.internal_error(message=error_msg)


class JenkinsJobToggleView(APIView):
    """启用/禁用 Job"""
    
    def post(self, request):
        """启用或禁用 Job"""
        try:
            job_name = request.data.get('job_name')
            action = request.data.get('action')
            
            if not job_name or action not in ['enable', 'disable']:
                return R.bad_request(
                    message='参数错误，action 必须为 enable 或 disable'
                )
            
            if action == 'enable':
                from .jenkins_client import enable_job
                success, message, data = enable_job(job_name)
            else:
                from .jenkins_client import disable_job
                success, message, data = disable_job(job_name)
            
            if success:
                return R.success(message=message, data=data)
            else:
                if '不存在' in message or 'not exist' in message.lower():
                    return R.error(
                        message=message,
                        code=ResponseCode.JENKINS_JOB_NOT_FOUND
                    )
                return R.jenkins_error(message=message)
                
        except Exception as e:
            error_msg = f"操作失败: {str(e)}"
            logger.error(error_msg)
            return R.internal_error(message=error_msg)


class JenkinsJobBuildView(APIView):
    """触发 Job 构建"""
    
    def post(self, request):
        """触发 Job 构建"""
        try:
            job_name = request.data.get('job_name')
            parameters = request.data.get('parameters')
            
            if not job_name:
                return R.bad_request(message=ResponseMessage.PARAM_MISSING + ': job_name')
            
            from .jenkins_client import build_job
            success, message, data = build_job(job_name, parameters)
            
            if success:
                return R.success(
                    message=ResponseMessage.BUILD_TRIGGERED,
                    data=data
                )
            else:
                return R.error(
                    message=message,
                    code=ResponseCode.JENKINS_BUILD_FAILED
                )
                
        except Exception as e:
            error_msg = f"触发构建失败: {str(e)}"
            logger.error(error_msg)
            return R.internal_error(message=error_msg)


# ==================== Template 相关视图 ====================

class JenkinsTemplateListView(APIView):
    """获取所有可用的 Job 模板列表"""
    
    def get(self, request):
        """
        获取所有可用模板
        
        Returns:
            {
                "code": 200,
                "message": "成功",
                "data": [
                    {
                        "type": "freestyle",
                        "name": "自由风格项目",
                        "description": "...",
                        "icon": "📋"
                    },
                    ...
                ]
            }
        """
        try:
            from .template_manager import get_template_manager
            
            manager = get_template_manager()
            templates = manager.get_all_templates()
            
            return R.success(
                message=f"成功获取 {len(templates)} 个模板",
                data=templates
            )
            
        except Exception as e:
            error_msg = f"获取模板列表失败: {str(e)}"
            logger.error(error_msg)
            return R.internal_error(message=error_msg)


class JenkinsTemplateDetailView(APIView):
    """获取指定类型的模板内容"""
    
    def get(self, request, template_type):
        """
        获取模板 XML 内容
        
        Args:
            template_type: 模板类型 (freestyle, pipeline, maven)
            
        Returns:
            {
                "code": 200,
                "message": "成功加载模板 [自由风格项目]",
                "data": {
                    "type": "freestyle",
                    "name": "自由风格项目",
                    "xml_content": "<?xml...>"
                }
            }
        """
        try:
            from .template_manager import get_template_manager
            
            manager = get_template_manager()
            
            # 1. 获取模板信息
            info_success, info_msg, template_info = manager.get_template_info(template_type)
            
            if not info_success:
                return R.bad_request(message=info_msg)
            
            # 2. 加载模板内容
            load_success, load_msg, xml_content = manager.load_template(template_type)
            
            if not load_success:
                return R.jenkins_error(message=load_msg)
            
            # 3. 返回完整数据
            return R.success(
                message=load_msg,
                data={
                    'type': template_type,
                    'name': template_info['name'],
                    'description': template_info['description'],
                    'xml_content': xml_content
                }
            )
            
        except Exception as e:
            error_msg = f"获取模板失败: {str(e)}"
            logger.error(error_msg)
            return R.internal_error(message=error_msg)


# ==================== Build 状态查询视图 ====================

class JenkinsBuildLatestView(APIView):
    """查询最新构建状态（用于前端轮询）"""
    
    def get(self, request):
        """
        获取指定 Job 的最新构建状态
        
        用途：前端轮询使用
        
        Query Parameters:
            job_name: Job 名称（必需）
            
        Returns:
            {
                "code": 200,
                "message": "最新构建 #45 - 构建成功",
                "data": {
                    "build_number": 45,
                    "result": "SUCCESS",      // SUCCESS, FAILURE, ABORTED, UNSTABLE, null(构建中)
                    "building": false,         // true(构建中), false(已完成)
                    "duration": 120000,        // 毫秒
                    "duration_text": "120.00秒",
                    "status_text": "构建成功",
                    "url": "http://jenkins/job/xxx/45/",
                    "timestamp": 1702615200000
                }
            }
        """
        try:
            job_name = request.query_params.get('job_name')
            
            if not job_name:
                return R.bad_request(message=ResponseMessage.PARAM_MISSING + ': job_name')
            
            # 1. 获取 Job 信息
            from .jenkins_client import get_job_info
            success, message, data = get_job_info(job_name)
            
            if not success:
                if '不存在' in message or 'not exist' in message.lower():
                    return R.error(
                        message=message,
                        code=ResponseCode.JENKINS_JOB_NOT_FOUND
                    )
                return R.jenkins_error(message=message)
            
            # 2. 检查是否有构建记录
            last_build = data.get('lastBuild')
            
            if not last_build:
                return R.success(
                    message='该 Job 还没有构建记录',
                    data=None
                )
            
            last_build_number = last_build.get('number')
            
            # 3. 获取最新构建的详细信息
            from .jenkins_client import get_build_info
            build_success, build_msg, build_data = get_build_info(job_name, last_build_number)
            
            if not build_success:
                return R.jenkins_error(message=build_msg)
            
            # 4. 解析构建状态
            result = build_data.get('result')
            building = build_data.get('building')
            duration = build_data.get('duration')
            
            # 确定状态文本
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
            
            # 5. 返回格式化的数据
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
            error_msg = f"查询最新构建状态失败: {str(e)}"
            logger.error(error_msg)
            return R.internal_error(message=error_msg)


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
                "message": "获取 Allure 报告 URL",
                "data": {
                    "allure_url": "...",
                    "job_name": "...",
                    "build_number": ...
                }
            }
            
            注意：实际实现已移至 allure_views.py
        """
        # 导入实际实现
        from .allure_views import JenkinsBuildAllureView as ActualView
        return ActualView().get(request)


class SyncJenkinsJobsView(APIView):
    """
    同步 Jenkins Jobs 视图
    从 Jenkins 服务器拉取所有 Job 并同步到数据库
    """
    
    def post(self, request):
        """
        触发同步 (异步)
        """
        try:
            # 调用 Celery 异步任务
            from .tasks import sync_jenkins_jobs_task
            task = sync_jenkins_jobs_task.delay()
            
            return R.success(
                message="Jenkins Jobs 同步任务已在后台启动",
                data={'task_id': task.id}
            )
                
        except Exception as e:
            logger.error(f"同步 Jobs 视图异常: {str(e)}")
            return R.internal_error(str(e))
