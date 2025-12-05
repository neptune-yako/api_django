from ApiEngine.basecase import run_test
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, status
from rest_framework.response import Response
from project.models import Environment
from .models import Interface, Case
from .serializer import InterfaceSerializer, CaseSerializer, CaseListSerializer, CaseGetSerializer, \
    InterfaceGetSerializer
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework import permissions
from backend.pagination import MyPaginator


@extend_schema(tags=["接口管理"])
class InterfaceView(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, mixins.ListModelMixin,
                    GenericViewSet):
    """接口管理的视图：增删改查操作"""
    queryset = Interface.objects.all().order_by('id')
    serializer_class = InterfaceSerializer
    permission_classes = [permissions.IsAuthenticated]
    # 设置查询过虑字段
    filterset_fields = ('project',)
    # 设置分页数据
    pagination_class = MyPaginator

    def get_serializer_class(self):
        """重写获取序列器的方法"""
        if self.action == "list":
            return InterfaceGetSerializer
        else:
            return self.serializer_class


@extend_schema(tags=["测试用例"])
class CaseView(ModelViewSet):
    """接口用例管理的视图"""
    queryset = Case.objects.all().order_by('id')
    serializer_class = CaseSerializer
    permission_classes = [permissions.IsAuthenticated]
    # 设置查询过虑字段
    filterset_fields = ('interface',)

    def get_serializer_class(self):
        """重写获取序列器的方法"""
        if self.action == 'list':
            return CaseListSerializer
        elif self.action == 'retrieve':
            return CaseGetSerializer
        else:
            return self.serializer_class

    @extend_schema(summary="运行用例")
    def run_case(self, request):
        """运行接口用例的方法"""
        # 获取前端传过来的接口参数
        env_id = request.data.get('env')
        cases = request.data.get('cases')
        if not env_id:
            return Response({'detail': "测试环境不能为空！"}, status=status.HTTP_400_BAD_REQUEST)
        if not cases:
            return Response({'detail': "测试用例不能为空！"}, status=status.HTTP_400_BAD_REQUEST)
        # 获取运行的测试环境数据，组装成测试执行引擎所需要的格式
        env = Environment.objects.get(id=env_id)
        env_config = {
            "ENV": {
                "host": env.host,
                "headers": env.headers,
                **env.global_variable,
                **env.debug_global_variable,
            },
            "DB": env.db,
            "global_func": env.global_func
        }
        # 获取用例数据，组装成测试执行引擎所需要的格式
        cases_datas = [
            {
                'name': "调试运行",
                'Cases': [cases]
            }
        ]
        # 调用测试执行引擎的run_test方法，运行测试用例，得到测试结果
        result, ENV = run_test(case_data=cases_datas, env_config=env_config, debug=True)
        # 将运行的环境变量保存到测试环境的debug_global_variable中
        env.debug_global_variable = ENV
        env.save()
        # 返回结果
        return Response(result['results'][0]['cases'][0])
