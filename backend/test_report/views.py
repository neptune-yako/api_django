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


class SyncJobBuildsView(APIView):
    """
    批量同步 Job 构建报告接口
    POST /api/test-report/sync-job/
    
    Payload:
    {
        "job_name": "a-test-Pipeline",
        "start_build": 1,        // 可选，默认 1
        "end_build": 100         // 可选，默认为最新构建号
    }
    """
    def post(self, request):
        job_name = request.data.get('job_name')
        start_build = request.data.get('start_build', 1)
        end_build = request.data.get('end_build')
        
        # 1. 参数校验
        if not job_name:
            return R.bad_request("缺少 job_name 参数")
        
        try:
            # 2. 查询 JenkinsJob
            job = JenkinsJob.objects.filter(name=job_name).first()
            if not job:
                return R.error(
                    code=ResponseCode.JENKINS_JOB_NOT_FOUND,
                    message=f"Job '{job_name}' 不存在"
                )
            
            # 3. 如果 end_build 未指定，获取最新构建号
            if not end_build:
                # TODO: 调用 Jenkins API 获取 lastBuild.number
                # 临时方案：默认同步最近 100 个构建
                end_build = start_build + 99
                logger.warning(f"未指定 end_build，默认同步到 Build #{end_build}")
            
            # 4. 启动 Celery 异步任务
            from .tasks import sync_job_builds_task
            task = sync_job_builds_task.delay(
                job.id, int(start_build), int(end_build)
            )
            
            total_builds = int(end_build) - int(start_build) + 1
            
            return R.success(
                message=f"批量同步任务已启动 (Job: {job_name})",
                data={
                    'task_id': task.id,
                    'job_name': job_name,
                    'total_builds': total_builds,
                    'status': 'PENDING'
                }
            )
            
        except Exception as e:
            logger.error(f"[TestReport] 启动批量同步任务失败: {str(e)}")
            return R.internal_error(str(e))


class TaskStatusView(APIView):
    """
    查询任务状态接口
    GET /api/test-report/task-status/{task_id}/
    """
    def get(self, request, task_id):
        from celery.result import AsyncResult
        
        try:
            task = AsyncResult(task_id)
            
            response_data = {
                'task_id': task_id,
                'status': task.state,
            }
            
            if task.state == 'PROGRESS':
                # 任务进行中，返回进度信息
                meta = task.info or {}
                response_data.update(meta)
                
            elif task.state == 'SUCCESS':
                # 任务完成，返回结果
                result = task.result or {}
                response_data.update(result)
                
            elif task.state == 'FAILURE':
                # 任务失败，返回错误
                response_data['error'] = str(task.info)
            
            return R.success(data=response_data)
            
        except Exception as e:
            logger.error(f"[TestReport] 查询任务状态失败: {str(e)}")
            return R.internal_error(str(e))


class TestExecutionListView(APIView):
    """
    查询测试执行列表接口
    GET /api/test-report/executions/
    
    Query Params:
    - job_id: 按 Job 筛选（可选）
    - page: 页码（默认 1）
    - size: 每页数量（默认 20）
    - start_date: 开始日期（可选）
    - end_date: 结束日期（可选）
    """
    def get(self, request):
        from .models import TestExecution
        from backend.pagination import MyPaginator
        
        try:
            # 1. 获取查询参数
            server_id = request.query_params.get('server_id')
            job_id = request.query_params.get('job_id')
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')
            
            # 调试日志
            logger.info(f"[TestReport] 查询参数 - server_id: {server_id}, job_id: {job_id}, start_date: {start_date}, end_date: {end_date}")
            
            # 2. 使用自定义 Manager 进行链式查询
            queryset = (TestExecution.objects
                        .filter_by_server(server_id)
                        .filter_by_job(job_id)
                        .filter_by_date_range(start_date, end_date)
                        .order_by('-created_at'))

            
            # 3. 分页
            paginator = MyPaginator()
            page = paginator.paginate_queryset(queryset, request)
            
            # 4. 序列化数据
            items = []
            for execution in page:
                items.append({
                    'id': execution.id,
                    'timestamp': execution.timestamp,
                    'report_title': execution.report_title,
                    'job_name': execution.job.name if execution.job else None,
                    'total_cases': execution.total_cases,
                    'passed_cases': execution.passed_cases,
                    'failed_cases': execution.failed_cases,
                    'pass_rate': float(execution.pass_rate),
                    'execution_time': execution.execution_time,
                    'status': execution.status,
                    'created_at': execution.created_at.isoformat()
                })
            
            return paginator.get_paginated_response(items)
            
        except Exception as e:
            logger.error(f"[TestReport] 查询执行列表失败: {str(e)}")
            return R.internal_error(str(e))


class TestExecutionDetailView(APIView):
    """
    查询测试执行详情接口
    GET /api/test-report/executions/{execution_id}/
    """
    def get(self, request, execution_id):
        from .models import TestExecution
        
        try:
            # 1. 查询 TestExecution
            execution = TestExecution.objects.prefetch_related(
                'suites', 'categories', 'scenarios'
            ).get(id=execution_id)
            
            # 2. 序列化数据
            data = {
                'execution': {
                    'id': execution.id,
                    'timestamp': execution.timestamp,
                    'report_title': execution.report_title,
                    'job_name': execution.job.name if execution.job else None,
                    'total_cases': execution.total_cases,
                    'passed_cases': execution.passed_cases,
                    'failed_cases': execution.failed_cases,
                    'skipped_cases': execution.skipped_cases,
                    'broken_cases': execution.broken_cases,
                    'unknown_cases': execution.unknown_cases,
                    'pass_rate': float(execution.pass_rate),
                    'execution_time': execution.execution_time,
                    'start_time': execution.start_time.isoformat() if execution.start_time else None,
                    'end_time': execution.end_time.isoformat() if execution.end_time else None,
                    'status': execution.status,
                    'created_at': execution.created_at.isoformat()
                },
                'suites': [
                    {
                        'suite_name': suite.suite_name,
                        'total_cases': suite.total_cases,
                        'passed_cases': suite.passed_cases,
                        'failed_cases': suite.failed_cases,
                        'pass_rate': float(suite.pass_rate),
                        'duration_seconds': float(suite.duration_seconds)
                    }
                    for suite in execution.suites.all()
                ],
                'categories': [
                    {
                        'category_name': cat.category_name,
                        'count': cat.count,
                        'severity': cat.severity,
                        'description': cat.description
                    }
                    for cat in execution.categories.all()
                ],
                'scenarios': [
                    {
                        'scenario_name': scn.scenario_name,
                        'total': scn.total,
                        'passed': scn.passed,
                        'failed': scn.failed,
                        'pass_rate': float(scn.pass_rate)
                    }
                    for scn in execution.scenarios.all()
                ]
            }
            
            return R.success(data=data)
            
        except TestExecution.DoesNotExist:
            return R.error(
                code=ResponseCode.NOT_FOUND,
                message=f"Execution ID [{execution_id}] 不存在"
            )
        except Exception as e:
            logger.error(f"[TestReport] 查询执行详情失败: {str(e)}")
            return R.internal_error(str(e))
