from django.db import models


class Project(models.Model):
    """测试项目表"""
    name = models.CharField(max_length=20, verbose_name="项目名称")
    username = models.CharField(max_length=20, verbose_name="项目创建人", default='')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建日期")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新日期")
    # 默认的Manager
    objects = models.Manager()

    def __str__(self):
        return self.name

    class Meta:
        db_table = "project"
        verbose_name_plural = verbose_name = '项目列表'

    def info(self):
        """返回项目的统计信息"""
        from plan.models import Record
        return [
            {'name': '执行环境', 'value': self.environment.count()},
            {'name': '测试套件', 'value': self.scene.count()},
            {'name': '测试计划', 'value': self.plan.count()},
            {'name': '接口测试', 'value': self.interface.count()},
            {'name': '定时任务', 'value': 0},
            {'name': '执行记录', 'value': Record.objects.filter(plan__project=self).count()}
        ]

    def bug(self):
        """返回项目的bug统计信息"""
        return [
            {'name': '未处理bug', 'value': self.bug_set.filter(status='1').count()},
            {'name': '处理中bug', 'value': self.bug_set.filter(status='2').count()},
            {'name': '处理完bug', 'value': self.bug_set.filter(status='3').count()},
            {'name': '无效的bug', 'value': self.bug_set.filter(status='4').count()},
        ]


global_function = '''# 全局工具函数，可以在测试用例的前置、断言脚本中直接调用
import base64
import hashlib
import time
# 生成各种伪数据的库
from faker import Faker

# 实例化，中文
fk = Faker(locale='zh_CN')


def mobile():
    """随机生成手机号"""
    return fk.phone_number()


def name():
    """随机生成中文名字"""
    return fk.name()


def address():
    """随机生成一个地址"""
    return fk.address()


def city():
    """随机生成一个城市名"""
    return fk.city()


def company():
    """随机生成一个公司名"""
    return fk.company()


def postcode():
    """随机生成一个邮编"""
    return fk.postcode()


def email():
    """随机生成一个邮箱号"""
    return fk.email()


def date():
    """随机生成一个日期1987-08-31"""
    return fk.date()


def date_time():
    """随机生成一个时间1988-12-11 01:35:30"""
    return fk.date_time()


def ipv4():
    """随机生成一个ipv4的地址18.63.34.130"""
    return fk.ipv4()


def timestamp():
    """生成当前时间戳1714358666.4879088"""
    return time.time()


def md5_encode(args):
    """md5加密，以指定的编码格式编码字符串"""
    # 先把变量转成utf-8的编码格式
    args = str(args).encode('utf-8')
    # md5加密
    args_value = hashlib.md5(args).hexdigest()
    # 返回
    return args_value


def base64_encode(args):
    """base64编码"""
    # 先把变量转成utf-8的编码格式
    args = str(args).encode('utf-8')
    # base64加密
    base64_value = base64.b64encode(args).decode(encoding='utf-8')
    # 返回
    return base64_value


def base64_decode(args):
    """base64解密"""
    # 原文转为二进制
    args = str(args).encode("utf-8")
    # base64解密(二进制)
    decode_value = base64.b64decode(args)
    # 转成字符串
    encode_str = decode_value.decode("utf-8")
    return encode_str


def sha1_encode(params):
    """参数sha1加密"""
    enc_data = hashlib.sha1()
    enc_data.update(params.encode(encoding="utf-8"))
    return enc_data.hexdigest()


def sha256_encode(params):
    """参数sha256加密"""
    enc_data = hashlib.sha256()
    enc_data.update(params.encode(encoding="utf-8"))
    return enc_data.hexdigest()


def sha512_encode(params):
    """参数sha512加密"""
    enc_data = hashlib.sha512()
    enc_data.update(params.encode(encoding="utf-8"))
    return enc_data.hexdigest()
'''


class Environment(models.Model):
    """项目测试环境表"""
    # 外键关联项目，项目删除后删除测试环境
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name="所属项目", related_name='environment')
    global_variable = models.JSONField(verbose_name="全局变量", default=dict, null=True, blank=True)
    debug_global_variable = models.JSONField(verbose_name="调试全局变量", default=dict, null=True, blank=True)
    db = models.JSONField(verbose_name="数据库配置", default=list, null=True, blank=True)
    headers = models.JSONField(verbose_name="全局请求头", default=dict, null=True, blank=True)
    global_func = models.TextField(verbose_name="全局工具函数", default=global_function, null=True, blank=True)
    name = models.CharField(verbose_name="环境名称", max_length=50)
    host = models.CharField(verbose_name="host地址", max_length=50)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建日期")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新日期")
    username = models.CharField(max_length=20, verbose_name="环境创建人")
    objects = models.Manager()

    def __str__(self):
        return self.name

    class Meta:
        db_table = "environment"
        verbose_name_plural = verbose_name = '测试环境'


class File(models.Model):
    """测试文件表"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name='所属项目')
    file = models.FileField(verbose_name='上传文件')
    info = models.JSONField(verbose_name='文件类型', default=list)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建日期")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新日期")
    objects = models.Manager()

    def __str__(self):
        return self.file.name

    class Meta:
        db_table = "file"
        verbose_name_plural = verbose_name = '文件列表'
