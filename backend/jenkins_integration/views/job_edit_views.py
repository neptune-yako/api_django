"""
Jenkins Job 编辑视图
职责：同步编辑 Jenkins 和本地数据库
"""
from rest_framework.views import APIView
from ..utils import R, ResponseCode, ResponseMessage
from ..models import JenkinsJob
from ..serializers import JenkinsJobSerializer
import logging
import traceback

logger = logging.getLogger(__name__)


class JenkinsJobEditView(APIView):
    """
    Jenkins Job 编辑视图
    支持编辑字段：
    - description（同步到 Jenkins）
    - config_xml（同步到 Jenkins，含软检查）
    - is_active（同步到 Jenkins）
    - project/environment/plan（仅本地）
    """
    
    def put(self, request):
        """编辑 Job"""
        try:
            # 1. 获取参数
            job_id = request.data.get('id')
            if not job_id:
                return R.bad_request(message=ResponseMessage.PARAM_MISSING + ': id')
            
            # 2. 获取 Job 实例
            try:
                job = JenkinsJob.objects.get(id=job_id)
            except JenkinsJob.DoesNotExist:
                return R.error(message="Job 不存在", code=ResponseCode.JENKINS_JOB_NOT_FOUND)
            
            logger.info(f"开始编辑 Job: {job.name} (ID: {job_id})")
            
            # 3. 分类字段
            data = request.data
            force = data.get('force', False)  # 强制保存标记
            
            # 需要同步到 Jenkins 的字段
            need_jenkins_sync = False
            jenkins_operations = []  # 记录需要执行的 Jenkins 操作
            
            # 4. 处理 config_xml（包含 description）
            if 'config_xml' in data or 'description' in data:
                need_jenkins_sync = True
                
                # 优先使用 config_xml，否则先获取现有配置
                if 'config_xml' in data:
                    config_xml = data['config_xml']
                else:
                    # 只更新 description，需要先获取现有配置
                    from ..jenkins_client import get_job_config
                    success, message, existing_config = get_job_config(job.name)
                    if not success:
                        return R.jenkins_error(message=f"获取现有配置失败: {message}")
                    
                    # 在现有配置中更新 description
                    config_xml = self._update_description_in_xml(
                        existing_config.get('config_xml', ''),
                        data.get('description', job.description)
                    )
                
                # XML 软检查
                from ..jenkins_client import validate_xml
                is_valid, errors = validate_xml(config_xml)
                
                if not is_valid and not force:
                    logger.warning(f"XML 验证失败: {errors}")
                    return R.error(
                        message="XML 验证失败，请修复后重试或强制保存",
                        code=ResponseCode.JENKINS_XML_INVALID,
                        data={
                            'errors': errors,
                            'need_force': True
                        }
                    )
                
                jenkins_operations.append(('update_config', config_xml))
            
            # 5. 处理 is_active
            if 'is_active' in data:
                new_active = data['is_active']
                if new_active != job.is_active:
                    need_jenkins_sync = True
                    action = 'enable' if new_active else 'disable'
                    jenkins_operations.append((action, None))
            
            # 6. 执行 Jenkins 同步操作
            if need_jenkins_sync:
                from ..jenkins_client import update_job, enable_job, disable_job
                
                for operation, param in jenkins_operations:
                    if operation == 'update_config':
                        logger.info(f"更新 Jenkins Job 配置: {job.name}")
                        success, message, _ = update_job(job.name, param)
                        if not success:
                            return R.jenkins_error(message=f"更新配置失败: {message}")
                    
                    elif operation == 'enable':
                        logger.info(f"启用 Jenkins Job: {job.name}")
                        success, message, _ = enable_job(job.name)
                        if not success:
                            return R.jenkins_error(message=f"启用失败: {message}")
                    
                    elif operation == 'disable':
                        logger.info(f"禁用 Jenkins Job: {job.name}")
                        success, message, _ = disable_job(job.name)
                        if not success:
                            return R.jenkins_error(message=f"禁用失败: {message}")
            
            # 7. 更新本地数据库
            update_fields = []
            
            # 同步字段（已同步到 Jenkins，现在更新 DB）
            if 'description' in data:
                job.description = data['description']
                update_fields.append('description')
            
            if 'config_xml' in data:
                job.config_xml = data['config_xml']
                update_fields.append('config_xml')
            
            if 'is_active' in data:
                job.is_active = data['is_active']
                update_fields.append('is_active')
            
            # 仅本地字段（不需要同步到 Jenkins）
            if 'project' in data:
                job.project_id = data['project']
                update_fields.append('project')
            
            if 'environment' in data:
                job.environment_id = data['environment']
                update_fields.append('environment')
            
            if 'plan' in data:
                job.plan_id = data['plan']
                update_fields.append('plan')
            
            # 保存
            if update_fields:
                update_fields.append('update_time')
                job.save(update_fields=update_fields)
                logger.info(f"Job 编辑成功: {job.name}, 更新字段: {update_fields}")
            
            # 8. 返回结果
            serializer = JenkinsJobSerializer(job)
            return R.success(
                message="Job 编辑成功",
                data=serializer.data
            )
            
        except Exception as e:
            error_msg = f"编辑 Job 异常: {str(e)}"
            error_trace = traceback.format_exc()
            logger.error(f"{error_msg}\n{error_trace}")
            return R.internal_error(
                message=error_msg,
                data={'traceback': error_trace}
            )
    
    def _update_description_in_xml(self, config_xml, new_description):
        """在 XML 中更新 description"""
        import xml.etree.ElementTree as ET
        
        try:
            root = ET.fromstring(config_xml)
            desc_elem = root.find('description')
            
            if desc_elem is not None:
                desc_elem.text = new_description
            else:
                # 如果没有 description 元素，创建一个
                desc_elem = ET.SubElement(root, 'description')
                desc_elem.text = new_description
            
            return ET.tostring(root, encoding='unicode')
        except Exception as e:
            logger.error(f"更新 XML description 失败: {e}")
            return config_xml
