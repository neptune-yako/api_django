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
