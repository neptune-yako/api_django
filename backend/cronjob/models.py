from django.db import models
from project.models import Project, Environment
from plan.models import Plan


class Cronjob(models.Model):
    """定时任务表"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name="所属项目", related_name='cronjob')
    env = models.ForeignKey(Environment, on_delete=models.CASCADE, verbose_name="测试环境")
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, verbose_name="测试计划")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    username = models.CharField(max_length=20, verbose_name="任务创建人")
    name = models.CharField(max_length=20, verbose_name="任务名称")
    status = models.BooleanField(verbose_name="状态", default=False)
    rule = models.CharField(max_length=20, verbose_name="执行规则", default='*/1 * * * *')
    objects = models.Manager()

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'cronjob'
        verbose_name_plural = verbose_name = '任务列表'
