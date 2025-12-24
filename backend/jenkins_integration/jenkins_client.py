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
# TOKEN = "1118c6009a9ea266a6f4edabf6c159c8f9"


def get_jenkins_client(url=None, username=None, token=None):
    """
    获取 Jenkins 客户端实例
    
    Args:
        url: Jenkins URL (可选，默认使用配置)
        username: 用户名 (可选，默认使用配置)
        token: API Token (可选，默认使用配置)
        
    Returns:
        jenkins.Jenkins: Jenkins 客户端对象
    """
    try:
        # 使用传入的参数 或 全局配置
        target_url = url or JENKINS_URL
        target_username = username or USERNAME
        target_token = token or TOKEN
        
        client = jenkins.Jenkins(
            url=target_url,
            username=target_username,
            password=target_token,
            # use_crumb=True  # 关键参数：启用 CSRF crumb 保护
        )
        
        # 仅在第一次或连接不同服务器时日志
        # logger.info(f"Jenkins 客户端创建成功: {target_url}")
        return client
        
    except Exception as e:
        logger.error(f"创建 Jenkins 客户端失败: {str(e)}")
        raise


def test_connection(url=None, username=None, token=None):
    """
    测试 Jenkins 连接
    
    Args:
        url: Jenkins URL
        username: 用户名
        token: API Token
        
    Returns:
        tuple: (是否成功, 消息, 数据)
    """
    try:
        # 即使参数为 None，get_jenkins_client 也会处理
        client = get_jenkins_client(url, username, token)
        
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
        error_msg = f"获取 Job [{job_name}] 详情异常: {str(e)}"
        logger.error(error_msg)
        return False, error_msg, None


def get_all_jobs_by_server(server):
    """
    获取指定服务器的所有 Jobs
    
    Args:
        server: JenkinsServer 模型实例
        
    Returns:
        tuple: (是否成功, 消息, jobs列表)
    """
    try:
        # 使用服务器的凭据创建客户端
        client = get_jenkins_client(
            url=server.url,
            username=server.username,
            token=server.token
        )
        jobs = client.get_all_jobs()
        
        logger.info(f"从服务器 [{server.name}] 成功获取 {len(jobs)} 个 Jobs")
        return True, f'成功获取 {len(jobs)} 个 Jobs', jobs
        
    except Exception as e:
        error_msg = f"从服务器 [{server.name}] 获取 Jobs 异常: {str(e)}"
        logger.error(error_msg)
        return False, error_msg, []


def get_job_detail_by_server(server, job_name):
    """
    获取指定服务器上的 Jenkins Job 详细信息
    
    Args:
        server: JenkinsServer 模型实例
        job_name: Job 名称
        
    Returns:
        (bool, str, dict): (是否成功, 消息, Job详情字典)
    """
    try:
        # 使用服务器的凭据
        server_url = server.url.rstrip('/')
        
        # 获取 Job 详情 JSON
        json_url = f"{server_url}/job/{job_name}/api/json?tree=description,buildable,inQueue,lastBuild[number,result,timestamp]"
        
        json_resp = requests.get(
            json_url, 
            auth=(server.username, server.token), 
            timeout=10
        )
        if json_resp.status_code != 200:
            return False, f"获取 Job JSON 失败: {json_resp.status_code}", None
            
        job_data = json_resp.json()
        
        # 获取 config.xml
        config_url = f"{server_url}/job/{job_name}/config.xml"
        config_resp = requests.get(
            config_url, 
            auth=(server.username, server.token), 
            timeout=10
        )
        
        config_xml = ""
        if config_resp.status_code == 200:
            config_xml = config_resp.text
            
        # 组装返回数据
        last_build = job_data.get('lastBuild') or {}
        result = {
            'description': job_data.get('description'),
            'is_buildable': job_data.get('buildable', True),
            'config_xml': config_xml,
            'last_build_number': last_build.get('number'),
            'last_build_status': last_build.get('result') or '',
        }
        
        return True, "获取成功", result

    except Exception as e:
        error_msg = f"从服务器 [{server.name}] 获取 Job [{job_name}] 详情异常: {str(e)}"
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


