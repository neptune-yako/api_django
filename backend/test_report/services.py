import logging
from django.db import transaction
from typing import Optional
from jenkins_integration.models import JenkinsJob
from test_report.models import TestExecution, TestSuite, Category, FeatureScenario
from test_report.utils.allure_client import AllureClient

logger = logging.getLogger('django')

class TestReportService:
    """
    测试报告业务逻辑层
    负责协调 AllureClient 和 Database，完成数据持久化
    """

    @staticmethod
    @transaction.atomic
    def save_report_from_jenkins(jenkins_job: JenkinsJob, build_number: int) -> Optional[TestExecution]:
        """
        从 Jenkins 拉取 Allure 报告并保存到数据库 (原子操作)
        
        :param jenkins_job: JenkinsJob 实例
        :param build_number: 构建编号
        :return: 创建成功的 TestExecution 实例，失败返回 None
        """
        # 1. 构造 Jenkins Allure 基础 URL
        # 格式通常为: {jenkins_url}/job/{job_name}/{build_number}/allure
        base_url = f"{jenkins_job.server.url}/job/{jenkins_job.name}/{build_number}/allure"
        
        logger.info(f"[TestReport] Starting to fetch report for {jenkins_job.name} #{build_number} from {base_url}")
        
        # 2. 初始化客户端
        client = AllureClient(
            base_url=base_url,
            username=jenkins_job.server.username,
            token=jenkins_job.server.token
        )
        
        # 3. 获取 Summary 数据
        summary_data = client.get_execution_summary()
        if not summary_data:
            logger.error(f"[TestReport] Failed to fetch summary for {jenkins_job.name} #{build_number}")
            return None
            
        # 4. 创建 TestExecution (如果是重新同步，先删除旧记录?)
        # 策略：timestamp 是唯一的，我们用 job_name + build_number 作为 timestamp 的一部分或者直接使用
        # 甲方 SQL 定义 timestamp 为 unique varchar(20)
        # 建议使用 "{job_id}_{build_number}" 或 Jenkins 原始 timestamp
        # 这里为了唯一性，我们使用构建的时间戳，如果 summary 里有的话，或者构造一个唯一的 ID
        
        # 为了防止重复导入，先检查是否存在
        # 这里假设 timestamp 使用 Build Number 的唯一标识，或者如果是 timestamp 字段，它就是时间
        # 让我们使用 summary_data['start_time'] 的时间戳作为 timestamp，
        # 但要注意可能有多个 job 在同一秒开始？
        # 更稳健的方法：生成一个唯一的 key: f"{jenkins_job.id}-{build_number}" 存入 timestamp 字段
        # 或者复用 SQL 的意图：timestamp 只是一个时间戳。
        # 让我们暂且使用 Jenkins 的 Start Timestamp (ms)
        
        ts_value = str(int(summary_data['start_time'].timestamp() * 1000)) if summary_data['start_time'] else str(build_number)
        
        # 如果已经存在相同时间戳的记录，决定是跳过还是更新。
        # 这里选择：如果存在且 job 相同，则更新；否则创建。
        # 但 timestamp 是 unique 的，会有冲突。
        # 实战修正：我们生成一个组合键存入 timestamp 以避免冲突: "{job_id}_{build_number}"
        unique_timestamp = f"{jenkins_job.id}_{build_number}" 
        
        # 删除旧数据 (如果存在)
        TestExecution.objects.filter(timestamp=unique_timestamp).delete()
        
        execution = TestExecution.objects.create(
            job=jenkins_job,
            timestamp=unique_timestamp, 
            report_title=f"{jenkins_job.name} #{build_number}",
            **summary_data
        )
        
        # 5. 获取并保存 Suites
        suites_data = client.get_suites()
        suites_objects = []
        for s_data in suites_data:
            suites_objects.append(TestSuite(execution=execution, **s_data))
        TestSuite.objects.bulk_create(suites_objects)
        
        # 6. 获取并保存 Categories
        categories_data = client.get_categories()
        cat_objects = []
        for c_data in categories_data:
            cat_objects.append(Category(execution=execution, **c_data))
        Category.objects.bulk_create(cat_objects)
        
        # 7. 获取并保存 FeatureScenarios
        scenarios_data = client.get_behaviors()
        scn_objects = []
        for scn_data in scenarios_data:
            scn_objects.append(FeatureScenario(execution=execution, **scn_data))
        FeatureScenario.objects.bulk_create(scn_objects)
        
        logger.info(f"[TestReport] Successfully saved report for {jenkins_job.name} #{build_number}, Execution ID: {execution.id}")
        return execution
