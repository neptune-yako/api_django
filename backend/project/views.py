import json
import os
import re

from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from .models import Project, Environment, File
from django.conf import settings
from .serializer import ProjectSerializer, EnvironmentSerializer, FileSerializer
from rest_framework import permissions, mixins, status
from backend.pagination import MyPaginator


@extend_schema(tags=["测试项目"])
class ProjectView(ModelViewSet):
    """测试项目视图集：增删改查操作"""
    queryset = Project.objects.all().order_by('-id')
    serializer_class = ProjectSerializer
    # 请求登录的权限校验
    permission_classes = [permissions.IsAuthenticated]
    # 设置分页数据
    pagination_class = MyPaginator


@extend_schema(tags=["测试环境"])
class EnvironmentView(ModelViewSet):
    """测试环境视图集：增删改查操作"""
    queryset = Environment.objects.all().order_by('-id')
    serializer_class = EnvironmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    # 设置过滤字段
    filterset_fields = ('project',)


@extend_schema(tags=["上传文件"])
class FileView(mixins.CreateModelMixin, mixins.DestroyModelMixin, mixins.ListModelMixin, GenericViewSet):
    """测试文件管理：增删查操作"""
    queryset = File.objects.all().order_by('-id')
    serializer_class = FileSerializer
    permission_classes = [permissions.IsAuthenticated]
    # 设置过滤字段
    filterset_fields = ('project',)

    @extend_schema(summary="上传文件")
    def create(self, request, *args, **kwargs):
        """重写文件上传的方法"""
        # 获取上传的文件大小和文件名
        size = request.data['file'].size
        name = request.data['file'].name
        # 文件名只能包含字母、数字、中文
        if not re.match(r'^[a-zA-Z0-9.\u4e00-\u9fa5]+$', name):
            return Response({"detail": "文件名只能包含字母、数字、中文！"}, status=status.HTTP_400_BAD_REQUEST)
        # 文本大小不能超过1024kb
        if size > 1024 * 1024:
            return Response({"detail": "文件大小不能超过1024kb！"}, status=status.HTTP_400_BAD_REQUEST)
        # 文件不能重复上传
        if name in os.listdir(settings.MEDIA_ROOT):
            return Response({"detail": "文件已存在，不能重复上传！"}, status=status.HTTP_400_BAD_REQUEST)
        # 安全性：检查文件类型，图片、pdf、word、excel、zip、文本
        content_types = ['image/jpeg', 'image/png', 'application/msword', 'application/pdf',
                         'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                         'application/vnd.ms-excel',
                         'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                         'application/zip', 'application/x-rar-compressed', 'text/plain']
        if request.data['file'].content_type not in content_types:
            return Response({"detail": "不支持当前的文件类型！"}, status=status.HTTP_400_BAD_REQUEST)
        # 修改info字段的值
        file_type = request.data['file'].content_type
        request.data['info'] = json.dumps([name, 'files/{}'.format(name), file_type])
        request.data['project'] = request.data.get('project_id')
        return super().create(request, *args, **kwargs)

    @extend_schema(summary="删除文件")
    def destroy(self, request, *args, **kwargs):
        """重写删除文件的方法"""
        file_path = self.get_object().info[1]
        # 调用父类的方法进行文件删除
        result = super().destroy(request, *args, **kwargs)
        # 删除服务器的文件
        os.remove(file_path)
        return result