# ==================== Node 节点操作 ====================

def extract_ip_from_node_config(config_xml):
    """
    从节点配置 XML 中提取 IP 地址或主机名
    
    适用于 SSH launcher 节点配置，从 <launcher><host> 标签提取主机信息
    
    Args:
        config_xml: 节点配置 XML 字符串
        
    Returns:
        str: IP地址或主机名，提取失败返回空字符串
    """
    try:
        import xml.etree.ElementTree as ET
        root = ET.fromstring(config_xml)
        
        # 提取 launcher 中的 host 字段
        # SSH launcher: <launcher class="hudson.plugins.sshslaves.SSHLauncher">
        #   <host>192.168.1.100</host>
        # </launcher>
        launcher = root.find('.//launcher')
        if launcher is not None:
            host = launcher.find('host')
            if host is not None and host.text:
                return host.text.strip()
        
        return ''
    except Exception as e:
        logger.debug(f"从XML提取IP失败: {str(e)}")
        return ''


def get_all_nodes():
    """
    获取所有 Jenkins 节点信息
    
    Returns:
        tuple: (是否成功, 消息, nodes列表)
        nodes格式: [
            {
                'name': str,                # 节点名称
                'displayName': str,         # 显示名称
                'description': str,         # 描述
                'numExecutors': int,        # 执行器数量
                'labels': str,              # 标签(逗号分隔)
                'offline': bool,            # 是否离线
                'temporarilyOffline': bool, # 是否临时离线
                'idle': bool,               # 是否空闲
                'offlineCauseReason': str   # 离线原因
            }
        ]
    """
    try:
        client = get_jenkins_client()
        
        # 获取所有节点信息
        nodes_info = client.get_nodes()
        
        # 解析节点数据
        nodes_list = []
        for node in nodes_info:
            node_name = node.get('name', '')
            
            try:
                # 获取节点详细信息 (使用 depth=1 获取更详细的launcher配置)
                node_info = client.get_node_info(node_name, depth=1)
                
                # 提取IP地址 - 采用多层次方法，按优先级依次尝试
                ip_address = ''
                extraction_method = 'none'  # 记录使用的提取方法，便于调试
                
                # ===== 方法1: 从节点配置XML中提取 (优先级最高，最可靠) =====
                try:
                    config_xml = client.get_node_config(node_name)
                    ip_address = extract_ip_from_node_config(config_xml)
                    if ip_address:
                        extraction_method = 'xml_config'
                        logger.debug(f"节点 [{node_name}] 通过XML配置获取IP: {ip_address}")
                except Exception as e:
                    logger.debug(f"节点 [{node_name}] 获取XML配置失败: {str(e)}")
                
                # ===== 方法2: 从 launcher 配置中提取 =====
                if not ip_address and 'launcher' in node_info:
                    launcher = node_info.get('launcher', {})
                    if isinstance(launcher, dict):
                        # 尝试多个可能的字段名
                        ip_address = launcher.get('host', '') or launcher.get('hostName', '') or launcher.get('hostname', '')
                        if ip_address:
                            extraction_method = 'launcher_config'
                            logger.debug(f"节点 [{node_name}] 通过launcher配置获取IP: {ip_address}")
                
                # ===== 方法3: 从 monitorData 中获取 (保留现有逻辑作为后备) =====
                if not ip_address:
                    monitor_data = node_info.get('monitorData', {})
                    
                    # 尝试从 ArchitectureMonitor 获取
                    if 'hudson.node_monitors.ArchitectureMonitor' in monitor_data:
                        arch_monitor = monitor_data['hudson.node_monitors.ArchitectureMonitor']
                        if isinstance(arch_monitor, dict):
                            ip_address = arch_monitor.get('ip', '')
                            if ip_address:
                                extraction_method = 'monitor_arch'
                    
                    # 尝试从 ResponseTimeMonitor 获取
                    if not ip_address and 'hudson.node_monitors.ResponseTimeMonitor' in monitor_data:
                        response_monitor = monitor_data['hudson.node_monitors.ResponseTimeMonitor']
                        if isinstance(response_monitor, dict):
                            ip_address = response_monitor.get('ip', '')
                            if ip_address:
                                extraction_method = 'monitor_response'
                    
                    if ip_address:
                        logger.debug(f"节点 [{node_name}] 通过monitorData获取IP: {ip_address}")
                
                # ===== 方法4: 从 displayName 或 description 中提取IP (最后的后备方案) =====
                if not ip_address:
                    import re
                    # 简单的IP正则匹配
                    ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
                    display_name = node_info.get('displayName', '')
                    description = node_info.get('description', '')
                    
                    ip_match = re.search(ip_pattern, display_name)
                    if ip_match:
                        ip_address = ip_match.group(0)
                        extraction_method = 'regex_displayname'
                    else:
                        ip_match = re.search(ip_pattern, description)
                        if ip_match:
                            ip_address = ip_match.group(0)
                            extraction_method = 'regex_description'
                    
                    if ip_address:
                        logger.debug(f"节点 [{node_name}] 通过正则匹配获取IP: {ip_address}")
                
                # 记录最终结果
                if ip_address:
                    logger.info(f"节点 [{node_name}] IP提取成功: {ip_address} (方法: {extraction_method})")
                else:
                    logger.warning(f"节点 [{node_name}] 未能提取到IP地址")
                
                # 提取关键信息
                node_data = {
                    'name': node_name,
                    'displayName': node_info.get('displayName', node_name),
                    'description': node_info.get('description', ''),
                    'numExecutors': node_info.get('numExecutors', 1),
                    'labels': ','.join([label.get('name', '') for label in node_info.get('assignedLabels', [])]),
                    'ip_address': ip_address,  # 添加IP地址
                    'offline': node_info.get('offline', False),
                    'temporarilyOffline': node_info.get('temporarilyOffline', False),
                    'idle': node_info.get('idle', True),
                    'offlineCauseReason': node_info.get('offlineCauseReason', '') if node_info.get('offline') else ''
                }
                
                nodes_list.append(node_data)
                logger.info(f"成功获取节点信息: {node_name}")
                
            except Exception as e:
                logger.warning(f"获取节点 [{node_name}] 详细信息失败: {str(e)}")
                # 即使获取详情失败,也添加基本信息
                nodes_list.append({
                    'name': node_name,
                    'displayName': node_name,
                    'description': '',
                    'numExecutors': 1,
                    'labels': '',
                    'offline': True,
                    'temporarilyOffline': False,
                    'idle': False,
                    'offlineCauseReason': f'获取详情失败: {str(e)}'
                })
        
        logger.info(f"成功获取 {len(nodes_list)} 个节点信息")
        return True, f'成功获取 {len(nodes_list)} 个节点', nodes_list
        
    except Exception as e:
        error_msg = f'获取节点信息失败: {str(e)}'
        logger.error(error_msg)
        return False, error_msg, None


