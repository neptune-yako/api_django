from django.contrib import admin
from .models import Cronjob


@admin.register(Cronjob)
class CronjobAdmin(admin.ModelAdmin):
    """后台定时任务列表设置"""
    list_display = ['id', 'name', 'plan', 'env', 'rule', 'status', 'username', 'create_time', 'update_time']
    list_per_page = 10
    ordering = ('-id',)
    list_filter = ('name',)
    list_display_links = ('name',)
