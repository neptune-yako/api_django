from django.contrib import admin
from .models import Scene, Step


@admin.register(Scene)
class SceneAdmin(admin.ModelAdmin):
    """后台测试套件列表设置"""
    list_display = ['id', 'name', 'project', 'create_time', 'update_time']
    list_per_page = 10
    ordering = ('-id',)
    list_display_links = ('name',)
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(Step)
class StepAdmin(admin.ModelAdmin):
    """后台用例步骤设置"""
    list_display = ['id', 'scene', 'icase', 'sort', 'create_time', 'update_time']
    list_per_page = 10
    ordering = ('-id',)
    list_display_links = ('scene',)
    list_filter = ('scene',)
    search_fields = ('scene',)
