"""
Jenkins 客户端 - 启用 CSRF Crumb 支持
"""
import jenkins
import requests
import logging

logger = logging.getLogger(__name__)

# Jenkins 配置
JENKINS_URL = "http://mg.morry.online"
USERNAME = "akko"
TOKEN = "112f35231e8ffe20994a406815179d8a68"


def get_jenkins_client():
    """
    获取 Jenkins 客户端实例
    
    Returns:
        jenkins.Jenkins: Jenkins 客户端对象
    """
    try:
        client = jenkins.Jenkins(
            url=JENKINS_URL,
            username=USERNAME,
            password=TOKEN,
            # use_crumb=True  # 关键参数：启用 CSRF crumb 保护
        )
        
        logger.info(f"Jenkins 客户端创建成功: {JENKINS_URL}")
        return client
        
    except Exception as e:
        logger.error(f"创建 Jenkins 客户端失败: {str(e)}")
        raise


def test_connection():
    """
    测试 Jenkins 连接
    
    Returns:
        tuple: (是否成功, 消息, 数据)
    """
    try:
        client = get_jenkins_client()
        
        # 获取版本信息
        version = client.get_version()
        logger.info(f"Jenkins 版本: {version}")
        
        # 获取用户信息
        user_info = client.get_whoami()
        logger.info(f"当前用户: {user_info.get('fullName')}")
        
        return True, 'Jenkins连接成功', {
            'version': version,
            'user': user_info
        }
        
    except Exception as e:
        error_msg = f'Jenkins连接失败: {str(e)}'
        logger.error(error_msg)
        return False, error_msg, None


def get_all_jobs():
    """
    获取所有 Jobs
    
    Returns:
        tuple: (是否成功, 消息, jobs列表)
    """
    try:
        client = get_jenkins_client()
        jobs = client.get_all_jobs()
        
        logger.info(f"成功获取 {len(jobs)} 个 Jobs")
        
        return True, f'成功获取 {len(jobs)} 个 Jobs', jobs
        
    except Exception as e:
        error_msg = f"获取 Jobs 异常: {str(e)}"
        logger.error(error_msg)
        return False, error_msg, []


def get_job_detail(job_name):
    """
    获取 Jenkins Job 详细信息（包括 description, config.xml 等）
    
    Args:
        job_name: Job 名称
        
    Returns:
        (bool, str, dict): (是否成功, 消息, Job详情字典)
            详情字典包含: description, config_xml, last_build_number, last_build_status
    """
    try:
        # 获取 Job 详情 JSON (用于 description, lastBuild 等)
        # tree 参数优化：获取 description, lastBuild, buildable, inQueue
        json_url = f"{JENKINS_URL}/job/{job_name}/api/json?tree=description,buildable,inQueue,lastBuild[number,result,timestamp]"
        
        json_resp = requests.get(json_url, auth=(USERNAME, TOKEN), timeout=10)
        if json_resp.status_code != 200:
            return False, f"获取 Job JSON 失败: {json_resp.status_code}", None
            
        job_data = json_resp.json()
        
        # 获取 config.xml
        config_url = f"{JENKINS_URL}/job/{job_name}/config.xml"
        config_resp = requests.get(config_url, auth=(USERNAME, TOKEN), timeout=10)
        
        config_xml = ""
        if config_resp.status_code == 200:
            config_xml = config_resp.text
            
        # 组装返回数据
        # 组装返回数据
        last_build = job_data.get('lastBuild') or {}
        result = {
            'description': job_data.get('description'),
            'is_buildable': job_data.get('buildable', True),
            'config_xml': config_xml,
            'last_build_number': last_build.get('number'),
            'last_build_status': last_build.get('result') or '',
            # timestamp 需要转换，暂时先不做
        }
        
        return True, "获取成功", result

    except Exception as e:
        error_msg = f"获取 Job 详情异常: {str(e)}"
        logger.error(error_msg)
        return False, error_msg, None


def get_job_info(job_name):
    """
    获取指定 Job 的详细信息
    
    Args:
        job_name: Job 名称
        
    Returns:
        tuple: (是否成功, 消息, job信息)
    """
    try:
        client = get_jenkins_client()
        job_info = client.get_job_info(job_name)
        
        return True, '获取Job信息成功', job_info
        
    except Exception as e:
        error_msg = f'获取Job信息失败: {str(e)}'
        logger.error(error_msg)
        return False, error_msg, None


