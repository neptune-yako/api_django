"""
Allure 报告数据同步服务

处理 Allure 数据抓取和入库的核心业务逻辑。
"""
import logging
from django.db import transaction
from ..models import JenkinsJob, AllureReport, AllureTestCase
from ..utils.allure_parser import AllureParser
from ..utils.codes import ResponseCode
from datetime import datetime

logger = logging.getLogger('django')

class AllureSyncService:
    """Allure 数据同步服务"""
    
    @staticmethod
    def sync_report_data(job: JenkinsJob, build_number: int, allure_url: str):
        """
        同步指定 Job 构建的 Allure 报告数据
        
        :param job: JenkinsJob 实例
        :param build_number: 构建编号
        :param allure_url: Allure 报告完整 URL（例如 http://jenkins/job/xxx/1/allure/）
        :return: (bool, str) - (是否成功, 错误信息)
        """
        try:
            # 1. 初始化解析器
            # 注意：如果 Jenkins 需要认证，这里需要传入 server.username/token
            # 目前假设是无认证或 Token 已包含在 header (如果后期需要)
            # 更好的方式是在 JenkinsServer 模型中取配置
            parser = AllureParser(
                base_url=allure_url,
                username=job.server.username,
                token=job.server.token
            )
            
            # 2. 获取统计数据 (Summary)
            summary = parser.get_summary()
            if not summary:
                return False, "Failed to fetch Allure summary.json"
                
            # 3. 开启事务，确保数据一致性
            with transaction.atomic():
                # 3.1 创建或更新 AllureReport
                report, created = AllureReport.objects.update_or_create(
                    job=job,
                    build_number=build_number,
                    defaults={
                        'total': summary['total'],
                        'passed': summary['passed'],
                        'failed': summary['failed'],
                        'broken': summary['broken'],
                        'skipped': summary['skipped'],
                        'pass_rate': summary['pass_rate'],
                        'duration': summary['duration'],
                        'start_timestamp': summary['start_timestamp'],
                        'stop_timestamp': summary['stop_timestamp'],
                        'allure_url': allure_url
                    }
                )
                
                # 3.2 如果是更新，先清空旧的测试用例（防止重复）
                if not created:
                    AllureTestCase.objects.filter(report=report).delete()
                    
                # 3.3 获取并入库测试用例详情 (Suites)
                test_cases_data = parser.get_test_cases()
                if test_cases_data:
                    test_cases_to_create = []
                    for case_data in test_cases_data:
                        test_cases_to_create.append(AllureTestCase(
                            report=report,
                            uid=case_data['uid'],
                            history_id=case_data.get('history_id', ''),
                            name=case_data['name'],
                            full_name=case_data.get('full_name', ''),
                            status=case_data['status'],
                            duration=case_data.get('duration', 0),
                            description=case_data.get('description', ''),
                            error_message=case_data.get('error_message'),
                            error_trace=case_data.get('error_trace'),
                            steps=case_data.get('steps', []),
                            attachments=case_data.get('attachments', []),
                            labels=case_data.get('labels', []),
                            parameters=case_data.get('parameters', [])
                        ))
                    
                    # 批量插入，提高性能
                    AllureTestCase.objects.bulk_create(test_cases_to_create)
                    
                # 3.4 更新 Job 的最后构建信息 (可选，保持同步)
                job.last_build_number = build_number
                job.last_build_status = 'SUCCESS' if summary['failed'] == 0 and summary['broken'] == 0 else 'FAILURE'
                job.last_build_time = datetime.fromtimestamp(summary['stop_timestamp'] / 1000) if summary['stop_timestamp'] else None
                job.save(update_fields=['last_build_number', 'last_build_status', 'last_build_time'])

            return True, f"Successfully synced Allure report for build #{build_number}"
            
        except Exception as e:
            logger.error(f"Error syncing Allure report: {str(e)}")
            return False, str(e)
