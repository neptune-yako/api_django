import json
from django_celery_beat.models import CrontabSchedule, PeriodicTask
from django.db import transaction
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework import permissions, mixins, status
from .models import Cronjob
from .serializer import CronjobSerializer
from backend.pagination import MyPaginator


@extend_schema(tags=["定时任务"])
class CronjobView(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, mixins.ListModelMixin,
                  GenericViewSet):
    """定时任务增删查改的序列化器"""
    queryset = Cronjob.objects.all().order_by('-id')
    serializer_class = CronjobSerializer
    permission_classes = [permissions.IsAuthenticated]
    # 设置查询过虑字段
    filterset_fields = ('project', 'plan')
    # 设置分页数据
    pagination_class = MyPaginator

    @extend_schema(summary="获取定时任务列表")
    def list(self, request, *args, **kwargs):
        """获取定时任务列表，包含测试计划定时任务和 Jenkins 定时任务"""
        # 1. 获取测试计划定时任务（原有逻辑）
        response = super().list(request, *args, **kwargs)
        
        # 2. 获取 Jenkins 定时任务
        from jenkins_integration.models import JenkinsJob
        
        jenkins_jobs = JenkinsJob.objects.filter(
            cron_enabled=True
        ).select_related('server', 'project', 'plan').order_by('-update_time')
        
        # 序列化 Jenkins 定时任务数据
        jenkins_cron_data = []
        for job in jenkins_jobs:
            jenkins_cron_data.append({
                'id': job.id,
                'name': job.name,
                'cron_schedule': job.cron_schedule,
                'is_active': job.is_active,
                'server_name': job.server.name if job.server else '',
                'project_name': job.project.name if job.project else '',
                'plan_name': job.plan.name if job.plan else '',
                'job_type': job.job_type,
                'last_build_time': job.last_build_time,
                'last_build_status': job.last_build_status,
            })
        
        # 3. 添加到响应
        response.data['jenkins_cron_jobs'] = jenkins_cron_data
        
        return response

    @extend_schema(summary="创建任务")
    def create(self, request, *args, **kwargs):
        """重写定时任务新建的方法"""
        # 开启视图
        with transaction.atomic():
            # 创建一个事物保存节点
            save_point = transaction.savepoint()
            try:
                # 调用父类的方法创建一条定时任务
                result = super().create(request, *args, **kwargs)
                # 获取创建定时任务的规则
                rule = result.data.get('rule').split(" ")
                rule_dict = dict(zip(['minute', 'hour', 'day_of_week', 'day_of_month', 'month_of_year'], rule))
                # 使用django-celer-beat中的CrontabSchedule模型创建一个规则对象
                try:
                    cronjob = CrontabSchedule.objects.get(**rule_dict)
                except:
                    cronjob = CrontabSchedule.objects.create(**rule_dict)
                # 使用django-celer-beat中的PeriodicTask创建一个周期性调度任务
                PeriodicTask.objects.create(
                    name=str(result.data.get('id')),
                    task='plan.tasks.run_task',
                    crontab=cronjob,
                    kwargs=json.dumps({
                        "env_id": result.data.get('env'),
                        "task_id": result.data.get('plan'),
                        "tester": request.user.username
                    }),
                    enabled=result.data.get('status'),
                )
            except:
                # 进行事物回滚
                transaction.savepoint_rollback(save_point)
                return Response({'detail': "定时任务创建失败！"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                # 提交事物
                transaction.savepoint_commit(save_point)
                return Response(result.data)

    @extend_schema(summary="更新任务")
    def update(self, request, *args, **kwargs):
        """重写定时任务更新的方法"""
        with transaction.atomic():
            save_point = transaction.savepoint()
            try:
                # 调用父类的方法更新数据
                res = super().update(request, *args, **kwargs)
                cronjob = self.get_object()
                # 更新周期任务和定期任务的时间规则
                ptask = PeriodicTask.objects.get(name=str(cronjob.id))
                # 更新执行的任务和测试环境
                ptask.kwargs = json.dumps({
                    "env_id": res.data.get('env'),
                    "task_id": res.data.get('plan'),
                    "tester": request.user.username
                })
                # 更新定时任务的状态
                ptask.enabled = res.data.get('status')
                # 获取定期执行的规则
                rule = res.data.get('rule').split(" ")
                rule_dict = dict(zip(['minute', 'hour', 'day_of_week', 'day_of_month', 'month_of_year'], rule))
                # 使用django-celer-beat中的CrontabSchedule模型创建一个规则对象
                try:
                    cronjob = CrontabSchedule.objects.get(**rule_dict)
                except:
                    cronjob = CrontabSchedule.objects.create(**rule_dict)
                # 更新周期规则
                ptask.crontab = cronjob
                ptask.save()
            except:
                transaction.savepoint_rollback(save_point)
                return Response({'detail:"定时任务修改失败！'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                transaction.savepoint_commit(save_point)
                return res

    @extend_schema(summary="删除任务")
    def destroy(self, request, *args, **kwargs):
        """重写定时任务删除的方法"""
        with transaction.atomic():
            save_point = transaction.savepoint()
            try:
                cronjob = self.get_object()
                ptask = PeriodicTask.objects.get(name=str(cronjob.id))
                ptask.enabled = False
                ptask.delete()
                res = super().destroy(request, *args, **kwargs)
            except Exception as e:
                transaction.savepoint_rollback(save_point)
                return Response({'detail:"定时任务删除失败！'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                transaction.savepoint_commit(save_point)
                return res