# ==================== Node IP 管理操作 ====================

def get_node_config(node_name):
    """
    获取节点的 XML 配置
    
    Args:
        node_name: 节点名称
        
    Returns:
        tuple: (是否成功, 消息, 配置XML字符串)
    """
    try:
        client = get_jenkins_client()
        config_xml = client.get_node_config(node_name)
        
        logger.info(f"成功获取节点 [{node_name}] 配置")
        return True, '获取节点配置成功', {'config_xml': config_xml}
        
    except Exception as e:
        error_msg = f'获取节点配置失败: {str(e)}'
        logger.error(error_msg)
        return False, error_msg, None


def get_node_current_ip(node_name):
    """
    获取节点当前的 IP 地址
    
    Args:
        node_name: 节点名称
        
    Returns:
        tuple: (是否成功, 消息, 数据)
        数据格式: {
            'node_name': str,
            'current_ip': str,
            'ssh_port': str or None
        }
    """
    try:
        import xml.etree.ElementTree as ET
        
        client = get_jenkins_client()
        config_xml = client.get_node_config(node_name)
        root = ET.fromstring(config_xml)
        
        # 查找 SSH 主机 IP
        host_elem = root.find(".//host")
        current_ip = host_elem.text if host_elem is not None and host_elem.text else None
        
        # 查找 SSH 端口
        port_elem = root.find(".//port")
        ssh_port = port_elem.text if port_elem is not None and port_elem.text else None
        
        if current_ip:
            logger.info(f"节点 [{node_name}] 当前 IP: {current_ip}, 端口: {ssh_port}")
            return True, '成功获取节点IP配置', {
                'node_name': node_name,
                'current_ip': current_ip,
                'ssh_port': ssh_port
            }
        else:
            logger.warning(f"未找到节点 [{node_name}] 的 IP 配置")
            return False, '未找到节点的IP配置', None
            
    except Exception as e:
        error_msg = f'获取节点IP失败: {str(e)}'
        logger.error(error_msg)
        return False, error_msg, None


