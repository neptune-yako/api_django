"""
测试报告模块 - Celery 异步任务
"""
from celery import shared_task
import logging
from jenkins_integration.models import JenkinsJob
from test_report.services import TestReportService

logger = logging.getLogger('django')


@shared_task(bind=True)
def sync_job_builds_task(self, job_id, start_build, end_build):
    """
    批量同步 Job 构建报告的 Celery 任务
    
    Args:
        self: Celery task 实例（支持 update_state）
        job_id: Jenkins Job ID
        start_build: 起始构建号
        end_build: 结束构建号
        
    Returns:
        dict: 同步结果统计
        {
            'status': 'SUCCESS' | 'FAILURE',
            'total': int,
            'success_count': int,
            'failed_count': int,
            'failed_builds': [{'build': int, 'error': str}],
            'execution_ids': [int]
        }
    """
    try:
        # 1. 获取 Job 对象
        try:
            job = JenkinsJob.objects.get(id=job_id)
        except JenkinsJob.DoesNotExist:
            logger.error(f"Job ID [{job_id}] 不存在")
            return {
                'status': 'FAILURE',
                'error': f'Job ID [{job_id}] 不存在'
            }
        
        # 2. 计算构建范围
        build_range = range(start_build, end_build + 1)
        total = len(build_range)
        
        logger.info(f"开始批量同步 Job [{job.name}] 的构建 #{start_build}-#{end_build}，共 {total} 个")
        
        # 3. 初始化结果统计
        results = {
            'success': [],
            'failed': [],
            'execution_ids': []
        }
        
        # 4. 循环同步每个构建
        for i, build_num in enumerate(build_range):
            try:
                # 调用单次同步逻辑
                execution = TestReportService.save_report_from_jenkins(job, build_num)
                
                if execution:
                    results['success'].append(build_num)
                    results['execution_ids'].append(execution.id)
                    logger.info(f"成功同步 Build #{build_num}，Execution ID: {execution.id}")
                else:
                    results['failed'].append({
                        'build': build_num,
                        'error': '报告获取失败或解析失败'
                    })
                    logger.warning(f"同步 Build #{build_num} 失败：报告获取失败")
                    
            except Exception as e:
                error_msg = str(e)
                logger.error(f"同步 Build #{build_num} 异常: {error_msg}")
                results['failed'].append({
                    'build': build_num,
                    'error': error_msg
                })
            
            # 5. 更新进度（重要！）
            self.update_state(
                state='PROGRESS',
                meta={
                    'current': i + 1,
                    'total': total,
                    'success_count': len(results['success']),
                    'failed_count': len(results['failed']),
                    'failed_builds': [f['build'] for f in results['failed']]
                }
            )
        
        # 6. 返回最终结果
        final_result = {
            'status': 'SUCCESS',
            'total': total,
            'success_count': len(results['success']),
            'failed_count': len(results['failed']),
            'failed_builds': results['failed'],
            'execution_ids': results['execution_ids']
        }
        
        logger.info(
            f"批量同步完成: Job [{job.name}], "
            f"成功 {final_result['success_count']}/{total}, "
            f"失败 {final_result['failed_count']}/{total}"
        )
        
        return final_result
        
    except Exception as e:
        error_msg = f"批量同步任务异常: {str(e)}"
        logger.error(error_msg)
        return {
            'status': 'FAILURE',
            'error': error_msg
        }
