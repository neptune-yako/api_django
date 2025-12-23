from rest_framework.views import APIView
from celery.result import AsyncResult
from ..utils import R, ResponseCode

class TaskStatusView(APIView):
    """
    Celery 任务状态查询视图
    """
    def get(self, request, task_id):
        if not task_id:
            return R.bad_request(message='缺少 task_id 参数')
            
        task_result = AsyncResult(task_id)
        
        response_data = {
            'task_id': task_id,
            'status': task_result.status,
            'result': None
        }
        
        if task_result.status == 'SUCCESS':
            response_data['result'] = task_result.result
            return R.success(data=response_data)
            
        elif task_result.status == 'FAILURE':
            response_data['result'] = str(task_result.result)
            return R.error(message=f'任务执行失败: {str(task_result.result)}', data=response_data)
            
        else:
            # PENDING, STARTED, RETRY etc.
            return R.success(message='任务正在执行中', data=response_data)
