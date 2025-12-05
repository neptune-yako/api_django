from django.apps import AppConfig


class CronjobConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "cronjob"
    verbose_name = '定时任务'
