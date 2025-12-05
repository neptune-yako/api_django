from django.db import models
from interface.models import Interface
from project.models import Project


class Bug(models.Model):
    """bug管理列表"""
    CHOICES1 = [('1', '未处理bug'), ('2', '处理中bug'), ('3', '处理完bug'), ('4', '无效的bug')]
    CHOICES2 = [('1', '严重'), ('2', '一般'), ('3', '轻微')]
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name='所属项目', related_name='bug_set')
    interface = models.ForeignKey(Interface, on_delete=models.CASCADE, verbose_name="所属接口")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="提交时间")
    describe = models.CharField(max_length=255, verbose_name="bug描述", blank=True)
    info = models.JSONField(verbose_name="bug的用例详情", blank=True, default=dict)
    status = models.CharField(max_length=10, verbose_name="bug状态", choices=CHOICES1, default='1')
    level = models.CharField(max_length=10, verbose_name="bug等级", choices=CHOICES2, default='1')
    username = models.CharField(max_length=20, verbose_name="提交人", default='', blank=True)
    objects = models.Manager()

    def __str__(self):
        return str(self.interface)

    class Meta:
        # 数据库表名称
        db_table = 'bug'
        # 后台菜单列表名称
        verbose_name_plural = verbose_name = 'Bug列表'


class Handle(models.Model):
    """bug处理记录"""
    bug = models.ForeignKey(Bug, on_delete=models.CASCADE, verbose_name='bug的接口')
    update_time = models.DateTimeField(auto_now_add=True, verbose_name="操作时间")
    handle = models.CharField(max_length=20, verbose_name="操作内容", blank=True)
    update_user = models.CharField(max_length=20, verbose_name="操作人", blank=True)
    objects = models.Manager()

    class Meta:
        db_table = 'handle'
        verbose_name_plural = verbose_name = 'Bug记录'
