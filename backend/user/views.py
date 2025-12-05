import re
from django.contrib.auth import logout
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from .models import Role
from .serializers import RoleSerializer
from .models import User
from django.core.exceptions import ValidationError
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.viewsets import ModelViewSet
from .serializers import UserSerializer, RegisterSerializer
from backend.pagination import MyPaginator
from django.core.validators import validate_email


@extend_schema(tags=["登录接口"])
class LoginView(TokenObtainPairView):
    """自定义登录返回的数据结构"""

    @extend_schema(summary="用户登录")
    def post(self, request: Request, *args, **kwargs) -> Response:
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            # 自定义登录返回的字段：token、refresh、mobile、email、username、nickname、date_joined、id
            result = serializer.validated_data
            result['id'] = serializer.user.id
            result['mobile'] = serializer.user.mobile
            result['email'] = serializer.user.email
            result['username'] = serializer.user.username
            result['nickname'] = serializer.user.nickname
            result['date_joined'] = serializer.user.date_joined
            result['is_superuser'] = serializer.user.is_superuser
            result['is_staff'] = serializer.user.is_staff
            result['last_login'] = serializer.user.last_login
            result['update_time'] = serializer.user.update_time
            result['msg'] = '用户登录成功！'
            result['token'] = result.pop('access')
            return Response(result, status=status.HTTP_200_OK)
        except TokenError as e:
            raise InvalidToken(e.args[0])


@extend_schema(tags=["用户注册"])
class RegisterView(viewsets.GenericViewSet):
    """自定义注册功能"""
    # 不校验登录权限
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    @extend_schema(summary="注册用户")
    @action(methods=['post'], detail=False)
    def register(self, request: Request, *args, **kwargs) -> Response:
        try:
            username = request.data.get('username')
            password = request.data.get('password')
            check_password = request.data.get('check_password')
            email = request.data.get('email')
            mobile = request.data.get('mobile')
            nickname = request.data.get('nickname')
            # 验证输入不为空
            if not all([username, password, check_password, email, mobile, nickname]):
                return Response({'detail': '必填项输入不能为空！'}, status=status.HTTP_400_BAD_REQUEST)
            # 验证密码一致性
            if password != check_password:
                return Response({'detail': '二次密码输入不一致！'}, status=status.HTTP_400_BAD_REQUEST)
            # 检查密码强度6位及以上
            if not self.valid_password(password):
                return Response({'detail': '密码强度不足6位！'}, status=status.HTTP_400_BAD_REQUEST)
            # 检查邮箱格式
            if not self.valid_email(email):
                return Response({'detail': '邮箱格式不正确！'}, status=status.HTTP_400_BAD_REQUEST)
            # 检查手机号格式
            if not self.valid_mobile(mobile):
                return Response({'detail': '手机号格式不正确！'}, status=status.HTTP_400_BAD_REQUEST)
            # 检查用户是否已存在
            exists = User.objects.filter(username=username).exists()
            if exists:
                return Response({'detail': '当前该账号已被注册！'}, status=status.HTTP_400_BAD_REQUEST)
            # 检查手机号是否已存在
            exists = User.objects.filter(mobile=mobile).exists()
            if exists:
                return Response({'detail': '当前手机号已被注册！'}, status=status.HTTP_400_BAD_REQUEST)
            # 检查邮箱是否已存在
            exists = User.objects.filter(email=email).exists()
            if exists:
                return Response({'detail': '当前邮箱已被注册！'}, status=status.HTTP_400_BAD_REQUEST)
            # 创建用户
            new_user = User(username=username, password=password, email=email, mobile=mobile,
                                                is_superuser=request.data.get('is_superuser', False), date_joined=timezone.now(),
                                                nickname=nickname, is_staff=request.data.get('is_staff', False), is_active=request.data.get('is_active', True))
            # 保存用户
            new_user.save()
            response = {"username": new_user.username, 'nickname': new_user.nickname, 'email': new_user.email,
                        'mobile': new_user.mobile, 'date_joined': new_user.date_joined, 'is_active': new_user.is_active,
                        'is_superuser': new_user.is_superuser, 'msg': '用户注册成功！'}
            return Response({'detail': response}, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail':  str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def valid_password(password: str) -> bool:
        """检查密码强度6-18位"""
        if 6 <= len(password) <= 18:
            return True
        return False

    @staticmethod
    def valid_email(email: str) -> bool:
        """检查邮箱格式"""
        try:
            validate_email(email)
            return True
        except ValidationError:
            return False

    @staticmethod
    def valid_mobile(mobile: str) -> bool:
        """检查手机号格式"""
        if re.match(r'1[3-9]\d{9}', mobile):
            return True
        return False


@extend_schema(tags=["用户管理"])
class UserView(ModelViewSet):
    """用户管理视图集：增删改查操作"""
    queryset = User.objects.all().prefetch_related('roles').order_by('-id')
    serializer_class = UserSerializer
    # 请求登录的权限校验
    permission_classes = [permissions.IsAuthenticated]
    # 设置分页数据
    pagination_class = MyPaginator


@extend_schema(tags=["角色管理"])
class RoleView(ModelViewSet):
    """角色管理视图集：增删改查操作"""
    queryset = Role.objects.all().order_by('-id')
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = MyPaginator

    @extend_schema(summary="删除角色")
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # 检查角色是否被用户关联
        if instance.user.exists():
            return Response({"detail": "该角色已被用户关联，无法删除！"}, status=status.HTTP_400_BAD_REQUEST)
        return super().destroy(request, *args, **kwargs)


@extend_schema(tags=["退出登录"])
class LogoutView(APIView):
    """退出登录功能"""
    # 请求登录的权限校验
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    @extend_schema(summary="退出登录")
    def post(self, request) -> Response:
        # 更新当前用户的最后登录时间
        user = request.user
        user.last_login = timezone.now()
        user.save()
        # 退出登录
        logout(request)
        return Response({'detail': '退出登录成功！'}, status=status.HTTP_200_OK)
