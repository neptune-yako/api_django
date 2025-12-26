"""
Jenkins 集成模块 - 数据库模型

包含以下模型：
1. JenkinsServer - Jenkins 服务器配置
2. JenkinsNode - Jenkins 节点管理
3. JenkinsJob - Jenkins 任务管理
4. AllureReport - Allure 报告统计
5. AllureTestCase - Allure 测试用例详情
"""

from django.db import models


class JenkinsServer(models.Model):
    """Jenkins 服务器配置"""
    
    name = models.CharField(max_length=50, verbose_name="服务器名称")
    url = models.URLField(max_length=200, verbose_name="Jenkins URL")
    username = models.CharField(max_length=50, verbose_name="认证用户名")
    token = models.CharField(max_length=255, verbose_name="API Token")
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    description = models.TextField(blank=True, null=True, verbose_name="服务器描述")
    last_check_time = models.DateTimeField(blank=True, null=True, verbose_name="最后连接测试时间")
    connection_status = models.CharField(
        max_length=20, 
        default='unknown',
        verbose_name="连接状态",
        help_text="connected/failed/unknown"
    )
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    created_by = models.CharField(max_length=20, verbose_name="创建人")
    
    objects = models.Manager()
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = "jenkins_server"
        verbose_name = "Jenkins 服务器"
        verbose_name_plural = verbose_name
        indexes = [
            models.Index(fields=['is_active'], name='idx_jenkins_server_active'),
        ]


class JenkinsNode(models.Model):
    """Jenkins 节点管理"""
    
    server = models.ForeignKey(
        JenkinsServer,
        on_delete=models.CASCADE,
        verbose_name="所属 Jenkins 服务器",
        related_name='nodes'
    )
    name = models.CharField(max_length=100, verbose_name="节点名称")
    display_name = models.CharField(max_length=100, verbose_name="显示名称")
    description = models.TextField(blank=True, null=True, verbose_name="节点描述")
    num_executors = models.IntegerField(default=1, verbose_name="执行器数量")
    labels = models.CharField(max_length=200, blank=True, verbose_name="节点标签")
    ip_address = models.CharField(max_length=50, blank=True, null=True, verbose_name="IP地址")
    is_ip_manual = models.BooleanField(
        default=False, 
        verbose_name="IP是否手动设置",
        help_text="标记IP地址是否为手动设置，True时同步不会覆盖"
    )
    is_online = models.BooleanField(default=True, verbose_name="是否在线")
    is_idle = models.BooleanField(default=True, verbose_name="是否空闲")
    offline_cause = models.TextField(blank=True, null=True, verbose_name="离线原因")
    last_sync_time = models.DateTimeField(blank=True, null=True, verbose_name="最后同步时间")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    objects = models.Manager()
    
    def __str__(self):
        return f"{self.server.name} - {self.name}"
    
    class Meta:
        db_table = "jenkins_node"
        verbose_name = "Jenkins 节点"
        verbose_name_plural = verbose_name
        unique_together = [['server', 'name']]
        indexes = [
            models.Index(fields=['server'], name='idx_jenkins_node_server'),
        ]