def update_node_ip(node_name, new_ip, ssh_port=None, credential_id=None):
    """
    更新节点的主机 IP 地址和SSH凭证
    
    参考 update_node_ip.py demo 实现
    
    Args:
        node_name: 节点名称
        new_ip: 新的 IP 地址
        ssh_port: SSH 端口(可选,默认保持不变)
        credential_id: SSH凭证ID(可选,默认保持不变)
        
    Returns:
        tuple: (是否成功, 消息, 数据)
        数据格式: {
            'node_name': str,
            'old_ip': str,
            'new_ip': str,
            'updated': bool
        }
    """
    try:
        import xml.etree.ElementTree as ET
        
        client = get_jenkins_client()
        
        logger.info(f"开始更新节点 [{node_name}] 的 IP 地址")
        
        # 1. 获取当前节点配置
        config_xml = client.get_node_config(node_name)
        
        # 2. 解析 XML
        root = ET.fromstring(config_xml)
        
        # 标记是否有更新
        updated = False
        old_ip = None
        
        # 3. 更新 SSH 主机 IP(对于 SSH 连接节点)
        host_elements = root.findall(".//host")
        for host_elem in host_elements:
            old_ip = host_elem.text
            if old_ip != new_ip:
                host_elem.text = new_ip
                updated = True
                logger.info(f"✓ 更新 SSH 主机 IP: {old_ip} → {new_ip}")
            else:
                logger.info(f"IP 地址已经是 {new_ip},无需更新")
        
        # 4. 更新端口(如果指定)
        if ssh_port:
            port_elements = root.findall(".//port")
            for port_elem in port_elements:
                old_port = port_elem.text
                if old_port != str(ssh_port):
                    port_elem.text = str(ssh_port)
                    updated = True
                    logger.info(f"✓ 更新 SSH 端口: {old_port} → {ssh_port}")
        
        # 5. 更新凭证ID(如果指定)
        if credential_id:
            cred_elements = root.findall(".//credentialsId")
            if cred_elements:
                for cred_elem in cred_elements:
                    old_cred = cred_elem.text or '(空)'
                    if old_cred != credential_id:
                        cred_elem.text = credential_id
                        updated = True
                        logger.info(f"✓ 更新 SSH 凭证ID: {old_cred} → {credential_id}")
            else:
                # 如果没有credentialsId元素，尝试在launcher下创建
                launcher_elem = root.find(".//launcher")
                if launcher_elem is not None:
                    cred_elem = ET.SubElement(launcher_elem, 'credentialsId')
                    cred_elem.text = credential_id
                    updated = True
                    logger.info(f"✓ 添加 SSH 凭证ID: {credential_id}")
        
        # 6. 更新 JNLP tunnel(对于 JNLP 连接节点)
        tunnel_elements = root.findall(".//tunnel")
        for tunnel_elem in tunnel_elements:
            if tunnel_elem.text and ":" in tunnel_elem.text:
                parts = tunnel_elem.text.split(":")
                if len(parts) == 2:
                    old_tunnel = tunnel_elem.text
                    port = parts[1]
                    tunnel_elem.text = f"{new_ip}:{port}"
                    updated = True
                    logger.info(f"✓ 更新 JNLP tunnel: {old_tunnel} → {new_ip}:{port}")
        
        # 如果没有找到任何需要更新的元素
        if not updated:
            logger.warning(f"未找到需要更新的 IP 配置元素")
            # 即使没有更新 Jenkins 配置（例如 Inbound 节点），也返回成功以便更新数据库
            return True, 'Jenkins配置未变更(该节点类型仅更新本地记录)', {
                'node_name': node_name,
                'old_ip': None,
                'new_ip': new_ip,
                'updated': False
            }
        
        # 6. 将更新后的配置转换回字符串
        updated_config = ET.tostring(root, encoding='unicode')
        
        # 7. 应用更新
        client.reconfig_node(node_name, updated_config)
        logger.info(f"✓ 成功应用节点配置更新")
        
        # 8. 验证更新 - 重新获取配置确认
        verify_config = client.get_node_config(node_name)
        verify_root = ET.fromstring(verify_config)
        verify_host = verify_root.find(".//host")
        
        if verify_host is not None and verify_host.text == new_ip:
            logger.info(f"✓ 验证通过: 节点 IP 已更新为 {new_ip}")
        else:
            logger.warning(f"⚠ 验证失败: 节点 IP 可能未正确更新")
        
        logger.info(f"✓ 节点 [{node_name}] IP 地址更新完成!")
        
        return True, '成功更新节点IP地址', {
            'node_name': node_name,
            'old_ip': old_ip,
            'new_ip': new_ip,
            'updated': True
        }
        
    except ET.ParseError as e:
        error_msg = f'解析 XML 配置失败: {str(e)}'
        logger.error(error_msg)
        return False, error_msg, None
    except jenkins.JenkinsException as e:
        error_msg = f'Jenkins API 错误: {str(e)}'
        logger.error(error_msg)
        return False, error_msg, None
    except Exception as e:
        error_msg = f'更新节点IP失败: {str(e)}'
        logger.error(error_msg)
        return False, error_msg, None


