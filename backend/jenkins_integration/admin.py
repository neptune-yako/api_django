"""
Jenkins 集成模块 - Django Admin 后台管理

将所有 Jenkins 模型注册到 Django Admin 后台，
方便开发和测试时进行数据管理。
"""

from django.contrib import admin
from .models import JenkinsServer, JenkinsNode, JenkinsJob, AllureReport, AllureTestCase


@admin.register(JenkinsServer)
class JenkinsServerAdmin(admin.ModelAdmin):
    """Jenkins 服务器管理"""
    
    list_display = [
        'id', 'name', 'url', 'username', 
        'is_active', 'connection_status', 
        'last_check_time', 'created_by', 'create_time'
    ]
    list_filter = ['is_active', 'connection_status', 'create_time']
    search_fields = ['name', 'url', 'username', 'created_by']
    readonly_fields = ['create_time', 'update_time']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'url', 'description')
        }),
        ('认证信息', {
            'fields': ('username', 'token')
        }),
        ('状态信息', {
            'fields': ('is_active', 'connection_status', 'last_check_time')
        }),
        ('审计信息', {
            'fields': ('created_by', 'create_time', 'update_time'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """保存时自动设置创建人"""
        if not change:  # 新建时
            obj.created_by = request.user.username
        super().save_model(request, obj, form, change)


@admin.register(JenkinsNode)
class JenkinsNodeAdmin(admin.ModelAdmin):
    """Jenkins 节点管理"""
    
    list_display = [
        'id', 'server', 'name', 'display_name', 
        'num_executors', 'is_online', 'is_idle',
        'last_sync_time'
    ]
    list_filter = ['server', 'is_online', 'is_idle', 'create_time']
    search_fields = ['name', 'display_name', 'labels']
    readonly_fields = ['create_time', 'update_time']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('server', 'name', 'display_name', 'description')
        }),
        ('节点配置', {
            'fields': ('num_executors', 'labels')
        }),
        ('状态信息', {
            'fields': ('is_online', 'is_idle', 'offline_cause', 'last_sync_time')
        }),
        ('时间信息', {
            'fields': ('create_time', 'update_time'),
            'classes': ('collapse',)
        }),
    )


@admin.register(JenkinsJob)
class JenkinsJobAdmin(admin.ModelAdmin):
    """Jenkins 任务管理"""
    
    list_display = [
        'id', 'server', 'name', 'display_name',
        'project', 'plan', 'environment',
        'job_type', 'is_active', 'is_buildable',
        'last_build_number', 'last_build_status',
        'created_by', 'create_time'
    ]
    list_filter = [
        'server', 'project', 'job_type', 
        'is_active', 'is_buildable', 
        'last_build_status', 'create_time'
    ]
    search_fields = ['name', 'display_name', 'description', 'created_by']
    readonly_fields = ['create_time', 'update_time']
    filter_horizontal = ['nodes']  # 多对多字段使用横向筛选器
    
    fieldsets = (
        ('基本信息', {
            'fields': ('server', 'name', 'display_name', 'description')
        }),
        ('关联信息（可选）', {
            'fields': ('project', 'plan', 'environment'),
            'classes': ('collapse',),
            'description': '这些字段是可选的，用于后期与现有系统集成'
        }),
        ('节点配置（可选）', {
            'fields': ('nodes',),
            'classes': ('collapse',),
            'description': '选择任务执行的节点（可多选，留空则使用默认节点）'
        }),
        ('Job 配置', {
            'fields': ('job_type', 'config_xml', 'parameters')
        }),
        ('状态信息', {
            'fields': ('is_active', 'is_buildable')
        }),
        ('构建信息', {
            'fields': (
                'last_build_number', 'last_build_status', 
                'last_build_time', 'last_sync_time'
            )
        }),
        ('审计信息', {
            'fields': ('created_by', 'create_time', 'update_time'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """保存时自动设置创建人"""
        if not change:  # 新建时
            obj.created_by = request.user.username
        super().save_model(request, obj, form, change)


@admin.register(AllureReport)
class AllureReportAdmin(admin.ModelAdmin):
    """Allure 报告管理"""
    
    list_display = [
        'id', 'job', 'build_number',
        'total', 'passed', 'failed', 'broken', 'skipped',
        'pass_rate', 'duration',
        'create_time'
    ]
    list_filter = ['job', 'create_time']
    search_fields = ['job__name', 'allure_url']
    readonly_fields = ['create_time']
    
    fieldsets = (
        ('关联信息', {
            'fields': ('job', 'build_number', 'allure_url')
        }),
        ('统计数据', {
            'fields': ('total', 'passed', 'failed', 'broken', 'skipped', 'pass_rate')
        }),
        ('时间信息', {
            'fields': ('duration', 'start_timestamp', 'stop_timestamp', 'create_time')
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        """查看模式下所有字段只读"""
        if obj:  # 编辑已存在的对象
            return [f.name for f in self.model._meta.fields]
        return self.readonly_fields


@admin.register(AllureTestCase)
class AllureTestCaseAdmin(admin.ModelAdmin):
    """Allure 测试用例管理"""
    
    list_display = [
        'id', 'report', 'name', 'status', 
        'duration', 'uid', 'history_id',
        'create_time'
    ]
    list_filter = ['status', 'report__job', 'create_time']
    search_fields = ['name', 'full_name', 'uid', 'history_id', 'description']
    readonly_fields = ['create_time']
    
    fieldsets = (
        ('关联信息', {
            'fields': ('report', 'uid', 'history_id')
        }),
        ('用例信息', {
            'fields': ('name', 'full_name', 'status', 'duration', 'description')
        }),
        ('错误信息', {
            'fields': ('error_message', 'error_trace'),
            'classes': ('collapse',)
        }),
        ('详细数据', {
            'fields': ('steps', 'attachments', 'labels', 'parameters'),
            'classes': ('collapse',)
        }),
        ('时间信息', {
            'fields': ('create_time',),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        """查看模式下所有字段只读"""
        if obj:  # 编辑已存在的对象
            return [f.name for f in self.model._meta.fields]
        return self.readonly_fields


# 自定义 Admin 站点标题（可选）
admin.site.site_header = 'Jenkins 集成管理后台'
admin.site.site_title = 'Jenkins Admin'
admin.site.index_title = '欢迎使用 Jenkins 集成管理系统'
