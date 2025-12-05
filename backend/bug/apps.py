from django.apps import AppConfig


class BugConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "bug"
    # 设置菜单名称
    verbose_name = 'BUG管理'