# ==================== Node CRUD 操作 (参考 jenkins_node_crud.py) ====================

def create_ssh_node(name, host, credential_id='', port=22, remote_fs='/home/jenkins', 
                    labels='', num_executors=2, description=''):
    """
    创建 SSH 连接节点
    
    参考: add_jenkins_node.py 的标准实现方式
    使用 python-jenkins 的 launcher 和 launcher_params 参数
    
    Args:
        name: 节点名称
        host: 主机 IP 或域名
        credential_id: SSH 凭证 ID
        port: SSH 端口 (默认 22)
        remote_fs: 远程工作目录 (默认 /home/jenkins)
        labels: 节点标签 (空格分隔)
        num_executors: 执行器数量 (默认 2)
        description: 节点描述
        
    Returns:
        tuple: (是否成功, 消息, 数据)
        数据格式: {
            'node_name': str,
            'host': str,
            'port': int,
            'labels': str,
            'num_executors': int
        }
    """
    try:
        client = get_jenkins_client()
        
        # 检查节点是否已存在
        if client.node_exists(name):
            error_msg = f'节点 [{name}] 已存在,无法创建'
            logger.warning(error_msg)
            return False, error_msg, None
        
        logger.info(f"开始创建 SSH 节点: {name}")
        
        # 构建 SSH launcher 参数（参考 add_jenkins_node.py）
        launcher_params = {
            'host': host,
            'port': str(port),  # 必须是字符串类型
        }
        
        # 添加凭证 ID（如果提供）
        if credential_id:
            launcher_params['credentialsId'] = credential_id
        
        # 使用 python-jenkins 标准方式创建节点
        client.create_node(
            name=name,
            numExecutors=num_executors,
            nodeDescription=description or f'Jenkins Node: {name}',
            remoteFS=remote_fs,
            labels=labels,
            exclusive=False,
            launcher=jenkins.LAUNCHER_SSH,      # 指定 SSH launcher
            launcher_params=launcher_params      # 传递 SSH 参数
        )
        
        logger.info(f"✓ 成功创建节点 [{name}]")
        logger.info(f"  - 主机: {host}:{port}")
        logger.info(f"  - 标签: {labels}")
        logger.info(f"  - 执行器: {num_executors}")
        logger.info(f"  - 凭证ID: {credential_id or '(未指定)'}")
        
        return True, f'成功创建节点 [{name}]', {
            'node_name': name,
            'host': host,
            'port': port,
            'labels': labels,
            'num_executors': num_executors,
            'remote_fs': remote_fs,
            'credential_id': credential_id
        }
        
    except jenkins.JenkinsException as e:
        error_msg = f'Jenkins API 错误: {str(e)}'
        logger.error(error_msg)
        return False, error_msg, None
    except Exception as e:
        error_msg = f'创建节点失败: {str(e)}'
        logger.error(error_msg)
        return False, error_msg, None


