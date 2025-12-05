from drf_spectacular.utils import extend_schema

from ApiEngine.basecase import run_test
from rest_framework import mixins, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from project.models import Environment
from .models import Scene, Step
from .serializer import SceneSerializer, StepSerializer, StepListSerializer, SceneRunSerializer
from backend.pagination import MyPaginator


@extend_schema(tags=["测试套件"])
class SceneView(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, mixins.ListModelMixin,
                GenericViewSet):
    """测试套件的视图类：增删改查操作"""
    queryset = Scene.objects.all().order_by('-id')
    serializer_class = SceneSerializer
    # 设置过滤字段
    filterset_fields = ('project',)
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(summary="运行套件")
    def run_scene(self, request):
        """运行测试套件"""
        # 获取请求参数并进行校验
        env_id = request.data.get('env')
        scene_id = request.data.get('scene')
        if not env_id:
            return Response({"detail": "测试环境不能为空！"}, status=status.HTTP_400_BAD_REQUEST)
        if not scene_id:
            return Response({"detail": "测试套件不能为空！"}, status=status.HTTP_400_BAD_REQUEST)
        # 获取测试运行环境数据
        env = Environment.objects.get(id=env_id)
        env_config = {
            "ENV": {
                "host": env.host,
                "headers": env.headers,
                **env.global_variable,
            },
            "DB": env.db,
            "global_func": env.global_func
        }
        # 获取测试套件中的用例数据
        scene = Scene.objects.get(id=scene_id)
        cases = scene.step_set.all().order_by('sort')
        # 对查询集中的数据进行序列化
        res = SceneRunSerializer(cases, many=True).data
        # 组装成测试执行引擎所需要的数据格式
        cases_data = [
            {
                "name": scene.name,
                "Cases": [item['icase'] for item in res]
            }
        ]
        # 使用测试执行引擎运行测试
        result, ENV = run_test(cases_data, env_config, debug=True)
        # 保存一下调试变量
        env.debug_global_variable = ENV
        env.save()
        # 返回测试执行结果
        return Response(result['results'][0])


@extend_schema(tags=["测试步骤"])
class StepView(mixins.CreateModelMixin, mixins.DestroyModelMixin, mixins.ListModelMixin, GenericViewSet):
    """测试套件中的用例执行顺序的接口"""
    queryset = Step.objects.all().order_by('sort')
    serializer_class = StepSerializer
    permission_classes = [permissions.IsAuthenticated]
    # 设置过滤字段
    filterset_fields = ('scene',)
    # 设置分页数据
    pagination_class = MyPaginator

    def get_serializer_class(self):
        """实现访问不同的方法时使用不同的序列器"""
        if self.action == 'list':
            return StepListSerializer
        else:
            return self.serializer_class


@extend_schema(tags=["测试步骤"])
class StepOrder(APIView):
    """修改测试套件中的用例执行顺序"""
    # 请求登录的权限校验
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = StepSerializer

    @extend_schema(summary="拖拽步骤")
    def patch(self, request):
        datas = request.data
        for item in datas:
            # 通过id用例执行步骤对象修改执行的顺序sort
            obj = Step.objects.get(id=item['id'])
            obj.sort = item['sort']
            obj.save(update_fields=['sort'])
        return Response({'detail': "拖拽用例排序成功！", 'data': datas}, status=status.HTTP_200_OK)
