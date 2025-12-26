from django.db import transaction
from django.http import HttpResponse, FileResponse
from django.core.files.base import ContentFile
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from .filters import RecordFilter
from .models import Plan, Record, Report
from .serializer import PlanSerializer, PlanGetSerializer, RecordSerializer, ReportSerializer
from rest_framework import permissions, mixins, status
from .tasks import run_task
from .script_generator import extract_plan_data, generate_pytest_script
from backend.pagination import MyPaginator
import os


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

    @extend_schema(summary="导出测试脚本")
    @action(detail=True, methods=['post'])
    def export_script(self, request, pk=None):
        """导出测试计划为可执行的Python测试脚本"""
        # 获取参数并进行校验
        env_id = request.data.get('env')
        if not env_id:
            return Response({"detail": "测试环境不能为空！"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # 提取测试计划数据
            plan_data = extract_plan_data(pk, env_id)
            
            # 检查是否有测试套件
            if not plan_data['scenes']:
                return Response({"detail": "测试计划中没有测试套件，无法导出！"}, status=status.HTTP_400_BAD_REQUEST)
            
            # 生成pytest脚本
            script_content = generate_pytest_script(plan_data)
            
            # 返回文件下载
            response = HttpResponse(script_content, content_type='text/x-python')
            filename = f'test_plan_{plan_data["plan_name"]}.py'
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
            
        except Plan.DoesNotExist:
            return Response({"detail": "测试计划不存在！"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": f"导出脚本失败: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(summary="上传Python测试脚本")
    @action(detail=True, methods=['post'])
    def upload_script(self, request, pk=None):
        """上传Python测试脚本并绑定到测试计划"""
        # 获取上传的文件
        script_file = request.FILES.get('file')
        if not script_file:
            return Response({"detail": "请选择要上传的脚本文件！"}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # 验证文件扩展名
        if not script_file.name.endswith('.py'):
            return Response({"detail": "只支持上传.py格式的Python脚本文件！"}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        try:
            plan = self.get_object()
            
            # 如果已有绑定的脚本,先删除旧文件
            if plan.script_file:
                if os.path.exists(plan.script_file.path):
                    os.remove(plan.script_file.path)
            
            # 保存新文件
            plan.script_file = script_file
            plan.script_name = script_file.name
            plan.script_type = 'uploaded'
            plan.script_bind_time = timezone.now()
            plan.save()
            
            serializer = self.get_serializer(plan)
            return Response({
                "detail": "脚本上传并绑定成功！",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({"detail": f"上传脚本失败: {str(e)}"}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(summary="下载测试脚本")
    @action(detail=True, methods=['get'])
    def download_script(self, request, pk=None):
        """下载已绑定的测试脚本"""
        try:
            plan = self.get_object()
            
            if not plan.script_file:
                return Response({"detail": "该测试计划尚未绑定测试脚本！"}, 
                              status=status.HTTP_404_NOT_FOUND)
            
            # 返回文件
            response = FileResponse(plan.script_file.open('rb'), 
                                   content_type='text/x-python')
            response['Content-Disposition'] = f'attachment; filename="{plan.script_name}"'
            return response
            
        except Exception as e:
            return Response({"detail": f"下载脚本失败: {str(e)}"}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(summary="解绑测试脚本")
    @action(detail=True, methods=['post'])
    def unbind_script(self, request, pk=None):
        """解除测试计划与脚本的绑定"""
        delete_file = request.data.get('delete_file', False)  # 是否同时删除文件
        
        try:
            plan = self.get_object()
            
            if not plan.script_file:
                return Response({"detail": "该测试计划未绑定测试脚本！"}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            # 如果需要删除文件
            if delete_file and plan.script_file:
                if os.path.exists(plan.script_file.path):
                    os.remove(plan.script_file.path)
            
            # 清空脚本相关字段
            plan.script_file = None
            plan.script_name = None
            plan.script_type = None
            plan.script_bind_time = None
            plan.save()
            
            serializer = self.get_serializer(plan)
            return Response({
                "detail": "解绑成功！",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": f"解绑失败: {str(e)}"}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
