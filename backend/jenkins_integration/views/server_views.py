from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.decorators import action
from django.utils import timezone

from ..utils import R, ResponseCode, ResponseMessage
from ..models import JenkinsServer
from ..serializers import JenkinsServerSerializer, JenkinsServerCreateSerializer
import logging
import traceback

logger = logging.getLogger(__name__)

# 服务器管理
class JenkinsTestView(APIView):
    """测试 Jenkins 连接"""
    
    def post(self, request):
        try:
            from ..jenkins_client import test_connection
            
            # 获取请求参数
            url = request.data.get('url')
            username = request.data.get('username')
            token = request.data.get('token')
            
            if not all([url, username, token]):
                return R.bad_request(message="请提供完整连接信息(url, username, token)")

            logger.info(f"开始测试 Jenkins 连接: {url}")
            success, message, data = test_connection(url, username, token)
            
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

    def perform_create(self, serializer):
        # 自动填充创建人
        serializer.save(created_by=self.request.user.username if self.request.user else 'system')

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        return R.success(data=response.data)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return R.success(message=ResponseMessage.UPDATED, data=response.data)
        
    def perform_update(self, serializer):
        # 获取 token，如果没有传或为空，则不更新 token
        # 注意: serializer 验证通过后，如果 token 不在 validated_data 里(因为没传)，save() 自然不会更新它
        # 如果传了空串，validated_data 可能包含 token=''，这里做个防御
        token = self.request.data.get('token')
        if not token and 'token' in serializer.validated_data:
             serializer.validated_data.pop('token')
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return R.success(message=ResponseMessage.DELETED)
    
    @action(detail=True, methods=['post'], url_path='test-connection')
    def test_connection(self, request, pk=None):
        """
        测试指定服务器的连接 (通过 ID)
        POST /api/jenkins/server/{id}/test-connection/
        
        从数据库获取服务器的完整凭据进行连接测试
        解决前端无法获取 token (write_only) 的问题
        """
        try:
            from ..jenkins_client import test_connection
            
            # 获取服务器实例
            server = self.get_object()
            
            logger.info(f"开始测试 Jenkins 服务器连接: ID={server.id}, Name={server.name}, URL={server.url}")
            
            # 从数据库获取完整凭据进行测试
            success, message, data = test_connection(server.url, server.username, server.token)
            
            if success:
                logger.info(f"Jenkins 连接成功: {message}")
                
                # 更新服务器的连接状态和检查时间
                server.connection_status = 'connected'
                server.last_check_time = timezone.now()
                server.save(update_fields=['connection_status', 'last_check_time'])
                
                return R.success(
                    message=ResponseMessage.JENKINS_CONNECTED,
                    data=data
                )
            else:
                logger.error(f"Jenkins 连接失败: {message}")
                
                # 更新服务器的连接状态为失败和检查时间
                server.connection_status = 'failed'
                server.last_check_time = timezone.now()
                server.save(update_fields=['connection_status', 'last_check_time'])
                
                return R.jenkins_error(
                    message=message,
                    code=ResponseCode.JENKINS_CONNECTION_FAILED
                )
                
        except Exception as e:
            error_msg = f"测试连接视图异常: {str(e)}"
            error_trace = traceback.format_exc()
            logger.error(f"{error_msg}\n{error_trace}")
            
            return R.internal_error(
                message=error_msg,
                data={'traceback': error_trace}
            )

