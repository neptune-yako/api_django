from django.contrib import admin
from .models import Project, Environment, File


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """后台项目列表设置"""
    list_display = ['id', 'name', 'username', 'create_time', 'update_time']
    list_per_page = 10
    ordering = ('-id',)
    list_filter = ('name',)
    list_display_links = ('name',)


@admin.register(Environment)
class EnvironmentAdmin(admin.ModelAdmin):
    """后台环境列表设置"""
    list_display = ['id', 'name', 'project', 'host', 'headers', 'db', 'debug_global_variable', 'global_variable',
                    'create_time', 'update_time']
    list_per_page = 10
    ordering = ('-id',)
    list_filter = ('name',)
    list_display_links = ('name',)


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    """后台文件上传列表设置"""
    list_display = ['id', 'project', 'file', 'info', 'create_time', 'update_time']
    list_per_page = 10
    ordering = ('-id',)
    list_filter = ('file',)
    list_display_links = ('file',)
