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



class JenkinsJobManageView(APIView):
    """
    Jenkins Job 管理视图 (统一 CRUD)
    支持：
    - POST: 创建 Job (远程 + 本地)
    - PUT: 编辑 Job (远程 + 本地)
    """

    def post(self, request):
        """创建 Job"""
        try:
            # 1. 获取参数
            job_name = request.data.get('name')
            if not job_name:
                return R.bad_request(message="参数错误: Job 名称不能为空")
            
            # 2. 获取并验证服务器
            from ..models import JenkinsServer
            server_id = request.data.get('server')
            if not server_id:
                return R.bad_request(message="参数错误: 请选择 Jenkins 服务器")
            
            try:
                server = JenkinsServer.objects.get(id=server_id, is_active=True)
            except JenkinsServer.DoesNotExist:
                return R.error(message="Jenkins 服务器不存在或已禁用")
                
            if JenkinsJob.objects.filter(name=job_name, server=server).exists():
                return R.error(message=f"Job '{job_name}' 已存在于服务器 {server.name}", code=ResponseCode.JENKINS_JOB_ALREADY_EXISTS)

            # 3. 处理 config_xml 和 job_type
            config_xml = request.data.get('config_xml')
            job_type = request.data.get('job_type', 'FreeStyle')  # 默认 FreeStyle
            force = request.data.get('force', False)
            
            if not config_xml:
                # 从模板加载配置
                config_xml = self._load_template_xml(job_type, request.data.get('description', ''))
            else:
                # XML 校验
                from ..jenkins_client import validate_xml
                is_valid, errors = validate_xml(config_xml)
                if not is_valid and not force:
                    return R.error(
                        message="XML 验证失败，请修复后重试或强制保存",
                        code=ResponseCode.JENKINS_XML_INVALID,
                        data={'errors': errors, 'need_force': True}
                    )

            # 4. 远程创建
            from ..jenkins_client import create_job
            logger.info(f"开始远程创建 Job: {job_name}")
            success, message, _ = create_job(job_name, config_xml)
            
            if not success:
                logger.error(f"远程创建失败: {message}")
                if '已存在' in message or 'exists' in message.lower():
                     return R.error(message=message, code=ResponseCode.JENKINS_JOB_ALREADY_EXISTS)
                return R.jenkins_error(message=message)

            # 5. 本地入库
            try:
                from django.utils import timezone
                # 注入创建人
                created_by = request.user.username if request.user.is_authenticated else 'system'
                
                # 安全获取关联 ID (处理空字符串等情况)
                def get_id(key):
                    val = request.data.get(key)
                    return val if val else None
                
                # 获取环境ID列表 (支持 environments 或 environment)
                environment_ids = request.data.get('environments', []) or request.data.get('environment')
                if isinstance(environment_ids, int):
                    # 兼容旧格式:单个ID转为列表
                    environment_ids = [environment_ids]
                elif environment_ids is None or environment_ids == '':
                    environment_ids = []

                job = JenkinsJob.objects.create(
                    name=job_name,
                    display_name=job_name,
                    server=server,
                    description=request.data.get('description', ''),
                    config_xml=config_xml,
                    is_active=request.data.get('is_active', True),
                    project_id=get_id('project'),
                    plan_id=get_id('plan'),
                    job_type=job_type,  
                    is_buildable=True,
                    created_by=created_by,
                    last_sync_time=timezone.now() # 设置同步时间，确保显示在列表顶部
                )
                
                # 设置多对多关系
                if environment_ids:
                    job.environments.set(environment_ids)
                
                logger.info(f"本地 Job 创建成功: {job.name}")
                
                return R.success(message="创建成功", data=JenkinsJobSerializer(job).data)
                
            except Exception as e:
                # 本地创建失败
                error_msg = f"远程创建成功，但本地数据库写入失败: {str(e)}"
                logger.error(error_msg)
                # 返回错误状态码，让前端知道出问题了
                return R.error(message=error_msg)

        except Exception as e:
            error_msg = f"创建 Job 异常: {str(e)}"
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            return R.internal_error(message=error_msg)

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
            
            if 'plan' in data:
                job.plan_id = data['plan']
                update_fields.append('plan')
            
            # 更新环境关联 (多对多) - 支持 environments 或 environment
            if 'environments' in data or 'environment' in data:
                environment_ids = data.get('environments') or data.get('environment', [])
                if isinstance(environment_ids, int):
                    environment_ids = [environment_ids]
                elif environment_ids is None or environment_ids == '':
                    environment_ids = []
                job.environments.set(environment_ids)
            
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
    
    def _load_template_xml(self, job_type='FreeStyle', description=''):
        """从模板文件加载配置 XML"""
        import os
        from django.conf import settings
        
        # 模板文件映射
        template_map = {
            'FreeStyle': 'freestyle.xml',
            'Pipeline': 'pipeline.xml',
            'Maven': 'maven.xml'
        }
        
        template_file = template_map.get(job_type, 'freestyle.xml')
        template_path = os.path.join(
            settings.BASE_DIR,
            'jenkins_integration',
            'job_templates',
            template_file
        )
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                config_xml = f.read()
            
            # 替换描述占位符（如果模板中有的话）
            if description and '{{description}}' in config_xml:
                config_xml = config_xml.replace('{{description}}', description)
            
            return config_xml
        except FileNotFoundError:
            logger.error(f"模板文件不存在: {template_path}")
            # 返回最基础的 FreeStyle 模板
            return """<?xml version='1.1' encoding='UTF-8'?>
<project>
  <description>{}</description>
  <keepDependencies>false</keepDependencies>
  <properties/>
  <scm class="hudson.scm.NullSCM"/>
  <canRoam>true</canRoam>
  <disabled>false</disabled>
  <blockBuildWhenDownstreamBuilding>false</blockBuildWhenDownstreamBuilding>
  <blockBuildWhenUpstreamBuilding>false</blockBuildWhenUpstreamBuilding>
  <triggers/>
  <concurrentBuild>false</concurrentBuild>
  <builders/>
  <publishers/>
  <buildWrappers/>
</project>""".format(description)
        except Exception as e:
            logger.error(f"加载模板文件失败: {e}")
            raise

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
