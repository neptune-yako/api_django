from django.db import models
from project.models import Project


# 接口管理
class Interface(models.Model):
    """接口管理"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name="所属项目", related_name='interface')
    name = models.CharField(max_length=20, verbose_name="接口名称")
    username = models.CharField(max_length=20, verbose_name="接口创建人")
    url = models.CharField(max_length=255, verbose_name="接口地址")
    method = models.CharField(max_length=50, verbose_name="请求方法")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建日期")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新日期")
    objects = models.Manager()

    def __str__(self):
        return self.url

    class Meta:
        db_table = 'interface'
        verbose_name_plural = verbose_name = "接口列表"


setup_script = """# 前置脚本(python)
# global_func：全局工具函数
# data：用例数据
# env：临时环境
# ENV：全局环境
# db：数据库操作对象
"""

teardown_script = """# 断言脚本(python)
# global_func：全局工具函数
# data：用例数据
# response：响应对象response
# env：临时环境
# ENV：全局环境
# db：数据库操作对象
"""


class Case(models.Model):
    """接口用例管理"""
    interface = models.ForeignKey(Interface, on_delete=models.CASCADE, verbose_name='接口地址')
    title = models.CharField(verbose_name='用例名称', max_length=20)
    headers = models.JSONField(verbose_name='请求头配置', null=True, default=dict, blank=True)
    request = models.JSONField(verbose_name='请求参数配置', null=True, default=dict, blank=True)
    file = models.JSONField(verbose_name='请求上传的文件参数', null=True, default=list, blank=True)
    setup_script = models.TextField(verbose_name='前置脚本', null=True, blank=True, default=setup_script)
    teardown_script = models.TextField(verbose_name='断言脚本', null=True, blank=True, default=teardown_script)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建日期")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新日期")
    username = models.CharField(max_length=20, verbose_name="用例创建人")
    objects = models.Manager()

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'case'
        verbose_name_plural = verbose_name = '用例列表'
