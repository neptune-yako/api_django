"""
Jenkins 数据同步服务
"""
import logging
from django.db import transaction
from ..models import JenkinsJob, JenkinsServer
from ..jenkins_client import get_all_jobs, get_job_detail, get_all_nodes

logger = logging.getLogger('django')

class JenkinsSyncService:
    """Jenkins 数据同步服务"""

    @staticmethod
    def sync_jobs(server_id=None):
        """
        同步 Jenkins Jobs 到数据库 (包含详情)
        
        Args:
            server_id: Jenkins 服务器 ID (可选,默认使用第一个服务器)
            
        Returns:
            tuple: (是否成功, 消息, 同步数量)
        """
        try:
            # 1. 获取指定的 Jenkins Server
            if server_id:
                try:
                    server = JenkinsServer.objects.get(id=server_id)
                except JenkinsServer.DoesNotExist:
                    return False, f"服务器 ID [{server_id}] 不存在", 0
            else:
                server = JenkinsServer.objects.first()
                if not server:
                    return False, "请先配置 Jenkins 服务器", 0
            
            # 2. 校验连接状态
            if server.connection_status != 'connected':
                return False, f"服务器 [{server.name}] 连接状态为 {server.connection_status},请先测试连接", 0
            
            # 3. 从指定服务器获取所有 Jobs 列表
            from ..jenkins_client import get_all_jobs_by_server, get_job_detail_by_server
            success, msg, jobs_data = get_all_jobs_by_server(server)
            if not success:
                return False, msg, 0

            sync_count = 0
            
            # 4. 遍历列表，逐个同步详情
            for job_item in jobs_data:
                job_name = job_item.get('name')
                
                if not job_name:
                    continue
                    
                # 4.1 获取 Job 详情 (使用指定服务器)
                detail_success, _, detail_data = get_job_detail_by_server(server, job_name)
                
                defaults = {}
                if detail_success and detail_data:
                    defaults['description'] = detail_data.get('description')
                    defaults['config_xml'] = detail_data.get('config_xml')
                    defaults['is_buildable'] = detail_data.get('is_buildable')
                    defaults['last_build_number'] = detail_data.get('last_build_number')
                    defaults['last_build_status'] = detail_data.get('last_build_status')
                
                # 4.2 存入数据库
                with transaction.atomic():
                    JenkinsJob.objects.update_or_create(
                        name=job_name,
                        server=server,
                        defaults=defaults
                    )
                sync_count += 1
            
            logger.info(f"从服务器 [{server.name}] 同步完成，共同步 {sync_count} 个任务")
            return True, f"成功从 [{server.name}] 同步 {sync_count} 个任务", sync_count

        except Exception as e:
            error_msg = f"同步 Jobs 数据库异常: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, 0


    @staticmethod
    def sync_nodes(project_id, username='jenkins_sync'):
        """
        同步 Jenkins 节点到项目环境

        Args:
            project_id: 项目 ID
            username: 环境创建人用户名 (默认 'jenkins_sync')

        Returns:
            tuple: (是否成功, 消息, 统计数据)
            统计数据格式: {
                'total': int,          # 总节点数
                'created': int,        # 新建环境数
                'updated': int,        # 更新环境数
                'skipped': int,        # 跳过数(无IP地址的节点)
                'nodes': list          # 同步的节点列表
            }
        """
        from project.models import Environment, Project

        # 1. 验证项目存在性
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return False, f"项目 [{project_id}] 不存在", None

        # 2. 从 Jenkins 获取所有节点
        success, msg, nodes_data = get_all_nodes()
        if not success:
            return False, f"获取 Jenkins 节点失败: {msg}", None

        # 3. 统计数据
        stats = {
            'total': len(nodes_data),
            'created': 0,
            'updated': 0,
            'skipped': 0,
            'nodes': []
        }

        # 4. 遍历节点，创建/更新 Environment
        for node_data in nodes_data:
            node_name = node_data.get('name')
            ip_address = node_data.get('ip_address', '')

            # 跳过没有 IP 地址的节点
            if not ip_address:
                logger.warning(f"节点 [{node_name}] 无 IP 地址，跳过同步")
                stats['skipped'] += 1
                continue

            # 确定环境名称：优先使用 display_name，否则使用 name
            env_name = node_data.get('displayName') or node_name

            # 准备环境数据
            env_defaults = {
                'host': ip_address,
                'source': 'jenkins',
                'username': username,
                'global_variable': {},
                'debug_global_variable': {},
                'db': [],
                'headers': {},
            }

            try:
                # 使用 update_or_create: 如果存在则更新，不存在则创建
                with transaction.atomic():
                    env, created = Environment.objects.update_or_create(
                        project=project,
                        name=env_name,
                        defaults=env_defaults
                    )

                    if created:
                        stats['created'] += 1
                        logger.info(f"创建新环境: {env_name} @ {ip_address}")
                    else:
                        stats['updated'] += 1
                        logger.info(f"更新环境: {env_name} @ {ip_address}")

                    stats['nodes'].append({
                        'name': env_name,
                        'ip': ip_address,
                        'action': 'created' if created else 'updated',
                        'is_online': not node_data.get('offline', True)
                    })

            except Exception as e:
                logger.error(f"同步节点 [{node_name}] 失败: {str(e)}")
                stats['skipped'] += 1
                continue

        logger.info(f"Jenkins 节点同步完成: 新建 {stats['created']}, 更新 {stats['updated']}, 跳过 {stats['skipped']}")

        return True, f"成功同步 {stats['created'] + stats['updated']} 个环境", stats
