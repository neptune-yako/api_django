from rest_framework.views import APIView
from jenkins_integration.models import JenkinsJob
from jenkins_integration.utils import R, ResponseCode
from .services import TestReportService
from .serializers import (
    SyncReportRequestSerializer,
    SyncJobBuildsRequestSerializer,
    TestExecutionListSerializer,
    TestExecutionDetailSerializer,
    TestSuiteDetailSerializer
)
from .utils.permissions import CanSyncReport, CanViewReport
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
    permission_classes = [CanSyncReport]
    
    def post(self, request):
        # 1. 验证请求参数
        serializer = SyncReportRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return R.bad_request(serializer.errors)
        
        job_name = serializer.validated_data['job_name']
        build_number = serializer.validated_data['build_number']
            
        try:
            # 2. 查找 Job
            job = JenkinsJob.objects.filter(name=job_name).first()
            if not job:
                return R.error(
                    code=ResponseCode.JENKINS_JOB_NOT_FOUND,
                    message=f"Job '{job_name}' not found"
                )
                
            # 3. 调用 Service 拉取数据
            execution = TestReportService.save_report_from_jenkins(job, build_number)
            
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
    permission_classes = [CanSyncReport]
    
    def post(self, request):
        # 1. 验证请求参数
        serializer = SyncJobBuildsRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return R.bad_request(serializer.errors)
        
        job_name = serializer.validated_data['job_name']
        start_build = serializer.validated_data.get('start_build', 1)
        end_build = serializer.validated_data.get('end_build')
        
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
                from jenkins_integration.jenkins_client import get_job_detail_by_server
                
                # 获取 Jenkins Server 配置
                server = job.server
                if not server:
                    return R.error(message=f"Job '{job_name}' 未关联 Jenkins Server")
                
                # 调用 API 获取 Job 详情
                success, message, job_detail = get_job_detail_by_server(server, job.name)
                
                if success and job_detail and job_detail.get('last_build_number'):
                    end_build = job_detail['last_build_number']
                    logger.info(f"[TestReport] 自动获取最新构建号: {end_build}")
                else:
                    # 回退方案：使用数据库中的 last_build_number
                    if job.last_build_number:
                        end_build = job.last_build_number
                        logger.warning(f"[TestReport] Jenkins API 获取失败，使用数据库值: {end_build}")
                    else:
                        return R.error(
                            message=f"无法获取 Job '{job_name}' 的最新构建号，请手动指定 end_build 参数"
                        )
            
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
    permission_classes = [CanViewReport]
    
    def get(self, request):
        from .models import TestExecution
        from backend.pagination import MyPaginator
        
        try:
            # 1. 获取查询参数
            server_id = request.query_params.get('server_id')
            job_id = request.query_params.get('job_id')
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')
            
            # 2. 使用自定义 Manager 进行链式查询
            queryset = (TestExecution.objects
                        .select_related('job')
                        .filter_by_server(server_id)
                        .filter_by_job(job_id)
                        .filter_by_date_range(start_date, end_date)
                        .order_by('-created_at'))
            
            # 3. 分页
            paginator = MyPaginator()
            page = paginator.paginate_queryset(queryset, request)
            
            # 4. 序列化数据
            serializer = TestExecutionListSerializer(page, many=True)
            
            return paginator.get_paginated_response(serializer.data)
            
        except Exception as e:
            logger.error(f"[TestReport] 查询执行列表失败: {str(e)}")
            return R.internal_error(str(e))


class TestExecutionDetailView(APIView):
    """
    查询测试执行详情接口
    GET /api/test-report/executions/{execution_id}/
    """
    permission_classes = [CanViewReport]
    
    def get(self, request, execution_id):
        from .models import TestExecution
        
        try:
            # 1. 查询 TestExecution（优化查询性能）
            execution = TestExecution.objects.prefetch_related(
                'suites', 'categories', 'scenarios'
            ).select_related('job').get(id=execution_id)
            
            # 2. 使用序列化器
            serializer = TestExecutionDetailSerializer(execution)
            
            return R.success(data=serializer.data)
            
        except TestExecution.DoesNotExist:
            return R.error(
                code=ResponseCode.NOT_FOUND,
                message=f"Execution ID [{execution_id}] 不存在"
            )
        except Exception as e:
            logger.error(f"[TestReport] 查询执行详情失败: {str(e)}")
            return R.internal_error(str(e))


class TestSuiteDetailListView(APIView):
    """
    查询测试用例详情列表接口
    GET /api/test-report/executions/{execution_id}/cases/
    
    Query Params:
    - parent_suite: 按父套件筛选（可选）
    - status: 按状态筛选（可选，如 passed, failed）
    """
    permission_classes = [CanViewReport]
    
    def get(self, request, execution_id):
        from .models import TestExecution, TestSuiteDetail
        from django.db import models
        
        try:
            # 1. 验证 Execution 是否存在
            if not TestExecution.objects.filter(id=execution_id).exists():
                return R.error(
                    code=ResponseCode.NOT_FOUND,
                    message=f"Execution ID [{execution_id}] 不存在"
                )
            
            # 2. 查询用例详情
            queryset = TestSuiteDetail.objects.filter(execution_id=execution_id)
            
            # 3. 可选筛选
            parent_suite = request.query_params.get('parent_suite')
            status = request.query_params.get('status')
            
            if parent_suite:
                queryset = queryset.filter(parent_suite=parent_suite)
            if status:
                queryset = queryset.filter(status=status)
            
            # 4. 排序（失败的在前）
            queryset = queryset.order_by(
                models.Case(
                    models.When(status='failed', then=0),
                    models.When(status='broken', then=1),
                    models.When(status='skipped', then=2),
                    models.When(status='passed', then=3),
                    default=4,
                    output_field=models.IntegerField()
                ),
                'parent_suite', 'suite', 'test_method'
            )
            
            # 5. 序列化
            serializer = TestSuiteDetailSerializer(queryset, many=True)
            
            return R.success(data={
                'execution_id': execution_id,
                'total_count': queryset.count(),
                'cases': serializer.data
            })
            
        except Exception as e:
            logger.error(f"[TestReport] 查询用例详情失败: {str(e)}")
            return R.internal_error(str(e))
