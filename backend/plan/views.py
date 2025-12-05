from django.db import transaction
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from .filters import RecordFilter
from .models import Plan, Record, Report
from .serializer import PlanSerializer, PlanGetSerializer, RecordSerializer, ReportSerializer
from rest_framework import permissions, mixins, status
from .tasks import run_task
from backend.pagination import MyPaginator


@extend_schema(tags=["测试计划"])
class PlanView(ModelViewSet):
    """定义测试任务管理的视图类"""
    queryset = Plan.objects.all().order_by('-id')
    serializer_class = PlanSerializer
    permission_classes = [permissions.IsAuthenticated]
    # 设置查询过虑字段
    filterset_fields = ('project',)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PlanGetSerializer
        else:
            return self.serializer_class

    @extend_schema(summary="运行计划")
    def run_plan(self, request):
        """利用celery运行测试任务的方法"""
        # 获取参数并进行校验
        env_id = request.data.get('env')
        plan_id = request.data.get('plan')
        if not env_id:
            return Response({"detail": "测试环境不能为空！"}, status=status.HTTP_400_BAD_REQUEST)
        if not plan_id:
            return Response({"detail": "测试计划不能为空！"}, status=status.HTTP_400_BAD_REQUEST)
        # 使用celery异步执行测试任务中的用例
        transaction.on_commit(lambda: run_task.delay(env_id=env_id, task_id=plan_id, tester=request.user.username))
        return Response({"detail": "测试任务已经开始执行！"}, status=status.HTTP_200_OK)


@extend_schema(tags=["测试记录"])
class RecordView(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin, GenericViewSet):
    """测试记录的模型"""
    queryset = Record.objects.all().order_by('-id')
    serializer_class = RecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    # 由于Record中没有project字段，过虑器需要自定义一个过虑器类
    # filterset_fields = ('project', 'env', 'plan')
    filterset_class = RecordFilter
    # 设置分页数据
    pagination_class = MyPaginator


@extend_schema(tags=["测试报告"])
class ReportView(mixins.RetrieveModelMixin, mixins.DestroyModelMixin, GenericViewSet):
    """测试报告的模型"""
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(summary="报告列表")
    def retrieve(self, request, *args, **kwargs):
        record = Record.objects.get(id=kwargs['pk'])
        report = Report.objects.get(record=record)
        serializer = self.get_serializer(report)
        return Response(serializer.data)
