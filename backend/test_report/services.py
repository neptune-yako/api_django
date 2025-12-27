import logging
from django.db import transaction
from typing import Optional
from jenkins_integration.models import JenkinsJob
from test_report.models import TestExecution, TestSuite, TestSuiteDetail, Category, FeatureScenario
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
        
        # 验证必要字段
        required_fields = ['total_cases', 'passed_cases', 'failed_cases']
        if not all(field in summary_data for field in required_fields):
            logger.error(f"[TestReport] Summary data missing required fields: {required_fields}")
            return None
            
        # 4. 生成唯一的 timestamp
        # 使用 start_time 转为简洁格式 (YYYYMMDDHHMMSS) 或使用 job_id + build_number 组合
        if summary_data.get('start_time'):
            unique_timestamp = summary_data['start_time'].strftime('%Y%m%d%H%M%S')
        else:
            unique_timestamp = f"{jenkins_job.id}_{build_number}" 
        
        # 删除旧数据 (如果存在)
        TestExecution.objects.filter(timestamp=unique_timestamp).delete()
        
        execution = TestExecution.objects.create(
            job=jenkins_job,
            timestamp=unique_timestamp, 
            report_title=f"{jenkins_job.name} #{build_number}",
            **summary_data
        )
        
        # 5. 获取并保存 Suites (汇总数据)
        try:
            suites_data = client.get_suites()
            suites_objects = []
            for s_data in suites_data:
                suites_objects.append(TestSuite(execution=execution, **s_data))
            TestSuite.objects.bulk_create(suites_objects)
            logger.info(f"[TestReport] Saved {len(suites_objects)} test suites")
        except Exception as e:
            logger.warning(f"[TestReport] Failed to fetch/save suites: {e}")
        
        # 6. 获取并保存 TestSuiteDetails (用例详情) ⭐ 新增
        try:
            suite_details_data = client.get_suite_details()
            detail_objects = []
            for detail_data in suite_details_data:
                detail_objects.append(TestSuiteDetail(execution=execution, **detail_data))
            TestSuiteDetail.objects.bulk_create(detail_objects)
            logger.info(f"[TestReport] Saved {len(detail_objects)} test case details")
        except Exception as e:
            logger.warning(f"[TestReport] Failed to fetch/save suite details: {e}")
        
        # 7. 获取并保存 Categories
        try:
            categories_data = client.get_categories()
            cat_objects = []
            for c_data in categories_data:
                cat_objects.append(Category(execution=execution, **c_data))
            Category.objects.bulk_create(cat_objects)
            logger.info(f"[TestReport] Saved {len(cat_objects)} categories")
        except Exception as e:
            logger.warning(f"[TestReport] Failed to fetch/save categories: {e}")
        
        # 8. 获取并保存 FeatureScenarios
        try:
            scenarios_data = client.get_behaviors()
            scn_objects = []
            for scn_data in scenarios_data:
                scn_objects.append(FeatureScenario(execution=execution, **scn_data))
            FeatureScenario.objects.bulk_create(scn_objects)
            logger.info(f"[TestReport] Saved {len(scn_objects)} feature scenarios")
        except Exception as e:
            logger.warning(f"[TestReport] Failed to fetch/save scenarios: {e}")
        
        logger.info(f"[TestReport] Successfully saved report for {jenkins_job.name} #{build_number}, Execution ID: {execution.id}")
        return execution