# ==================== Job CRUD 操作 ====================

def validate_xml(xml_content):
    """
    校验 XML 格式
    
    Args:
        xml_content: XML 字符串内容
        
    Returns:
        tuple: (是否有效, 错误列表)
    """
    try:
        from lxml import etree
    except ImportError:
        # 如果 lxml 未安装，使用基础的 XML 解析
        import xml.etree.ElementTree as ET
        try:
            ET.fromstring(xml_content)
            return True, []
        except ET.ParseError as e:
            return False, [{
                'type': 'syntax',
                'message': str(e),
                'line': e.position[0] if hasattr(e, 'position') else 'unknown'
            }]
    
    errors = []
    
    try:
        # 使用 lxml 进行更详细的校验
        parser = etree.XMLParser()
        root = etree.fromstring(xml_content.encode('utf-8'), parser)
        
        # 检查根节点类型是否为 Jenkins 支持的类型
        valid_root_tags = [
            'project',                    # Freestyle project
            'flow-definition',            # Pipeline
            'maven2-moduleset',           # Maven project
            'matrix-project',             # Multi-configuration project
            'org.jenkinsci.plugins.workflow.job.WorkflowJob'  # Pipeline (新版本)
        ]
        
        if root.tag not in valid_root_tags:
            errors.append({
                'type': 'structure',
                'message': f'根节点类型 "{root.tag}" 可能不被 Jenkins 支持',
                'suggestion': f'建议使用: {", ".join(valid_root_tags)}'
            })
        
        return len(errors) == 0, errors
        
    except etree.XMLSyntaxError as e:
        return False, [{
            'type': 'syntax',
            'message': str(e),
            'line': e.lineno,
            'column': e.offset
        }]
    except Exception as e:
        return False, [{
            'type': 'unknown',
            'message': str(e)
        }]


def create_job(job_name, config_xml):
    """
    创建 Jenkins Job
    
    Args:
        job_name: Job 名称
        config_xml: Job 的 XML 配置内容
        
    Returns:
        tuple: (是否成功, 消息, 数据)
    """
    try:
        client = get_jenkins_client()
        
        # 先检查 Job 是否已存在
        if client.job_exists(job_name):
            error_msg = f'Job [{job_name}] 已存在，无法创建'
            logger.warning(error_msg)
            return False, error_msg, None
        
        # 创建 Job
        client.create_job(job_name, config_xml)
        logger.info(f"成功创建 Job: {job_name}")
        
        return True, f'成功创建 Job [{job_name}]', {'job_name': job_name}
        
    except Exception as e:
        error_msg = f'创建 Job 失败: {str(e)}'
        logger.error(error_msg)
        return False, error_msg, None


def get_job_config(job_name):
    """
    获取 Job 的 XML 配置
    
    Args:
        job_name: Job 名称
        
    Returns:
        tuple: (是否成功, 消息, XML配置)
    """
    try:
        client = get_jenkins_client()
        config_xml = client.get_job_config(job_name)
        
        logger.info(f"成功获取 Job [{job_name}] 配置")
        return True, '获取Job配置成功', {'config_xml': config_xml}
        
    except Exception as e:
        error_msg = f'获取Job配置失败: {str(e)}'
        logger.error(error_msg)
        return False, error_msg, None


def update_job(job_name, config_xml):
    """
    更新 Job 配置
    
    Args:
        job_name: Job 名称
        config_xml: 新的 XML 配置内容
        
    Returns:
        tuple: (是否成功, 消息, 数据)
    """
    try:
        client = get_jenkins_client()
        
        # 检查 Job 是否存在
        if not client.job_exists(job_name):
            error_msg = f'Job [{job_name}] 不存在，无法更新'
            logger.warning(error_msg)
            return False, error_msg, None
        
        # 更新配置
        client.reconfig_job(job_name, config_xml)
        logger.info(f"成功更新 Job [{job_name}] 配置")
        
        return True, f'成功更新 Job [{job_name}]', {'job_name': job_name}
        
    except Exception as e:
        error_msg = f'更新 Job 失败: {str(e)}'
        logger.error(error_msg)
        return False, error_msg, None


