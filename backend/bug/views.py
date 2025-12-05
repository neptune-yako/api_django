from drf_spectacular.utils import extend_schema
from rest_framework import permissions, mixins
from rest_framework.viewsets import GenericViewSet
from .models import Bug, Handle
from .serializer import BugSerializer, BugListSerializer
from backend.pagination import MyPaginator


@extend_schema(tags=["Bug管理"])
class BugView(mixins.CreateModelMixin, mixins.DestroyModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
              mixins.ListModelMixin, GenericViewSet):
    """bug管理的视图：增删改查操作"""
    queryset = Bug.objects.all().order_by('-id')
    serializer_class = BugSerializer
    # 设置仅限：登录的用户访问
    permission_classes = [permissions.IsAuthenticated]
    # 设置查询过虑字段
    filterset_fields = ('project',)
    # 设置分页数据
    pagination_class = MyPaginator

    def get_serializer_class(self):
        if self.action == 'list':
            return BugListSerializer
        else:
            return self.serializer_class

    def perform_create(self, serializer):
        # 关联当前用户
        bug = serializer.save(username=self.request.user.username)
        # 在创建一条bug操作记录
        status_value = '提交bug，状态为【{}】'.format(bug.status)
        Handle.objects.create(bug=bug, handle=status_value, update_user=self.request.user.username)

    def perform_update(self, serializer):
        # 创建一条bug操作记录
        bug = serializer.save()
        status_value = '提交bug，状态为【{}】'.format(bug.status)
        Handle.objects.create(bug=bug, handle=status_value, update_user=self.request.user.username)
