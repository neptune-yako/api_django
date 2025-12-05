from django.contrib import admin
from .models import Interface, Case


@admin.register(Interface)
class InterfaceAdmin(admin.ModelAdmin):
    """后台接口列表设置"""
    list_display = ['id', 'name', 'project', 'method', 'url', 'username', 'create_time', 'update_time']
    list_per_page = 10
    ordering = ('-id',)
    list_filter = ('name',)
    list_display_links = ('name',)


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    """后台用例列表设置"""
    list_display = ['id', 'title', 'interface', 'create_time', 'update_time']
    list_per_page = 10
    ordering = ('-id',)
    list_filter = ('title',)
    list_display_links = ('title',)