class JenkinsJob(models.Model):
    """Jenkins 任务管理"""
    
    # Jenkins 服务器关联
    server = models.ForeignKey(
        JenkinsServer,
        on_delete=models.CASCADE,
        verbose_name="所属 Jenkins 服务器",
        related_name='jobs'
    )
    
    # 基本信息
    name = models.CharField(max_length=100, verbose_name="Job 名称")
    display_name = models.CharField(max_length=100, verbose_name="显示名称")
    description = models.TextField(blank=True, null=True, verbose_name="Job 描述")
    
    # 与现有系统集成（可选，预留扩展）
    project = models.ForeignKey(
        'project.Project',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="关联项目",
        related_name='jenkins_jobs'
    )
    plan = models.ForeignKey(
        'plan.Plan',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="关联测试计划",
        related_name='jenkins_jobs'
    )
    environments = models.ManyToManyField(
        'project.Environment',
        blank=True,
        verbose_name="测试环境列表",
        related_name='jenkins_jobs',
        help_text="可选择多个测试环境"
    )
    
    # 多对多关系：执行节点（可选，预留扩展）
    nodes = models.ManyToManyField(
        JenkinsNode,
        blank=True,
        verbose_name="执行节点列表",
        related_name='jobs',
        help_text="选择任务执行的节点（可多选，留空则使用默认节点）"
    )

    # 单节点主执行节点（向后兼容）
    target_node = models.ForeignKey(
        JenkinsNode,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="目标执行节点",
        related_name='target_jobs',
        help_text="该Job实际运行的节点"
    )

    # Job 配置
    config_xml = models.TextField(blank=True, null=True, verbose_name="Job 配置 XML")
    parameters = models.JSONField(default=dict, blank=True, verbose_name="构建参数")
    
    # Pipeline 可视化配置 (仅本地保存，不发送给 Jenkins)
    pipeline_config = models.JSONField(default=dict, blank=True, verbose_name="Pipeline 可视化配置")

    # 状态信息
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    is_buildable = models.BooleanField(default=True, verbose_name="是否可构建")
    is_multi_node_parent = models.BooleanField(
        default=False,
        verbose_name="是否为多节点主Job",
        help_text="标记该Job是否为多节点并行的父Job"
    )
    
    # 定时任务配置
    cron_enabled = models.BooleanField(
        default=False, 
        verbose_name="启用定时任务",
        help_text="是否启用定时执行"
    )
    cron_schedule = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        verbose_name="Cron表达式",
        help_text="Jenkins cron语法，如: H 18 * * *"
    )
    parent_job = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="父任务",
        related_name='child_jobs',
        help_text="多节点并行时，子Job指向主Job"
    )
    job_type = models.CharField(
        max_length=20,
        default='freestyle',
        verbose_name="Job 类型",
        help_text="freestyle/pipeline/maven"
    )
    
    # 构建信息
    last_build_number = models.IntegerField(blank=True, null=True, verbose_name="最后构建编号")
    last_build_status = models.CharField(max_length=20, blank=True, verbose_name="最后构建状态")
    last_build_time = models.DateTimeField(blank=True, null=True, verbose_name="最后构建时间")
    last_sync_time = models.DateTimeField(blank=True, null=True, verbose_name="最后同步时间")
    
    # 审计字段
    created_by = models.CharField(max_length=20, verbose_name="创建人")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    objects = models.Manager()
    
    def __str__(self):
        return f"{self.server.name} - {self.name}"
    
    def get_allure_url(self, build_number):
        """
        获取指定构建的 Allure 报告 URL
        :param build_number: 构建编号
        :return: Allure 报告 URL
        """
        # 确保 server URL 不以 / 结尾
        base_url = self.server.url.rstrip('/')
        # 拼接标准 Allure 插件 URL 路径
        return f"{base_url}/job/{self.name}/{build_number}/allure/"

    class Meta:
        db_table = "jenkins_job"
        verbose_name = "Jenkins 任务"
        verbose_name_plural = verbose_name
        unique_together = [['server', 'name']]
        indexes = [
            models.Index(fields=['server'], name='idx_jenkins_job_server'),
            models.Index(fields=['project'], name='idx_jenkins_job_project'),
            models.Index(fields=['plan'], name='idx_jenkins_job_plan'),
            models.Index(fields=['is_active'], name='idx_jenkins_job_active'),
            models.Index(fields=['last_build_time'], name='idx_jenkins_job_build_time'),
        ]


