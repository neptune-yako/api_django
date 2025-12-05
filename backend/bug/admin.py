from django.contrib import admin
from .models import Bug, Handle


@admin.register(Bug)
class ManageAdmin(admin.ModelAdmin):
    """后台bug列表设置"""
    # 需要展示的字段
    list_display = ['id', 'interface', 'level', 'describe', 'status', 'username', 'create_time']
    # 分页：每页10条
    list_per_page = 10
    # 排序
    ordering = ('-id',)
    # 过滤器
    list_filter = ('interface',)


@admin.register(Handle)
class HandleAdmin(admin.ModelAdmin):
    """后台bug处理记录设置"""
    list_display = ['id', 'bug', 'handle', 'update_user', 'update_time']
    list_per_page = 10
    ordering = ('-id',)
    list_filter = ('bug',)
