from rest_framework import serializers
from .models import TestExecution, TestSuite, TestSuiteDetail, Category, FeatureScenario


# ==================== 输出序列化器 (Response Serializers) ====================

class TestSuiteSerializer(serializers.ModelSerializer):
    """测试套件序列化器"""
    pass_rate = serializers.DecimalField(max_digits=5, decimal_places=2, coerce_to_string=False)
    duration_seconds = serializers.DecimalField(max_digits=10, decimal_places=3, coerce_to_string=False)
    
    class Meta:
        model = TestSuite
        fields = [
            'id', 'suite_name', 'total_cases', 'passed_cases', 
            'failed_cases', 'skipped_cases', 'broken_cases', 'unknown_cases',
            'pass_rate', 'duration_seconds'
        ]


class TestSuiteDetailSerializer(serializers.ModelSerializer):
    """测试用例详情序列化器"""
    duration_in_ms = serializers.DecimalField(max_digits=12, decimal_places=3, coerce_to_string=False)
    
    class Meta:
        model = TestSuiteDetail
        fields = [
            'id', 'name', 'description', 'parent_suite', 'suite', 'sub_suite',
            'test_class', 'test_method', 'status', 'start_time', 'stop_time',
            'duration_in_ms'
        ]


class CategorySerializer(serializers.ModelSerializer):
    """缺陷分类序列化器"""
    
    class Meta:
        model = Category
        fields = ['id', 'category_name', 'count', 'severity', 'description']


class FeatureScenarioSerializer(serializers.ModelSerializer):
    """特性场景序列化器"""
    pass_rate = serializers.DecimalField(max_digits=5, decimal_places=2, coerce_to_string=False)
    
    class Meta:
        model = FeatureScenario
        fields = ['id', 'scenario_name', 'count', 'passed', 'failed', 'total', 'pass_rate']


class TestExecutionListSerializer(serializers.ModelSerializer):
    """测试执行列表序列化器（简化版）"""
    job_name = serializers.CharField(source='job.name', read_only=True, allow_null=True)
    pass_rate = serializers.DecimalField(max_digits=5, decimal_places=2, coerce_to_string=False)
    
    class Meta:
        model = TestExecution
        fields = [
            'id', 'timestamp', 'report_title', 'job_name', 
            'total_cases', 'passed_cases', 'failed_cases',
            'pass_rate', 'execution_time', 'status', 'created_at'
        ]


class TestExecutionDetailSerializer(serializers.ModelSerializer):
    """测试执行详情序列化器（完整版）"""
    job_name = serializers.CharField(source='job.name', read_only=True, allow_null=True)
    pass_rate = serializers.DecimalField(max_digits=5, decimal_places=2, coerce_to_string=False)
    
    # 嵌套关联数据
    suites = TestSuiteSerializer(many=True, read_only=True)
    categories = CategorySerializer(many=True, read_only=True)
    scenarios = FeatureScenarioSerializer(many=True, read_only=True)
    
    class Meta:
        model = TestExecution
        fields = [
            'id', 'timestamp', 'report_title', 'job_name',
            'total_cases', 'passed_cases', 'failed_cases', 
            'skipped_cases', 'broken_cases', 'unknown_cases',
            'pass_rate', 'execution_time', 'start_time', 'end_time',
            'status', 'created_at',
            'suites', 'categories', 'scenarios'
        ]


# ==================== 输入验证序列化器 (Request Serializers) ====================

class SyncReportRequestSerializer(serializers.Serializer):
    """同步单个报告请求验证"""
    job_name = serializers.CharField(
        required=True,
        max_length=255,
        help_text="Jenkins Job 名称"
    )
    build_number = serializers.IntegerField(
        required=True,
        min_value=1,
        help_text="构建编号"
    )


class SyncJobBuildsRequestSerializer(serializers.Serializer):
    """批量同步报告请求验证"""
    job_name = serializers.CharField(
        required=True,
        max_length=255,
        help_text="Jenkins Job 名称"
    )
    start_build = serializers.IntegerField(
        required=False,
        default=1,
        min_value=1,
        help_text="起始构建号"
    )
    end_build = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=1,
        help_text="结束构建号（不填则自动获取最新）"
    )
    
    def validate(self, data):
        """验证 start_build 必须小于等于 end_build"""
        start = data.get('start_build', 1)
        end = data.get('end_build')
        
        if end and start > end:
            raise serializers.ValidationError({
                'start_build': 'start_build 不能大于 end_build'
            })
        
        return data