def delete_node(node_name):
    """
    删除指定节点
    
    参考: jenkins_node_crud.py 的 delete_node 方法
    
    Args:
        node_name: 节点名称
        
    Returns:
        tuple: (是否成功, 消息, 数据)
        数据格式: {
            'node_name': str,
            'deleted': bool
        }
    """
    try:
        client = get_jenkins_client()
        
        # 检查节点是否存在
        if not client.node_exists(node_name):
            error_msg = f'节点 [{node_name}] 不存在,无法删除'
            logger.warning(error_msg)
            return False, error_msg, None
        
        logger.info(f"开始删除节点: {node_name}")
        
        # 删除节点
        client.delete_node(node_name)
        
        logger.info(f"✓ 成功删除节点 [{node_name}]")
        
        return True, f'成功删除节点 [{node_name}]', {
            'node_name': node_name,
            'deleted': True
        }
        
    except Exception as e:
        error_msg = f'删除节点失败: {str(e)}'
        logger.error(error_msg)
        return False, error_msg, None


def enable_node(node_name):
    """
    启用节点
    
    参考: jenkins_node_crud.py 的 enable_node 方法
    
    Args:
        node_name: 节点名称
        
    Returns:
        tuple: (是否成功, 消息, 数据)
    """
    try:
        client = get_jenkins_client()
        
        if not client.node_exists(node_name):
            error_msg = f'节点 [{node_name}] 不存在'
            logger.warning(error_msg)
            return False, error_msg, None
        
        logger.info(f"启用节点: {node_name}")
        client.enable_node(node_name)
        
        logger.info(f"✓ 成功启用节点 [{node_name}]")
        
        return True, f'成功启用节点 [{node_name}]', {
            'node_name': node_name,
            'enabled': True
        }
        
    except Exception as e:
        error_msg = f'启用节点失败: {str(e)}'
        logger.error(error_msg)
        return False, error_msg, None


def disable_node(node_name, message=''):
    """
    禁用节点
    
    参考: jenkins_node_crud.py 的 disable_node 方法
    
    Args:
        node_name: 节点名称
        message: 禁用原因 (可选)
        
    Returns:
        tuple: (是否成功, 消息, 数据)
    """
    try:
        client = get_jenkins_client()
        
        if not client.node_exists(node_name):
            error_msg = f'节点 [{node_name}] 不存在'
            logger.warning(error_msg)
            return False, error_msg, None
        
        logger.info(f"禁用节点: {node_name}, 原因: {message}")
        client.disable_node(node_name, message)
        
        logger.info(f"✓ 成功禁用节点 [{node_name}]")
        
        return True, f'成功禁用节点 [{node_name}]', {
            'node_name': node_name,
            'disabled': True,
            'message': message
        }
        
    except Exception as e:
        error_msg = f'禁用节点失败: {str(e)}'
        logger.error(error_msg)
        return False, error_msg, None


