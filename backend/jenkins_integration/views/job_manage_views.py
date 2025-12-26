"""
Jenkins Job 编辑视图
职责：同步编辑 Jenkins 和本地数据库
"""
from rest_framework.views import APIView
from ..utils import R, ResponseCode, ResponseMessage
from ..models import JenkinsJob, JenkinsNode
from ..serializers import JenkinsJobSerializer
from ..pipeline_generator import create_pipeline_generator
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
    
    def _wrap_pipeline_script_in_xml(self, script_content, description=''):
        """将纯 Pipeline 脚本封装为 Jenkins XML 配置（使用 CDATA）
        
        Args:
            script_content: 原始 Groovy 脚本内容
            description: Job 描述（会自动转义 XML 特殊字符）
            
        Returns:
            str: 完整的 Jenkins XML 配置
        """
        import xml.sax.saxutils as saxutils
        
        # 转义 description 中的 XML 特殊字符
        safe_description = saxutils.escape(description)
        
        # 处理脚本中的嵌套 CDATA（极少见但需要处理）
        if ']]>' in script_content:
            script_content = script_content.replace(']]>', ']]]]><![CDATA[>')
            logger.warning("检测到脚本中包含 ']]>'，已分割为多段 CDATA")
        
        # 使用字符串拼接避免格式化问题（Groovy 脚本中有大量 {}）
        config_xml = (
            "<?xml version='1.1' encoding='UTF-8'?>\n"
            "<flow-definition plugin=\"workflow-job\">\n"
            "  <description>" + safe_description + "</description>\n"
            "  <keepDependencies>false</keepDependencies>\n"
            "  <properties/>\n"
            "  <definition class=\"org.jenkinsci.plugins.workflow.cps.CpsFlowDefinition\" plugin=\"workflow-cps\">\n"
            "    <script><![CDATA[" + script_content + "]]></script>\n"
            "    <sandbox>true</sandbox>\n"
            "  </definition>\n"
            "  <triggers/>\n"
            "  <disabled>false</disabled>\n"
            "</flow-definition>"
        )
        
        # 🔍 调试：写入文件
        try:
            with open('debug_pipeline.log', 'a', encoding='utf-8') as f:
                import datetime
                f.write(f"\n{'='*20} {datetime.datetime.now()} {'='*20}\n")
                f.write(f"封装前脚本长度: {len(script_content)}\n")
                f.write(f"封装后 XML 长度: {len(config_xml)}\n")
                f.write(f"XML 内容预览:\n{config_xml}\n")
                f.write(f"{'='*50}\n")
        except Exception as e:
            logger.error(f"写入调试日志失败: {e}")

        logger.info(f"Pipeline XML 封装完成 - XML: {len(config_xml)} 字符, 脚本: {len(script_content)} 字符")
        return config_xml


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

            #===================
            logger.info(f"收到 config_xml 长度: {len(config_xml) if config_xml else 0}")
            logger.info(f"job_type: {job_type}")
            logger.info(f"config_xml 前 200 字符: {config_xml[:200] if config_xml else 'None'}")
            logger.info(f"是否包含 <flow-definition: {'<flow-definition' in config_xml if config_xml else False}")
            logger.info(f"是否包含 <![CDATA[: {'<![CDATA[' in config_xml if config_xml else False}")
                
            # 检查是否触发 CDATA 封装   
            if job_type == 'Pipeline' and config_xml and '<flow-definition' not in config_xml:
                if not config_xml.strip().startswith('<'):
                    logger.info("✅ 条件满足：将使用 CDATA 封装")
                    config_xml = self._wrap_pipeline_script_in_xml(
                        script_content=config_xml,
                        description=request.data.get('description', '')
                    )
                    logger.info(f"✅ CDATA 封装完成，新 XML 长度: {len(config_xml)}")
                    logger.info(f"封装后是否包含 CDATA: {'<![CDATA[' in config_xml}")
                else:
                    logger.warning("⚠️ config_xml 以 < 开头，判断为 XML 格式，跳过封装")
            else:
                logger.warning(f"⚠️ 未触发 CDATA 封装 - job_type={job_type}, has_config={bool(config_xml)}, has_flow_def={'<flow-definition' in config_xml if config_xml else False}")
            
            # 在发送到 Jenkins 前，再次确认
            logger.info("=" * 60)
            logger.info("准备发送到 Jenkins 的 XML:")
            logger.info(f"- 总长度: {len(config_xml)}")
            logger.info(f"- 包含 CDATA: {'<![CDATA[' in config_xml}")
            logger.info(f"- 前 500 字符:\n{config_xml[:500]}")
            logger.info("=" * 60)
        

            #====================



            # 获取环境ID列表
            environment_ids = request.data.get('environments', [])

            # 从测试环境获取节点信息（环境名称即为节点名称）
            node_labels = []
            environment_names = []

            if environment_ids and len(environment_ids) > 0:
                from project.models import Environment
                environments = Environment.objects.filter(id__in=environment_ids)

                # 收集环境名（环境名即节点名）
                for env in environments:
                    if env.name:
                        environment_names.append(env.name)
                        node_labels.append(env.name)

                # 构建节点标签字符串
                node_label = ','.join(node_labels) if node_labels else 'any'

                logger.info(f"从环境获取节点（环境名即节点名），环境数: {len(environment_ids)}, 环境: {environment_names}, 节点: {node_label}")

            # ===== 新增：Pipeline 生成器逻辑 =====
            if not config_xml and job_type == 'Pipeline':
                # Pipeline 类型：使用新的动态生成器
                logger.info("使用 Pipeline 生成器动态生成配置")

                # 获取 Pipeline 配置
                pipeline_config = request.data.get('pipeline_config', {})

                # 构建生成器配置
                generator_config = {
                    'name': job_name,
                    'description': request.data.get('description', ''),
                    'node_label': node_label,
                    'environment_names': environment_names,  # 新增：环境名称列表
                    'pre_script': pipeline_config.get('simple', {}).get('preScript', ''),
                    'test_command': pipeline_config.get('simple', {}).get('testCommand', ''),
                    'post_script': pipeline_config.get('simple', {}).get('postScript', ''),
                    # 定时任务配置
                    'cron_enabled': request.data.get('cron_enabled', False),
                    'cron_schedule': request.data.get('cron_schedule', ''),
                }

                # 处理自定义 stages
                if pipeline_config.get('type') == 'custom' and pipeline_config.get('custom'):
                    generator_config['stages'] = pipeline_config['custom']

                # 创建生成器
                use_custom_stages = pipeline_config.get('type') == 'custom'

                # 根据节点数量自动选择模式
                if use_custom_stages:
                    # 自定义 stages 使用 label 模式
                    multi_node_mode = 'label'
                else:
                    # 解析节点数量
                    if isinstance(node_label, str):
                        node_count = len([label.strip() for label in node_label.split(',') if label.strip()])
                    elif isinstance(node_label, list):
                        node_count = len(node_label)
                    else:
                        node_count = 1

                    # 多节点使用 matrix 模式，单节点使用 label 模式
                    multi_node_mode = 'matrix' if node_count > 1 else 'label'

                generator = create_pipeline_generator(generator_config, multi_node_mode, use_custom_stages)

                # 生成配置 XML
                config_xml = generator.generate_job_config_xml()
                logger.info(f"Pipeline 配置已生成，节点: {node_label}, 环境: {environment_names}")
            # ===== 结束新增 =====

            if not config_xml:
                # 非 Pipeline 类型或用户未提供配置：从模板加载
                config_xml = self._load_template_xml(job_type, request.data.get('description', ''), node_label)
            elif request.data.get('use_visual_builder', False) == False:
                # 用户提供了 config_xml：替换节点占位符（仅高级模式）
                config_xml = self._replace_agent_placeholder(config_xml, node_label)
                
                # 自动识别并封装纯 Pipeline 脚本
                if job_type == 'Pipeline' and config_xml and '<flow-definition' not in config_xml:
                    if not config_xml.strip().startswith('<'):
                        logger.info("检测到纯 Pipeline 脚本，自动封装为 XML")
                        config_xml = self._wrap_pipeline_script_in_xml(
                            script_content=config_xml,
                            description=request.data.get('description', '')
                        )


                # XML 校验 (已禁用：直接依赖 Jenkins API 的返回结果)
                # from ..jenkins_client import validate_xml
                # is_valid, errors = validate_xml(config_xml)
                # if not is_valid and not force:
                #     return R.error(
                #         message="XML 验证失败,请修复后重试或强制保存",
                #         code=ResponseCode.JENKINS_XML_INVALID,
                #         data={'errors': errors, 'need_force': True}
                #     )

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

                # 判断是否为多节点父 Job（基于环境数量）
                is_multi_node_parent = len(environment_ids) > 1

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
                    is_multi_node_parent=is_multi_node_parent,
                    created_by=created_by,
                    last_sync_time=timezone.now(), # 设置同步时间，确保显示在列表顶部
                    # 定时任务配置
                    cron_enabled=request.data.get('cron_enabled', False),
                    cron_schedule=request.data.get('cron_schedule', ''),
                    pipeline_config=request.data.get('pipeline_config', {}),
                )

                # 设置环境多对多关系
                if environment_ids:
                    job.environments.set(environment_ids)

                # 根据环境名称（节点标签）查找并设置对应的节点
                if environment_ids:
                    from project.models import Environment
                    environments = Environment.objects.filter(id__in=environment_ids)
                    # 环境名称即为节点名称，通过名称匹配节点
                    env_names = [env.name for env in environments if env.name]
                    if env_names:
                        # 查找匹配的 JenkinsNode（按名称匹配）
                        matching_nodes = JenkinsNode.objects.filter(name__in=env_names, server=server)
                        if matching_nodes.exists():
                            job.nodes.set(matching_nodes)
                            logger.info(f"从环境设置了 {matching_nodes.count()} 个执行节点: {list(matching_nodes.values_list('name', flat=True))}")

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
            
            # 🔥🔥🔥 强制调试日志 🔥🔥🔥
            config_xml = request.data.get('config_xml')
            print(f"【DEBUG】PUT 请求收到: job_id={job_id}")
            print("-" * 60)
            print(f"【DEBUG】config_xml 长度: {len(config_xml) if config_xml else 0}")
            print(f"【DEBUG】config_xml 前 500 字符:\n{config_xml[:500] if config_xml else 'None'}")
            print(f"【DEBUG】是否包含 <flow-definition: {'<flow-definition' in config_xml if config_xml else False}")
            print("-" * 60)
            
            # 🔍 写文件调试
            try:
                # 尝试使用绝对路径，避免路径问题
                import os
                log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'debug_pipeline.log')
                print(f"【DEBUG】尝试写入日志文件: {log_path}")
                with open(log_path, 'a', encoding='utf-8') as f:
                    import datetime
                    f.write(f"\n{'='*20} {datetime.datetime.now()} [PUT] {'='*20}\n")
                    f.write(f"PUT 请求收到 job_id: {job_id}\n")
                    f.write(f"config_xml 长度: {len(config_xml) if config_xml else 0}\n")
                    # 🔥 打印完整内容，不截断
                    f.write(f"完整 XML 内容:\n{config_xml}\n")
                    f.write(f"{'='*50}\n")
            except Exception as e:
                print(f"【ERROR】写入日志文件失败: {e}")

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
            
            # 调试日志
            logger.info(f"编辑请求数据包含字段: {list(data.keys())}")
            logger.info(f"Pipeline 类型: {job.job_type}")
            if 'use_visual_builder' in data:
                logger.info(f"use_visual_builder: {data.get('use_visual_builder')}")
            if 'config_xml' in data:
                logger.info(f"收到 config_xml，长度: {len(data.get('config_xml', ''))} 字符")
            if 'pipeline_config' in data:
                logger.info(f"收到 pipeline_config: {data.get('pipeline_config')}")
            
            # 需要同步到 Jenkins 的字段
            need_jenkins_sync = False
            jenkins_operations = []  # 记录需要执行的 Jenkins 操作
            
            # 4. 处理 config_xml（包含 description）
            if 'config_xml' in data or 'description' in data:
                need_jenkins_sync = True
                
                # 优先使用 config_xml，否则先获取现有配置
                if 'config_xml' in data:
                    config_xml = data['config_xml']
                    logger.info(f"使用提交的 config_xml 更新 Jenkins")
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
                
                # 自动识别并封装纯 Pipeline 脚本
                job_type = job.job_type
                is_pipeline = 'Pipeline' in job_type or '<flow-definition' in job.config_xml
                
                if is_pipeline and config_xml:
                    # 情况1：纯脚本（不含 XML 标签）
                    if '<flow-definition' not in config_xml and not config_xml.strip().startswith('<'):
                        logger.info("编辑模式：检测到纯 Pipeline 脚本，自动封装为 XML")
                        config_xml = self._wrap_pipeline_script_in_xml(
                            script_content=config_xml,
                            description=data.get('description', job.description)
                        )
                    
                    # 情况2：是 XML 但缺少 CDATA（常见于手动复制或前端格式化）
                    elif '<flow-definition' in config_xml and '<script><![CDATA[' not in config_xml and '<script>' in config_xml:
                        logger.info("编辑模式：检测到 XML 缺少 CDATA，正在尝试自动修复...")
                        import re
                        import html
                        # 提取 script 标签内容
                        match = re.search(r'<script>(.*?)</script>', config_xml, re.DOTALL)
                        if match:
                            raw_script = match.group(1).strip()
                            # 反转义（把 &lt; 变回 <）
                            raw_script = html.unescape(raw_script)
                            logger.info(f"成功提取并还原脚本内容，长度: {len(raw_script)}")
                            
                            # 重新封装为标准格式
                            config_xml = self._wrap_pipeline_script_in_xml(
                                script_content=raw_script,
                                description=data.get('description', job.description)
                            )

                # XML 软检查 (已禁用)
                # from ..jenkins_client import validate_xml
                # is_valid, errors = validate_xml(config_xml)
                
                # if not is_valid and not force:
                #     logger.warning(f"XML 验证失败: {errors}")
                #     return R.error(
                #         message="XML 验证失败，请修复后重试或强制保存",
                #         code=ResponseCode.JENKINS_XML_INVALID,
                #         data={
                #             'errors': errors,
                #             'need_force': True
                #         }
                #     )
                
                jenkins_operations.append(('update_config', config_xml))
            
            # 5. 处理定时任务变更（需要更新 XML 中的 triggers 块）
            if 'cron_enabled' in data or 'cron_schedule' in data:
                # 定时任务配置改变，需要重新生成 config_xml
                need_jenkins_sync = True
                logger.info("检测到定时任务配置变更，需要更新 Jenkins XML")
                
                # 获取当前 config_xml
                if 'config_xml' in data:
                    # 如果同时修改了 config_xml，使用新的 XML
                    base_xml = data['config_xml']
                else:
                    # 否则获取现有配置
                    from ..jenkins_client import get_job_config
                    success, message, existing_config = get_job_config(job.name)
                    if not success or not existing_config.get('config_xml'):
                        logger.warning(f"获取现有配置失败，尝试使用数据库中的 config_xml")
                        base_xml = job.config_xml or ''
                    else:
                        base_xml = existing_config.get('config_xml', '')
                
                # 更新 triggers 块
                cron_enabled = data.get('cron_enabled', job.cron_enabled)
                cron_schedule = data.get('cron_schedule', job.cron_schedule)
                
                config_xml = self._update_triggers_in_xml(base_xml, cron_enabled, cron_schedule)
                jenkins_operations.append(('update_config', config_xml))
                
                # 更新 config_xml 到数据中，确保后续保存到DB
                data['config_xml'] = config_xml
                
                logger.info(f"定时任务配置: enabled={cron_enabled}, schedule={cron_schedule}")
            
            # 6. 处理 is_active
            if 'is_active' in data:
                new_active = data['is_active']
                if new_active != job.is_active:
                    need_jenkins_sync = True
                    action = 'enable' if new_active else 'disable'
                    jenkins_operations.append((action, None))
            
            # 7. 执行 Jenkins 同步操作
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
            
            # 定时任务字段
            if 'cron_enabled' in data:
                job.cron_enabled = data['cron_enabled']
                update_fields.append('cron_enabled')
            
            if 'cron_schedule' in data:
                job.cron_schedule = data['cron_schedule']
                update_fields.append('cron_schedule')
            
            if 'pipeline_config' in data:
                job.pipeline_config = data['pipeline_config']
                update_fields.append('pipeline_config')
            
            # 仅本地字段（不需要同步到 Jenkins）
            if 'project' in data:
                job.project_id = data['project']
                update_fields.append('project')
            
            if 'plan' in data:
                job.plan_id = data['plan']
                update_fields.append('plan')
            
            if 'target_node' in data:
                job.target_node_id = data['target_node']
                update_fields.append('target_node')
            
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
    
    def _load_template_xml(self, job_type='FreeStyle', description='', node_label='any'):
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
            
            # 替换 agent 占位符
            if '{{agent_label}}' in config_xml:
                if node_label and node_label != 'any':
                    agent_str = f"{{ label '{node_label}' }}"
                else:
                    agent_str = 'any'
                config_xml = config_xml.replace('{{agent_label}}', agent_str)
            
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
    
    def _update_triggers_in_xml(self, config_xml: str, cron_enabled: bool, cron_schedule: str) -> str:
        """
        更新 XML 中的 triggers 块
        
        Args:
            config_xml: 原始 XML 配置
            cron_enabled: 是否启用定时任务
            cron_schedule: Cron 表达式
            
        Returns:
            更新后的 XML 字符串
        """
        import xml.etree.ElementTree as ET
        
        try:
            root = ET.fromstring(config_xml)
            
            # 查找或创建 triggers 元素
            triggers_elem = root.find('triggers')
            if triggers_elem is None:
                # 如果没有 triggers 元素，创建一个
                triggers_elem = ET.SubElement(root, 'triggers')
            
            # 清空现有的 TimerTrigger
            for timer in triggers_elem.findall('hudson.triggers.TimerTrigger'):
                triggers_elem.remove(timer)
            
            # 如果启用了定时任务，添加 TimerTrigger
            if cron_enabled and cron_schedule:
                timer_trigger = ET.SubElement(triggers_elem, 'hudson.triggers.TimerTrigger')
                spec = ET.SubElement(timer_trigger, 'spec')
                spec.text = cron_schedule
                logger.info(f"已添加定时触发器: {cron_schedule}")
            else:
                logger.info("定时触发器已移除或禁用")
            
            # 转换回字符串
            return ET.tostring(root, encoding='unicode')
            
        except Exception as e:
            logger.error(f"更新 triggers 块失败: {e}")
            # 如果解析失败，返回原 XML
            return config_xml
    
    def _replace_agent_placeholder(self, config_xml, node_label='any'):
        """
        替换 config_xml 中的 agent 占位符
        
        Args:
            config_xml: 配置 XML 字符串
            node_label: 节点标签,默认 'any'
            
        Returns:
            替换后的 XML 字符串
        """
        if '{{agent_label}}' in config_xml:
            if node_label and node_label != 'any':
                agent_str = f"{{ label '{node_label}' }}"
            else:
                agent_str = 'any'
            config_xml = config_xml.replace('{{agent_label}}', agent_str)
        
        return config_xml