class AllureReport(models.Model):
    """Allure 报告统计数据"""
    
    job = models.ForeignKey(
        JenkinsJob,
        on_delete=models.CASCADE,
        verbose_name="所属 Job",
        related_name='reports'
    )
    build_number = models.IntegerField(verbose_name="构建编号")
    
    # 统计数据
    total = models.IntegerField(default=0, verbose_name="总用例数")
    passed = models.IntegerField(default=0, verbose_name="通过数量")
    failed = models.IntegerField(default=0, verbose_name="失败数量")
    broken = models.IntegerField(default=0, verbose_name="损坏数量")
    skipped = models.IntegerField(default=0, verbose_name="跳过数量")
    pass_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="通过率（%）")
    duration = models.IntegerField(default=0, verbose_name="总耗时（毫秒）")
    
    # 测试执行时间（来自 Allure）
    start_timestamp = models.BigIntegerField(verbose_name="测试开始时间戳")
    stop_timestamp = models.BigIntegerField(verbose_name="测试结束时间戳")
    
    # Allure 报告 URL
    allure_url = models.URLField(max_length=200, verbose_name="Allure 报告 URL")
    
    # 数据入库时间
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    objects = models.Manager()
    
    def __str__(self):
        return f"{self.job.name} - Build #{self.build_number}"
    
    class Meta:
        db_table = "allure_report"
        verbose_name = "Allure 报告"
        verbose_name_plural = verbose_name
        unique_together = [['job', 'build_number']]
        indexes = [
            models.Index(fields=['job'], name='idx_allure_report_job'),
            models.Index(fields=['create_time'], name='idx_allure_report_create'),
            models.Index(fields=['start_timestamp'], name='idx_allure_report_start'),
        ]


class AllureTestCase(models.Model):
    """Allure 测试用例详情"""
    
    report = models.ForeignKey(
        AllureReport,
        on_delete=models.CASCADE,
        verbose_name="所属报告",
        related_name='test_cases'
    )
    
    # 用例唯一标识（极重要 - 用于日志下载）
    uid = models.CharField(
        max_length=64,
        unique=True,
        verbose_name="用例唯一标识",
        help_text="Allure 内部生成的唯一标识，用于日志下载"
    )
    
    # 历史 ID（重要 - 用于趋势分析）
    history_id = models.CharField(
        max_length=64,
        verbose_name="用例历史 ID",
        help_text="用于识别同一个用例在不同构建中的表现"
    )
    
    # 用例基本信息
    name = models.CharField(max_length=200, verbose_name="用例名称")
    full_name = models.CharField(max_length=500, blank=True, verbose_name="用例完整路径")
    status = models.CharField(
        max_length=20,
        verbose_name="用例状态",
        help_text="passed/failed/broken/skipped"
    )
    duration = models.IntegerField(default=0, verbose_name="执行时长（毫秒）")
    description = models.TextField(blank=True, null=True, verbose_name="用例描述")
    
    # 错误信息
    error_message = models.TextField(blank=True, null=True, verbose_name="失败原因")
    error_trace = models.TextField(blank=True, null=True, verbose_name="错误堆栈")
    
    # JSON 字段
    steps = models.JSONField(default=list, blank=True, verbose_name="测试步骤")
    attachments = models.JSONField(
        default=list,
        blank=True,
        verbose_name="附件信息",
        help_text="日志、截图等附件列表"
    )
    labels = models.JSONField(default=dict, blank=True, verbose_name="标签信息")
    parameters = models.JSONField(default=dict, blank=True, verbose_name="参数信息")
    
    # 创建时间
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    objects = models.Manager()
    
    def __str__(self):
        return f"{self.report.job.name} - {self.name}"
    
    class Meta:
        db_table = "allure_test_case"
        verbose_name = "Allure 测试用例"
        verbose_name_plural = verbose_name
        indexes = [
            models.Index(fields=['report'], name='idx_allure_testcase_report'),
            models.Index(fields=['uid'], name='idx_allure_testcase_uid'),
            models.Index(fields=['history_id'], name='idx_allure_testcase_history'),
            models.Index(fields=['status'], name='idx_allure_testcase_status'),
        ]
