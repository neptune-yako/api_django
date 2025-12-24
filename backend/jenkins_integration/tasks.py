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
