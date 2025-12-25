# 创建一个celery的应用，并且加载settings中的celery配置项
import os
from celery import Celery
import logging

logger = logging.getLogger(__name__)

# 设置django默认环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# 创建一个app的celery应用
app = Celery('backend')

# 读取settings.py里的配置，使用CELERY_作为前缀标识
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动加载django每个应用下名称为tasks.py的文件，获取celery的注册任务
try:
    app.autodiscover_tasks()
    logger.info("Celery tasks autodiscovery completed successfully")
except Exception as e:
    logger.error(f"Celery autodiscover_tasks failed: {e}")
    raise


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """用于测试的调试任务"""
    print(f'Request: {self.request!r}')
