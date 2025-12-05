from django.db import models
from project.models import Project
from interface.models import Case


class Scene(models.Model):
    """测试套件的模型类定义"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name="所属项目", related_name='scene')
    name = models.CharField(max_length=20, verbose_name="套件名称")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建日期")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新日期")
    username = models.CharField(max_length=20, verbose_name="套件创建人")
    objects = models.Manager()

    def __str__(self):
        return self.name

    class Meta:
        db_table = "scene"
        verbose_name_plural = verbose_name = '测试套件'


class Step(models.Model):
    """用例步骤的模型类定义"""
    icase = models.ForeignKey(Case, on_delete=models.CASCADE, verbose_name='接口用例')
    scene = models.ForeignKey(Scene, on_delete=models.CASCADE, verbose_name='测试套件')
    sort = models.IntegerField(verbose_name='执行顺序', null=True, blank=True)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建日期")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新日期")
    objects = models.Manager()

    def __str__(self):
        return self.icase.title

    class Meta:
        db_table = "step"
        verbose_name_plural = verbose_name = '测试步骤'