def reconnect_node(node_name):
    """
    重新连接节点
    
    参考: jenkins_node_crud.py 的 reconnect_node 方法
    
    Args:
        node_name: 节点名称
        
    Returns:
        tuple: (是否成功, 消息, 数据)
    """
    try:
        import time
        
        client = get_jenkins_client()
        
        if not client.node_exists(node_name):
            error_msg = f'节点 [{node_name}] 不存在'
            logger.warning(error_msg)
            return False, error_msg, None
        
        logger.info(f"开始重新连接节点: {node_name}")
        
        # 先禁用
        client.disable_node(node_name)
        time.sleep(2)
        
        # 再启用
        client.enable_node(node_name)
        time.sleep(3)
        
        # 检查状态
        node_info = client.get_node_info(node_name)
        is_online = not node_info.get('offline', True)
        
        if is_online:
            logger.info(f"✓ 节点 [{node_name}] 已上线")
            return True, f'节点 [{node_name}] 重新连接成功', {
                'node_name': node_name,
                'is_online': True,
                'reconnected': True
            }
        else:
            logger.warning(f"⚠ 节点 [{node_name}] 仍然离线")
            return True, f'节点 [{node_name}] 重新连接已触发,但仍处于离线状态', {
                'node_name': node_name,
                'is_online': False,
                'reconnected': False,
                'offline_cause': node_info.get('offlineCauseReason', '')
            }
        
    except Exception as e:
        error_msg = f'重新连接节点失败: {str(e)}'
        logger.error(error_msg)
        return False, error_msg, None


def get_node_info(node_name):
    """
    获取节点详细信息
    
    参考: jenkins_node_crud.py 的 get_node_info 方法
    
    Args:
        node_name: 节点名称
        
    Returns:
        tuple: (是否成功, 消息, 节点信息)
    """
    try:
        client = get_jenkins_client()
        
        if not client.node_exists(node_name):
            error_msg = f'节点 [{node_name}] 不存在'
            logger.warning(error_msg)
            return False, error_msg, None
        
        logger.info(f"获取节点详细信息: {node_name}")
        
        # 获取节点详细信息
        node_info = client.get_node_info(node_name, depth=1)
        
        # 提取关键信息
        result = {
            'name': node_name,
            'displayName': node_info.get('displayName', node_name),
            'description': node_info.get('description', ''),
            'numExecutors': node_info.get('numExecutors', 1),
            'labels': ','.join([label.get('name', '') for label in node_info.get('assignedLabels', [])]),
            'offline': node_info.get('offline', False),
            'temporarilyOffline': node_info.get('temporarilyOffline', False),
            'idle': node_info.get('idle', True),
            'offlineCauseReason': node_info.get('offlineCauseReason', '') if node_info.get('offline') else '',
            'monitorData': node_info.get('monitorData', {})
        }
        
        logger.info(f"✓ 成功获取节点 [{node_name}] 详细信息")
        
        return True, f'成功获取节点 [{node_name}] 信息', result
        
    except Exception as e:
        error_msg = f'获取节点信息失败: {str(e)}'
        logger.error(error_msg)
        return False, error_msg, None


def update_node_labels(node_name, labels):
    """
    更新节点标签
    
    参考: jenkins_node_crud.py 的 update_node_labels 方法
    
    Args:
        node_name: 节点名称
        labels: 新的标签 (空格分隔字符串)
        
    Returns:
        tuple: (是否成功, 消息, 数据)
    """
    try:
        import xml.etree.ElementTree as ET
        
        client = get_jenkins_client()
        
        if not client.node_exists(node_name):
            error_msg = f'节点 [{node_name}] 不存在'
            logger.warning(error_msg)
            return False, error_msg, None
        
        logger.info(f"更新节点 [{node_name}] 标签: {labels}")
        
        # 获取当前配置
        config_xml = client.get_node_config(node_name)
        root = ET.fromstring(config_xml)
        
        # 更新标签
        label_elem = root.find('.//label')
        old_labels = ''
        
        if label_elem is not None:
            old_labels = label_elem.text or ''
            label_elem.text = labels
        else:
            # 如果不存在标签元素,创建一个
            label_elem = ET.SubElement(root, 'label')
            label_elem.text = labels
        
        # 应用更新
        updated_config = ET.tostring(root, encoding='unicode')
        client.reconfig_node(node_name, updated_config)
        
        logger.info(f"✓ 成功更新节点 [{node_name}] 标签: {old_labels} → {labels}")
        
        return True, f'成功更新节点 [{node_name}] 标签', {
            'node_name': node_name,
            'old_labels': old_labels,
            'new_labels': labels,
            'updated': True
        }
        
    except Exception as e:
        error_msg = f'更新节点标签失败: {str(e)}'
        logger.error(error_msg)
        return False, error_msg, None


