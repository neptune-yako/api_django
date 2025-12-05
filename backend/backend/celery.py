# 创建一个celery的应用，并且加载settings中的celery配置项
import os
from celery import Celery

# 设置django默认环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
# 创建一个app的celery应用
app = Celery('backend')
# 读取settings.py里的配置，使用CELERY_作为前缀标识
app.config_from_object('django.conf:settings', namespace='CELERY')
# 自动加载django每个应用下名称为tasks.py的文件，获取celery的注册任务
app.autodiscover_tasks()