def delete_job(job_name):
    """
    删除 Job
    
    Args:
        job_name: Job 名称
        
    Returns:
        tuple: (是否成功, 消息, 数据)
    """
    try:
        client = get_jenkins_client()
        
        # 检查 Job 是否存在
        if not client.job_exists(job_name):
            error_msg = f'Job [{job_name}] 不存在，无法删除'
            logger.warning(error_msg)
            return False, error_msg, None
        
        # 删除 Job
        client.delete_job(job_name)
        logger.info(f"成功删除 Job: {job_name}")
        
        return True, f'成功删除 Job [{job_name}]', {'job_name': job_name}
        
    except Exception as e:
        error_msg = f'删除 Job 失败: {str(e)}'
        logger.error(error_msg)
        return False, error_msg, None


def copy_job(source_job_name, new_job_name):
    """
    复制 Job（基于现有 Job 创建新 Job）
    
    Args:
        source_job_name: 源 Job 名称
        new_job_name: 新 Job 名称
        
    Returns:
        tuple: (是否成功, 消息, 数据)
    """
    try:
        client = get_jenkins_client()
        
        # 检查源 Job 是否存在
        if not client.job_exists(source_job_name):
            error_msg = f'源 Job [{source_job_name}] 不存在'
            logger.warning(error_msg)
            return False, error_msg, None
        
        # 检查新 Job 名称是否已被占用
        if client.job_exists(new_job_name):
            error_msg = f'Job [{new_job_name}] 已存在，无法复制'
            logger.warning(error_msg)
            return False, error_msg, None
        
        # 复制 Job
        client.copy_job(source_job_name, new_job_name)
        logger.info(f"成功复制 Job: {source_job_name} -> {new_job_name}")
        
        return True, f'成功复制 Job [{new_job_name}]', {
            'source_job': source_job_name,
            'new_job': new_job_name
        }
        
    except Exception as e:
        error_msg = f'复制 Job 失败: {str(e)}'
        logger.error(error_msg)
        return False, error_msg, None


def enable_job(job_name):
    """
    启用 Job
    
    Args:
        job_name: Job 名称
        
    Returns:
        tuple: (是否成功, 消息, 数据)
    """
    try:
        client = get_jenkins_client()
        
        if not client.job_exists(job_name):
            error_msg = f'Job [{job_name}] 不存在'
            logger.warning(error_msg)
            return False, error_msg, None
        
        client.enable_job(job_name)
        logger.info(f"成功启用 Job: {job_name}")
        
        return True, f'成功启用 Job [{job_name}]', {'job_name': job_name}
        
    except Exception as e:
        error_msg = f'启用 Job 失败: {str(e)}'
        logger.error(error_msg)
        return False, error_msg, None


def disable_job(job_name):
    """
    禁用 Job
    
    Args:
        job_name: Job 名称
        
    Returns:
        tuple: (是否成功, 消息, 数据)
    """
    try:
        client = get_jenkins_client()
        
        if not client.job_exists(job_name):
            error_msg = f'Job [{job_name}] 不存在'
            logger.warning(error_msg)
            return False, error_msg, None
        
        client.disable_job(job_name)
        logger.info(f"成功禁用 Job: {job_name}")
        
        return True, f'成功禁用 Job [{job_name}]', {'job_name': job_name}
        
    except Exception as e:
        error_msg = f'禁用 Job 失败: {str(e)}'
        logger.error(error_msg)
        return False, error_msg, None


def job_exists(job_name):
    """
    检查 Job 是否存在
    
    Args:
        job_name: Job 名称
        
    Returns:
        tuple: (是否成功, 消息, 数据)
    """
    try:
        client = get_jenkins_client()
        exists = client.job_exists(job_name)
        
        return True, 'Job存在性检查完成', {'exists': exists, 'job_name': job_name}
        
    except Exception as e:
        error_msg = f'检查 Job 是否存在失败: {str(e)}'
        logger.error(error_msg)
        return False, error_msg, None


# ==================== Build 操作 ====================

