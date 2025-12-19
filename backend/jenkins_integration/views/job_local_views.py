from rest_framework import viewsets, mixins
from rest_framework.views import APIView
from ..utils import R, ResponseCode, ResponseMessage
from ..models import JenkinsJob
from ..serializers import JenkinsJobSerializer
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
    queryset = JenkinsJob.objects.all().order_by('-last_sync_time')
    serializer_class = JenkinsJobSerializer
    filterset_fields = ['server', 'project', 'plan', 'environment', 'is_active']

    def list(self, request, *args, **kwargs):
        # 支持按 Job Name 模糊搜索
        name = request.query_params.get('name')
        if name:
            self.queryset = self.queryset.filter(name__icontains=name)
            
        page = self.paginate_queryset(self.queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(self.queryset, many=True)
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
    触发异步任务，从 Jenkins 服务器拉取数据并更新本地 DB
    """
    
    def post(self, request):
        try:
            # 调用 Celery 异步任务
            from ..tasks import sync_jenkins_jobs_task
            task = sync_jenkins_jobs_task.delay()
            
            return R.success(
                message="Jenkins Jobs 同步任务已在后台启动",
                data={'task_id': task.id}
            )
                
        except Exception as e:
            logger.error(f"同步 Jobs 视图异常: {str(e)}")
            return R.internal_error(str(e))
