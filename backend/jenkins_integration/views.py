"""
Jenkins API 视图 - 简化版
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import traceback
import logging

logger = logging.getLogger(__name__)


class JenkinsTestView(APIView):
    """测试 Jenkins 连接"""
    
    def get(self, request):
        try:
            # 动态导入，避免模块冲突
            from .jenkins_client import test_connection
            
            logger.info("开始测试 Jenkins 连接...")
            success, message, data = test_connection()
            
            if success:
                logger.info(f"Jenkins 连接成功: {message}")
                return Response({
                    'code': 200,
                    'message': message,
                    'data': data
                })
            else:
                logger.error(f"Jenkins 连接失败: {message}")
                return Response({
                    'code': 500,
                    'message': message,
                    'data': None
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            error_msg = f"视图异常: {str(e)}"
            error_trace = traceback.format_exc()
            logger.error(f"{error_msg}\n{error_trace}")
            
            return Response({
                'code': 500,
                'message': error_msg,
                'data': {'traceback': error_trace}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class JenkinsJobsView(APIView):
    """获取所有 Jobs"""
    
    def get(self, request):
        try:
            # 动态导入，避免模块冲突
            from .jenkins_client import get_all_jobs
            
            logger.info("开始获取 Jenkins Jobs...")
            success, message, data = get_all_jobs()
            
            if success:
                logger.info(f"获取 Jobs 成功: {message}")
                return Response({
                    'code': 200,
                    'message': message,
                    'data': data
                })
            else:
                logger.error(f"获取 Jobs 失败: {message}")
                return Response({
                    'code': 500,
                    'message': message,
                    'data': None
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            error_msg = f"视图异常: {str(e)}"
            error_trace = traceback.format_exc()
            logger.error(f"{error_msg}\n{error_trace}")
            
            return Response({
                'code': 500,
                'message': error_msg,
                'data': {'traceback': error_trace}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
