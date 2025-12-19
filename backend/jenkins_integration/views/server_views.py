from rest_framework import viewsets
from rest_framework.views import APIView
from ..utils import R, ResponseCode, ResponseMessage
from ..models import JenkinsServer
from ..serializers import JenkinsServerSerializer, JenkinsServerCreateSerializer
import logging
import traceback

logger = logging.getLogger(__name__)

# 服务器管理
class JenkinsTestView(APIView):
    """测试 Jenkins 连接"""
    
    def get(self, request):
        try:
            from ..jenkins_client import test_connection
            
            logger.info("开始测试 Jenkins 连接...")
            success, message, data = test_connection()
            
            if success:
                logger.info(f"Jenkins 连接成功: {message}")
                return R.success(
                    message=ResponseMessage.JENKINS_CONNECTED,
                    data=data
                )
            else:
                logger.error(f"Jenkins 连接失败: {message}")
                return R.jenkins_error(
                    message=message,
                    code=ResponseCode.JENKINS_CONNECTION_FAILED
                )
                
        except Exception as e:
            error_msg = f"视图异常: {str(e)}"
            error_trace = traceback.format_exc()
            logger.error(f"{error_msg}\n{error_trace}")
            
            return R.internal_error(
                message=error_msg,
                data={'traceback': error_trace}
            )

class JenkinsServerViewSet(viewsets.ModelViewSet):
    """
    Jenkins 服务器管理视图集 (CRUD)
    """
    queryset = JenkinsServer.objects.all().order_by('-create_time')
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return JenkinsServerCreateSerializer
        return JenkinsServerSerializer

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return R.success(data=response.data)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return R.success(message=ResponseMessage.CREATED, data=response.data)

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        return R.success(data=response.data)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return R.success(message=ResponseMessage.UPDATED, data=response.data)

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return R.success(message=ResponseMessage.DELETED)
