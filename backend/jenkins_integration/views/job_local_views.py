from rest_framework import viewsets, mixins
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from ..utils import R, ResponseCode, ResponseMessage
from ..models import JenkinsJob
from ..serializers import JenkinsJobSerializer
from backend.pagination import MyPaginator
import logging

logger = logging.getLogger(__name__)
# 本地 Job 管理
class JenkinsJobViewSet(mixins.RetrieveModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.ListModelMixin,
                        viewsets.GenericViewSet):
    """
    Jenkins Job 本地数据管理视图集
    用途：更新 Job 的关联关系 (Plan, Project, Environment)
    注意：不涉及 Jenkins 用于的远程配置修改
    """
    queryset = JenkinsJob.objects.all().select_related(
        'server', 'project', 'plan'
    ).prefetch_related(
        'environments', 'nodes'
    ).order_by('-last_sync_time')
    serializer_class = JenkinsJobSerializer
    pagination_class = MyPaginator
    filter_backends = [DjangoFilterBackend]
    # 移除 environment,因为ManyToMany字段需要特殊处理
    filterset_fields = ['server', 'project', 'plan', 'is_active']

    def list(self, request, *args, **kwargs):
        """
        列表查询，支持：
        - 按 name 模糊搜索
        - 按 server/project/plan/is_active 精确筛选（filterset_fields）
        - 按 environment 精确筛选（多对多关系）
        """
        # 获取基础 queryset
        queryset = self.filter_queryset(self.get_queryset())
        
        # 额外支持按 Job Name 模糊搜索
        name = request.query_params.get('name')
        if name:
            queryset = queryset.filter(name__icontains=name)
        
        # 按环境ID过滤 (支持多对多)
        environment_id = request.query_params.get('environment')
        if environment_id:
            queryset = queryset.filter(environments__id=environment_id)
            
        # 分页
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        # 无分页
        serializer = self.get_serializer(queryset, many=True)
        return R.success(data=serializer.data)

    def update(self, request, *args, **kwargs):
        """更新本地关联信息 (Plan/Project/Env)"""
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return R.success(message="关联信息已更新", data=serializer.data)
        except Exception as e:
            return R.error(message=str(e))

class SyncJenkinsJobsView(APIView):
    """
    同步 Jenkins Jobs 视图
    触发异步任务,从指定 Jenkins 服务器拉取数据并更新本地 DB
    """
    
    def post(self, request):
        try:
            # 获取请求参数
            server_id = request.data.get('server_id')
            
            # 参数校验
            if not server_id:
                return R.bad_request(message="请选择要同步的 Jenkins 服务器")
            
            # 验证服务器存在性
            from ..models import JenkinsServer
            try:
                server = JenkinsServer.objects.get(id=server_id)
            except JenkinsServer.DoesNotExist:
                return R.error(message=f"服务器 ID [{server_id}] 不存在", code=ResponseCode.NOT_FOUND)
            
            # 验证连接状态
            if server.connection_status != 'connected':
                return R.error(
                    message=f"服务器 [{server.name}] 连接状态为 {server.connection_status},请先在服务器管理页面测试连接",
                    code=ResponseCode.BAD_REQUEST
                )
            
            # 调用 Celery 异步任务
            from ..tasks import sync_jenkins_jobs_task
            task = sync_jenkins_jobs_task.delay(server_id=server_id)
            
            return R.success(
                message=f"Jenkins Jobs 同步任务已启动 (服务器: {server.name})",
                data={'task_id': task.id, 'server_name': server.name}
            )
                
        except Exception as e:
            logger.error(f"同步 Jobs 视图异常: {str(e)}")
            return R.internal_error(str(e))


class CleanupJenkinsJobsView(APIView):
    """
    清理失效的 Jenkins Jobs 视图
    触发异步任务,删除本地存在但 Jenkins 服务器上已不存在的 Jobs
    """
    
    def post(self, request):
        try:
            # 获取请求参数
            server_id = request.data.get('server_id')
            
            # 参数校验
            if not server_id:
                return R.bad_request(message="请选择要清理的 Jenkins 服务器")
            
            # 验证服务器存在性
            from ..models import JenkinsServer
            try:
                server = JenkinsServer.objects.get(id=server_id)
            except JenkinsServer.DoesNotExist:
                return R.error(message=f"服务器 ID [{server_id}] 不存在", code=ResponseCode.NOT_FOUND)
            
            # 验证连接状态
            if server.connection_status != 'connected':
                return R.error(
                    message=f"服务器 [{server.name}] 连接状态为 {server.connection_status},无法清理",
                    code=ResponseCode.BAD_REQUEST
                )
            
            # 调用 Celery 异步任务
            from ..tasks import cleanup_jenkins_jobs_task
            task = cleanup_jenkins_jobs_task.delay(server_id=server_id)
            
            return R.success(
                message=f"Jenkins Jobs 清理任务已启动 (服务器: {server.name})",
                data={'task_id': task.id, 'server_name': server.name}
            )
                
        except Exception as e:
            logger.error(f"清理 Jobs 视图异常: {str(e)}")
            return R.internal_error(str(e))
