from django.db import models
from jenkins_integration.models import JenkinsJob

class TestExecution(models.Model):
    """测试执行总览表 (test_execution)"""
    # 业务关联字段 (非甲方SQL强制，但为了业务闭环添加，设为可选)
    job = models.ForeignKey(JenkinsJob, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="关联Jenkins任务", related_name="executions")
    
    # 核心字段 - 严格对应 SQL
    timestamp = models.CharField(max_length=20, unique=True, verbose_name='时间戳')
    report_title = models.CharField(max_length=255, default='自动化测试报告', verbose_name='报告标题')
    
    # 用例统计
    total_cases = models.IntegerField(default=0, verbose_name='总测试用例数')
    passed_cases = models.IntegerField(default=0, verbose_name='通过用例数')
    failed_cases = models.IntegerField(default=0, verbose_name='失败用例数')
    skipped_cases = models.IntegerField(default=0, verbose_name='跳过用例数')
    broken_cases = models.IntegerField(default=0, verbose_name='中断用例数')
    unknown_cases = models.IntegerField(default=0, verbose_name='未知状态用例数')
    
    pass_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name='通过率')
    
    # 时间统计
    min_duration = models.BigIntegerField(default=0, verbose_name='最小执行时间(ms)')
    max_duration = models.BigIntegerField(default=0, verbose_name='最大执行时间(ms)')
    sum_duration = models.BigIntegerField(default=0, verbose_name='总执行时间(ms)')
    execution_time = models.CharField(max_length=50, null=True, blank=True, verbose_name='执行时长')
    
    start_time = models.DateTimeField(null=True, blank=True, verbose_name='开始时间')
    end_time = models.DateTimeField(null=True, blank=True, verbose_name='结束时间')
    
    STATUS_CHOICES = (
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('running', 'Running'),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='success', verbose_name='执行状态')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'test_execution'
        verbose_name = '测试执行总览'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.report_title} - {self.timestamp}"


class TestSuite(models.Model):
    """测试套表 (test_suites)"""
    execution = models.ForeignKey(TestExecution, on_delete=models.CASCADE, related_name='suites', verbose_name='关联的执行')
    suite_name = models.CharField(max_length=255, verbose_name='测试套名称')
    
    # 统计字段 (复用逻辑)
    total_cases = models.IntegerField(default=0)
    passed_cases = models.IntegerField(default=0)
    failed_cases = models.IntegerField(default=0)
    skipped_cases = models.IntegerField(default=0)
    broken_cases = models.IntegerField(default=0)
    unknown_cases = models.IntegerField(default=0)
    
    pass_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    
    # 时间
    min_duration = models.BigIntegerField(default=0)
    max_duration = models.BigIntegerField(default=0)
    sum_duration = models.BigIntegerField(default=0)
    duration_seconds = models.DecimalField(max_digits=10, decimal_places=3, default=0.000, verbose_name='执行时长(秒)')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'test_suites'
        verbose_name = '测试套件'
        verbose_name_plural = verbose_name
        unique_together = ('execution', 'suite_name')

    def __str__(self):
        return self.suite_name


class Category(models.Model):
    """类别表 (categories) - 对应 Allure Categories"""
    execution = models.ForeignKey(TestExecution, on_delete=models.CASCADE, related_name='categories', verbose_name='关联的执行')
    category_name = models.CharField(max_length=100, verbose_name='类别名称')
    
    count = models.IntegerField(default=0, verbose_name='数量')
    
    SEVERITY_CHOICES = (
        ('critical', 'Critical'),
        ('major', 'Major'),
        ('minor', 'Minor'),
        ('trivial', 'Trivial'),
    )
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default='major', verbose_name='严重程度')
    description = models.TextField(null=True, blank=True, verbose_name='描述')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'categories'
        verbose_name = '缺陷类别'
        verbose_name_plural = verbose_name
        unique_together = ('execution', 'category_name')

    def __str__(self):
        return f"{self.category_name} ({self.count})"


class FeatureScenario(models.Model):
    """特性场景表 (feature_scenarios) - 对应 Allure Behaviors"""
    execution = models.ForeignKey(TestExecution, on_delete=models.CASCADE, related_name='scenarios', verbose_name='关联的执行')
    scenario_name = models.CharField(max_length=100, verbose_name='场景名称')
    
    count = models.IntegerField(default=0, verbose_name='数量')
    passed = models.IntegerField(default=0, verbose_name='通过数')
    failed = models.IntegerField(default=0, verbose_name='失败数')
    total = models.IntegerField(default=0, verbose_name='总数')
    
    pass_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name='通过率')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'feature_scenarios'
        verbose_name = '特性场景'
        verbose_name_plural = verbose_name
        unique_together = ('execution', 'scenario_name')

    def __str__(self):
        return self.scenario_name
