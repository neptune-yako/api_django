"""
Jenkins 集成模块 - Celery 异步任务
"""
from celery import shared_task
import logging

logger = logging.getLogger('django')

@shared_task
def sync_jenkins_jobs_task(server_id=None):
    """
    异步同步 Jenkins Jobs
    
    Args:
        server_id: Jenkins 服务器 ID (可选)
    """
    try:
        logger.info(f"开始执行 Jenkins Jobs 异步同步任务 (server_id={server_id})...")
        from .services.jenkins_sync import JenkinsSyncService
        
        success, msg, count = JenkinsSyncService.sync_jobs(server_id=server_id)
        
        if success:
            logger.info(f"Jenkins Jobs 异步同步成功: {msg}")
            return f"Synchronized {count} jobs"
        else:
            logger.error(f"Jenkins Jobs 异步同步失败: {msg}")
            return f"Failed: {msg}"
            
    except Exception as e:
        error_msg = f"Jenkins Jobs 异步同步任务异常: {str(e)}"
        logger.error(error_msg)
        return error_msg


@shared_task
def cleanup_jenkins_jobs_task(server_id):
    """
    异步清理失效的 Jenkins Jobs
    
    Args:
        server_id: Jenkins 服务器 ID (必填)
    """
    try:
        logger.info(f"开始执行 Jenkins Jobs 清理任务 (server_id={server_id})...")
        from .services.jenkins_sync import JenkinsSyncService
        
        success, msg, count = JenkinsSyncService.cleanup_jobs(server_id=server_id)
        
        if success:
            logger.info(f"Jenkins Jobs 清理成功: {msg}")
            return f"Cleaned {count} jobs"
        else:
            logger.error(f"Jenkins Jobs 清理失败: {msg}")
            return f"Failed: {msg}"
            
    except Exception as e:
        error_msg = f"Jenkins Jobs 清理任务异常: {str(e)}"
        logger.error(error_msg)
        return error_msg


@shared_task
def cleanup_jenkins_nodes_task(server_id=None):
    """
    异步清理失效的 Jenkins 节点
    
    Args:
        server_id: Jenkins 服务器 ID (可选，默认使用第一个活跃服务器)
    """
    try:
        logger.info(f"开始执行 Jenkins 节点清理任务 (server_id={server_id})...")
        from .services.jenkins_sync import JenkinsSyncService
        
        success, msg, stats = JenkinsSyncService.cleanup_nodes(server_id=server_id)
        
        if success:
            if stats:
                logger.info(
                    f"Jenkins 节点清理成功: 删除 {stats.get('nodes_deleted', 0)} 个节点, "
                    f"{stats.get('envs_deleted', 0)} 个环境"
                )
                return f"Cleaned {stats.get('nodes_deleted', 0)} nodes, {stats.get('envs_deleted', 0)} environments"
            else:
                logger.info(f"Jenkins 节点清理成功: {msg}")
                return msg
        else:
            logger.error(f"Jenkins 节点清理失败: {msg}")
            return f"Failed: {msg}"
            
    except Exception as e:
        error_msg = f"Jenkins 节点清理任务异常: {str(e)}"
        logger.error(error_msg)
        return error_msg
