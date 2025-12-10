"""
Jenkins 客户端 - 启用 CSRF Crumb 支持
"""
import jenkins
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
        error_msg = f'获取Jobs失败: {str(e)}'
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
        
        if parameters:
            queue_id = client.build_job(job_name, parameters=parameters)
        else:
            queue_id = client.build_job(job_name)
        
        logger.info(f"成功触发 Job [{job_name}] 构建，队列ID: {queue_id}")
        
        return True, '成功触发构建', {'queue_id': queue_id}
        
    except Exception as e:
        error_msg = f'触发构建失败: {str(e)}'
        logger.error(error_msg)
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
