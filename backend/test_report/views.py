from rest_framework.views import APIView
from jenkins_integration.models import JenkinsJob
from jenkins_integration.utils import R, ResponseCode
from .services import TestReportService
import logging

logger = logging.getLogger('django')


class SyncAllureReportView(APIView):
    """
    独立同步 Allure 报告接口 (test_report 模块专属)
    POST /api/test-report/sync/
    
    Payload:
    {
        "job_name": "xxx", # 必须是数据库中已存在的 Jenkins Job Name
        "build_number": 123
    }
    """
    # 说明：
    # 目前不支持默认同步最后一次，必须明确指定构建号。
    # 通过JenkinsJob 模型中的server字段获取jenkins的认证信息。
    # 负责job的单次构建的同步。
    def post(self, request):
        job_name = request.data.get('job_name')
        build_number = request.data.get('build_number')
        
        if not job_name or not build_number:
            return R.bad_request("Missing job_name or build_number")
            
        try:
            # 1. 查找 Job
            job = JenkinsJob.objects.filter(name=job_name).first()
            if not job:
                return R.error(
                    code=ResponseCode.JENKINS_JOB_NOT_FOUND,
                    message=f"Job '{job_name}' not found"
                )
                
            # 2. 调用 Service 拉取数据
            # 注意：这里我们仅负责数据入库 test_report 表，不干扰 jenkins_integration 模块的原有逻辑
            execution = TestReportService.save_report_from_jenkins(job, int(build_number))
            
            if execution:
                return R.success(
                    message=f"Successfully fetched report for {job_name} #{build_number}",
                    data={"execution_id": execution.id, "timestamp": execution.timestamp}
                )
            else:
                return R.error(message="Failed to fetch or parse Allure report")
                
        except Exception as e:
            logger.error(f"[TestReport] Sync API Error: {str(e)}")
            return R.internal_error(str(e))
