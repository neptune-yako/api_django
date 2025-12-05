import re
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError


class Role(models.Model):
    """角色表"""
    name = models.CharField(verbose_name='角色名称', max_length=20, unique=True)
    description = models.CharField(verbose_name='角色描述', max_length=255, blank=True)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    objects = models.Manager()

    class Meta:
        db_table = "role"
        verbose_name_plural = verbose_name = "角色列表"

    def __str__(self):
        return self.name


def validate_mobile(value):
    if not re.match(r'1[3-9]\d{9}', value):
        raise ValidationError('手机号码格式不正确！')


class User(AbstractUser):
    # 新增mobile和nickname字段
    mobile = models.CharField(verbose_name='手机号', max_length=11, null=True, blank=True, unique=True,
                              error_messages={'unique': '该手机号码已经被注册！'}, validators=[validate_mobile])
    nickname = models.CharField(verbose_name="用户昵称", null=True, blank=True, max_length=20, default="")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新日期")
    roles = models.ManyToManyField(Role, verbose_name="用户角色", related_name='user', blank=True)
    objects = models.Manager()

    # 通过createsuperuser管理命令创建用户时将输入邮箱email字段改成mobile字段
    REQUIRED_FIELDS = ['mobile']

    # 用户表
    class Meta:
        db_table = "user"
        verbose_name_plural = verbose_name = "用户列表"