def build_job(job_name, parameters=None):
    """
    触发 Job 构建
    
    Args:
        job_name: Job 名称
        parameters: 构建参数（字典格式，可选）
        
    Returns:
        tuple: (是否成功, 消息, 队列ID)
    """
    try:
        client = get_jenkins_client()
        
        #首先检查 Job 是否存在
        if not client.job_exists(job_name):
            error_msg = f'Job [{job_name}] 不存在，无法触发构建'
            logger.error(error_msg)
            return False, error_msg, None
        
        # 如果传递了参数，先检查 Job 是否支持参数
        if parameters:
            try:
                # 获取 Job 信息
                job_info = client.get_job_info(job_name)
                
                # 检查是否有参数定义
                has_parameters = False
                if 'property' in job_info:
                    for prop in job_info['property']:
                        if 'parameterDefinitions' in prop:
                            has_parameters = True
                            break
                
                if not has_parameters:
                    logger.warning(f"Job [{job_name}] 未定义参数，但提供了参数。将尝试无参数构建")
                    # 改为无参数构建
                    queue_id = client.build_job(job_name)
                else:
                    # 使用参数构建
                    queue_id = client.build_job(job_name, parameters=parameters)
                    
            except Exception as param_error:
                # 如果参数检查失败，尝试直接构建
                logger.warning(f"参数检查失败，尝试直接构建: {str(param_error)}")
                try:
                    queue_id = client.build_job(job_name, parameters=parameters)
                except:
                    # 最后尝试无参数构建
                    queue_id = client.build_job(job_name)
        else:
            # 无参数构建
            queue_id = client.build_job(job_name)
        
        logger.info(f"成功触发 Job [{job_name}] 构建，队列ID: {queue_id}")
        
        return True, '成功触发构建', {'queue_id': queue_id}
        
    except jenkins.JenkinsException as je:
        # Jenkins 特定异常
        error_msg = f'Jenkins 错误: {str(je)}'
        logger.error(error_msg)
        return False, error_msg, None
    except Exception as e:
        # 详细的错误信息
        error_msg = f'触发构建失败: {str(e)}'
        error_type = type(e).__name__
        logger.error(f"{error_msg} (异常类型: {error_type})")
        
        # 提供更友好的错误提示
        if 'JSON' in str(e) or 'json' in str(e):
            friendly_msg = f"Job [{job_name}] 可能未定义参数，但尝试传递了参数。请检查 Job 配置或不传递 parameters 参数"
            return False, friendly_msg, None
        
        return False, error_msg, None


def get_build_info(job_name, build_number):
    """
    获取指定构建的详细信息
    
    Args:
        job_name: Job 名称
        build_number: 构建编号
        
    Returns:
        tuple: (是否成功, 消息, 构建信息)
    """
    try:
        client = get_jenkins_client()
        build_info = client.get_build_info(job_name, build_number)
        
        return True, '获取构建信息成功', build_info
        
    except Exception as e:
        error_msg = f'获取构建信息失败: {str(e)}'
        logger.error(error_msg)
        return False, error_msg, None


def get_build_console_output(job_name, build_number):
    """
    获取构建的控制台输出
    
    Args:
        job_name: Job 名称
        build_number: 构建编号
        
    Returns:
        tuple: (是否成功, 消息, 控制台输出)
    """
    try:
        client = get_jenkins_client()
        console_output = client.get_build_console_output(job_name, build_number)
        
        return True, '获取控制台输出成功', {'console': console_output}
        
    except Exception as e:
        error_msg = f'获取控制台输出失败: {str(e)}'
        logger.error(error_msg)
        return False, error_msg, None


def get_allure_report_url(job_name, build_number):
    """
    获取 Allure 报告 URL
    
    注意：Jenkins API 无法可靠检测 Allure 报告是否存在，
    因此直接返回标准 URL，由前端自行验证。
    
    Args:
        job_name: Job 名称
        build_number: 构建编号
        
    Returns:
        tuple: (是否成功, 消息, 数据)
        数据格式: {
            'allure_url': str,
            'job_name': str,
            'build_number': int
        }
    """
    try:
        client = get_jenkins_client()
        
        # 验证构建是否存在
        build_info = client.get_build_info(job_name, build_number)
        
        # 直接构造 Allure 报告的标准 URL
        # 注意：无法通过 API 可靠检测报告是否存在，由前端自行验证
        allure_url = f"{JENKINS_URL}/job/{job_name}/{build_number}/allure/"
        
        return True, "Allure 报告 URL 已生成", {
            'allure_url': allure_url,
            'job_name': job_name,
            'build_number': build_number
        }
        
    except Exception as e:
        error_msg = f'获取 Allure 报告失败: {str(e)}'
        logger.error(error_msg)
        return False, error_msg, None