def node_exists(node_name):
    """
    检查节点是否存在
    
    Args:
        node_name: 节点名称
        
    Returns:
        tuple: (是否成功, 消息, 数据)
    """
    try:
        client = get_jenkins_client()
        exists = client.node_exists(node_name)
        
        return True, '节点存在性检查完成', {
            'node_name': node_name,
            'exists': exists
        }
        
    except Exception as e:
        error_msg = f'检查节点是否存在失败: {str(e)}'
        logger.error(error_msg)
        return False, error_msg, None


def get_credentials_list():
    """
    获取 Jenkins 凭证列表
    
    参考 list_credentials.py 实现
    
    Returns:
        tuple: (是否成功, 消息, 凭证列表)
        凭证列表格式: [
            {
                'id': str,              # 凭证ID
                'description': str,     # 描述
                'displayName': str,     # 显示名称
                'typeName': str,        # 类型名称
                'className': str,       # 类名
                'scope': str           # 作用域
            }
        ]
    """
    try:
        import requests
        
        client = get_jenkins_client()
        
        # 获取 Jenkins 服务器配置
        from .models import JenkinsServer
        try:
            server = JenkinsServer.objects.first()
            if not server:
                return False, 'Jenkins服务器未配置', None
            
            jenkins_url = server.url.rstrip('/')
            username = server.username
            token = server.token  # 使用 token 而不是 password
        except Exception as e:
            return False, f'获取Jenkins服务器配置失败: {str(e)}', None
        
        # 尝试多个API端点
        endpoints = [
            "/credentials/store/system/domain/_/api/json?depth=2",
            "/credentials/store/system/domain/_/api/json",
            "/credentials/api/json",
        ]
        
        auth = (username, token)  # 使用 token 进行认证
        data = None
        
        for endpoint in endpoints:
            url = jenkins_url + endpoint
            try:
                response = requests.get(url, auth=auth, timeout=10)
                if response.status_code == 200:
                    resp_data = response.json()
                    if 'credentials' in resp_data:
                        data = resp_data
                        logger.info(f"成功通过端点获取凭证: {endpoint}")
                        break
            except Exception as e:
                logger.debug(f"尝试端点失败 {endpoint}: {str(e)}")
                continue
        
        if not data or 'credentials' not in data:
            return False, '无法获取凭证信息，请检查Jenkins配置和权限', None
        
        # 解析凭证数据
        credentials = data['credentials']
        parsed_list = []
        
        for cred in credentials:
            # 提取凭证信息
            cred_info = {
                'id': cred.get('id') or cred.get('credentialId') or 'Unknown',
                'description': cred.get('description', ''),
                'displayName': cred.get('displayName', ''),
                'typeName': cred.get('typeName', ''),
                'className': cred.get('_class', ''),
                'scope': cred.get('scope', ''),
            }
            
            # 如果没有 typeName，从 className 推断
            if not cred_info['typeName'] and cred_info['className']:
                class_name = cred_info['className']
                if 'SSH' in class_name or 'ssh' in class_name:
                    cred_info['typeName'] = 'SSH Username with private key'
                elif 'UsernamePassword' in class_name:
                    cred_info['typeName'] = 'Username with password'
                elif 'Secret' in class_name:
                    cred_info['typeName'] = 'Secret text'
                elif 'Certificate' in class_name:
                    cred_info['typeName'] = 'Certificate'
                else:
                    parts = class_name.split('.')
                    cred_info['typeName'] = parts[-1] if parts else 'Unknown'
            
            parsed_list.append(cred_info)
        
        logger.info(f"成功获取 {len(parsed_list)} 个凭证")
        
        return True, f'成功获取 {len(parsed_list)} 个凭证', parsed_list
        
    except Exception as e:
        error_msg = f'获取凭证列表失败: {str(e)}'
        logger.error(error_msg)
        return False, error_msg, None
