"""
Jenkins 数据同步服务
"""
import logging
from django.db import transaction
from ..models import JenkinsJob, JenkinsServer
from ..jenkins_client import get_all_jobs, get_job_detail

logger = logging.getLogger('django')

class JenkinsSyncService:
    """Jenkins 数据同步服务"""

    @staticmethod
    def sync_jobs():
        """
        同步所有 Jenkins Jobs 到数据库 (包含详情)
        """
        # 1. 从 Jenkins 获取所有 Jobs 列表
        success, msg, jobs_data = get_all_jobs()
        if not success:
            return False, msg, 0

        try:
            # 2. 获取默认的 Jenkins Server
            server = JenkinsServer.objects.first()
            if not server:
                return False, "请先配置 Jenkins 服务器", 0

            sync_count = 0
            
            # 3. 遍历列表，逐个同步详情
            for job_item in jobs_data:
                job_name = job_item.get('name')
                
                if not job_name:
                    continue
                    
                # 3.1 获取 Job 详情 (config.xml, description...)
                # 注意：这里会产生 HTTP 请求，如果是异步任务就没问题
                detail_success, _, detail_data = get_job_detail(job_name)
                
                defaults = {}
                if detail_success and detail_data:
                    defaults['description'] = detail_data.get('description')
                    defaults['config_xml'] = detail_data.get('config_xml')
                    defaults['is_buildable'] = detail_data.get('is_buildable')
                    defaults['last_build_number'] = detail_data.get('last_build_number')
                    defaults['last_build_status'] = detail_data.get('last_build_status')
                
                # 3.2 存入数据库
                with transaction.atomic():
                    JenkinsJob.objects.update_or_create(
                        name=job_name,
                        server=server,
                        defaults=defaults
                    )
                sync_count += 1
            
            logger.info(f"Jenkins Jobs 同步完成，共同步 {sync_count} 个任务")
            return True, f"成功同步 {sync_count} 个任务", sync_count
            
        except Exception as e:
            error_msg = f"同步 Jobs 数据库异常: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, 0
