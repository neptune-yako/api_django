from django.db import models
from project.models import Project, Environment
from scene.models import Scene


class Plan(models.Model):
    """测试任务的模型类"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name="所属项目", related_name='plan')
    name = models.CharField(max_length=20, verbose_name='任务名称')
    scene = models.ManyToManyField(Scene, verbose_name='包含的测试套件', default=list)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建日期")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新日期")
    username = models.CharField(max_length=20, verbose_name="计划创建人")
    objects = models.Manager()

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'plan'
        verbose_name_plural = verbose_name = '测试计划'


class Record(models.Model):
    """测试运行记录"""
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, verbose_name="测试计划")
    env = models.ForeignKey(Environment, on_delete=models.CASCADE, verbose_name="测试环境")
    all = models.IntegerField(verbose_name="总用例数", default=0, blank=True)
    success = models.IntegerField(verbose_name="通过用例数", default=0, blank=True)
    fail = models.IntegerField(verbose_name="失败用例数", default=0, blank=True)
    error = models.IntegerField(verbose_name="错误用例数", default=0, blank=True)
    pass_rate = models.CharField(max_length=20, verbose_name="通过率（%）", default='0', blank=True)
    tester = models.CharField(max_length=20, verbose_name="执行者", blank=True)
    status = models.CharField(max_length=10, verbose_name="执行状态")
    create_time = models.DateTimeField(auto_created=True, verbose_name="执行时间", auto_now_add=True)
    objects = models.Manager()

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'record'
        verbose_name_plural = verbose_name = '运行记录'


class Report(models.Model):
    """测试报告"""
    info = models.JSONField(verbose_name="报告数据", blank=True, default=dict)
    record = models.ForeignKey(Record, on_delete=models.CASCADE, verbose_name="运行记录id")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建日期")
    objects = models.Manager()

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'report'
        verbose_name_plural = verbose_name = '测试报告'
