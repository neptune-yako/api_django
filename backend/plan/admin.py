from django.contrib import admin
from .models import Plan, Record, Report


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    """后台测试计划列表设置"""
    list_display = ['id', 'name', 'project', 'create_time', 'update_time']
    list_per_page = 10
    ordering = ('-id',)
    list_display_links = ('name',)
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    """后台测试记录列表设置"""
    list_display = ['id', 'plan', 'env', 'pass_rate', 'all', 'success', 'fail', 'error', 'tester', 'status',
                    'create_time']
    list_per_page = 10
    ordering = ('-id',)
    list_display_links = ('plan',)
    list_filter = ('plan',)


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    """后台测试报告列表设置"""
    list_display = ['id', 'record', 'create_time']
    list_per_page = 10
    ordering = ('-id',)
    list_display_links = ('record',)
    list_filter = ('record',)
