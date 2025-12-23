"""
Jenkins 集成模块 - DRF 序列化器

为所有 Jenkins 模型提供 REST API 序列化器，
支持前后端 JSON 数据交互。
"""

from rest_framework import serializers
from .models import JenkinsServer, JenkinsNode, JenkinsJob, AllureReport, AllureTestCase


class JenkinsServerSerializer(serializers.ModelSerializer):
    """Jenkins 服务器序列化器"""
    
    # 统计信息（只读）
    jobs_count = serializers.SerializerMethodField()
    nodes_count = serializers.SerializerMethodField()
    
    class Meta:
        model = JenkinsServer
        fields = [
            'id', 'name', 'url', 'username', 'token',
            'is_active', 'description', 'connection_status',
            'last_check_time', 'created_by',
            'create_time', 'update_time',
            'jobs_count', 'nodes_count'  # 额外统计字段
        ]
        read_only_fields = ['id', 'create_time', 'update_time', 'jobs_count', 'nodes_count']
        extra_kwargs = {
            'token': {'write_only': True}  # Token 不在响应中返回（安全考虑）
        }
    
    def get_jobs_count(self, obj):
        """获取该服务器下的 Job 数量"""
        return obj.jobs.count()
    
    def get_nodes_count(self, obj):
        """获取该服务器下的 Node 数量"""
        return obj.nodes.count()


class JenkinsNodeSerializer(serializers.ModelSerializer):
    """Jenkins 节点序列化器"""
    
    # 嵌套显示服务器名称
    server_name = serializers.CharField(source='server.name', read_only=True)
    
    class Meta:
        model = JenkinsNode
        fields = [
            'id', 'server', 'server_name',
            'name', 'display_name', 'description',
            'num_executors', 'labels', 'ip_address',
            'is_online', 'is_idle', 'offline_cause',
            'last_sync_time', 'create_time', 'update_time'
        ]
        read_only_fields = ['id', 'server_name', 'ip_address', 'create_time', 'update_time']


class JenkinsJobSerializer(serializers.ModelSerializer):
    """Jenkins 任务序列化器"""
    
    # 嵌套显示关联对象名称
    server_name = serializers.CharField(source='server.name', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True, allow_null=True)
    plan_name = serializers.CharField(source='plan.name', read_only=True, allow_null=True)
    environment_name = serializers.CharField(source='environment.name', read_only=True, allow_null=True)
    
    # 统计信息
    reports_count = serializers.SerializerMethodField()
    
    class Meta:
        model = JenkinsJob
        fields = [
            'id', 'server', 'server_name',
            'name', 'display_name', 'description',
            'project', 'project_name',
            'plan', 'plan_name',
            'environment', 'environment_name',
            'nodes',  # 多对多字段
            'config_xml', 'parameters',
            'is_active', 'is_buildable', 'job_type',
            'last_build_number', 'last_build_status',
            'last_build_time', 'last_sync_time',
            'created_by', 'create_time', 'update_time',
            'reports_count'  # 额外统计字段
        ]
        read_only_fields = [
            'id', 'server_name', 'project_name', 'plan_name', 'environment_name',
            'create_time', 'update_time', 'reports_count'
        ]
    
    def get_reports_count(self, obj):
        """获取该 Job 下的报告数量"""
        return obj.reports.count()


class JenkinsJobSimpleSerializer(serializers.ModelSerializer):
    """Jenkins 任务简化序列化器（用于列表展示）"""
    
    server_name = serializers.CharField(source='server.name', read_only=True)
    
    class Meta:
        model = JenkinsJob
        fields = [
            'id', 'server', 'server_name',
            'name', 'display_name', 'job_type',
            'is_active', 'last_build_number', 'last_build_status',
            'create_time'
        ]
        read_only_fields = ['id', 'server_name', 'create_time']


class AllureTestCaseSerializer(serializers.ModelSerializer):
    """Allure 测试用例序列化器"""
    
    class Meta:
        model = AllureTestCase
        fields = [
            'id', 'report',
            'uid', 'history_id',
            'name', 'full_name', 'status', 'duration',
            'description', 'error_message', 'error_trace',
            'steps', 'attachments', 'labels', 'parameters',
            'create_time'
        ]
        read_only_fields = ['id', 'create_time']


class AllureTestCaseSimpleSerializer(serializers.ModelSerializer):
    """Allure 测试用例简化序列化器（用于嵌套展示）"""
    
    class Meta:
        model = AllureTestCase
        fields = [
            'id', 'uid', 'name', 'status', 'duration'
        ]
        read_only_fields = ['id']


class AllureReportSerializer(serializers.ModelSerializer):
    """Allure 报告序列化器"""
    
    # 嵌套显示 Job 信息
    job_name = serializers.CharField(source='job.name', read_only=True)
    
    # 统计信息
    test_cases_count = serializers.SerializerMethodField()
    
    # 嵌套测试用例列表（可选，用于详情页）
    test_cases = AllureTestCaseSimpleSerializer(many=True, read_only=True)
    
    class Meta:
        model = AllureReport
        fields = [
            'id', 'job', 'job_name', 'build_number',
            'total', 'passed', 'failed', 'broken', 'skipped',
            'pass_rate', 'duration',
            'start_timestamp', 'stop_timestamp',
            'allure_url', 'create_time',
            'test_cases_count', 'test_cases'  # 额外字段
        ]
        read_only_fields = ['id', 'job_name', 'create_time', 'test_cases_count', 'test_cases']
    
    def get_test_cases_count(self, obj):
        """获取该报告下的用例数量"""
        return obj.test_cases.count()


class AllureReportSimpleSerializer(serializers.ModelSerializer):
    """Allure 报告简化序列化器（用于列表展示）"""
    
    job_name = serializers.CharField(source='job.name', read_only=True)
    
    class Meta:
        model = AllureReport
        fields = [
            'id', 'job', 'job_name', 'build_number',
            'total', 'passed', 'failed', 'pass_rate',
            'allure_url', 'create_time'
        ]
        read_only_fields = ['id', 'job_name', 'create_time']


# ==================== 创建/更新专用序列化器 ====================

class JenkinsServerCreateSerializer(serializers.ModelSerializer):
    """Jenkins 服务器创建序列化器（不返回 Token）"""
    
    class Meta:
        model = JenkinsServer
        fields = [
            'name', 'url', 'username', 'token',
            'is_active', 'description', 'created_by'
        ]
        extra_kwargs = {
            'token': {'write_only': True, 'required': False}
        }
        read_only_fields = ['created_by']


class AllureReportCreateSerializer(serializers.ModelSerializer):
    """Allure 报告创建序列化器（带测试用例）"""
    
    test_cases = AllureTestCaseSerializer(many=True, required=False)
    
    class Meta:
        model = AllureReport
        fields = [
            'job', 'build_number',
            'total', 'passed', 'failed', 'broken', 'skipped',
            'pass_rate', 'duration',
            'start_timestamp', 'stop_timestamp',
            'allure_url', 'test_cases'
        ]
    
    def create(self, validated_data):
        """创建报告及其关联的测试用例"""
        test_cases_data = validated_data.pop('test_cases', [])
        report = AllureReport.objects.create(**validated_data)
        
        # 批量创建测试用例
        for test_case_data in test_cases_data:
            AllureTestCase.objects.create(report=report, **test_case_data)
        
        return report
