import time
import uuid
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

User = get_user_model()

class UserMockView(APIView):
    """
    用户管理模拟接口
    """
    authentication_classes = [] # 公开接口，无需认证
    permission_classes = []

    def get(self, request, pk=None):
        if pk:
            return Response({
                "id": pk,
                "name": f"User {pk}",
                "email": f"user{pk}@test.com",
                "role": "admin" if pk == '1' else "user"
            })
        
        users = [
            {"id": 1, "name": "Alice", "role": "admin"},
            {"id": 2, "name": "Bob", "role": "user"},
            {"id": 3, "name": "Charlie", "role": "user"}
        ]
        return Response(users)

    def post(self, request):
        return Response({
            "id": int(time.time()),
            "name": request.data.get("name", "New User"),
            "status": "created"
        }, status=status.HTTP_201_CREATED)

class StatusMockView(APIView):
    """
    状态码模拟接口
    """
    authentication_classes = []
    permission_classes = []

    def get(self, request, code):
        code = int(code)
        if code == 200:
            return Response({"status": "success", "code": 200})
        elif code == 400:
            return Response({"error": "Bad Request", "code": 400}, status=status.HTTP_400_BAD_REQUEST)
        elif code == 500:
            return Response({"error": "Internal Server Error", "code": 500}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({"message": f"Returned custom status {code}"}, status=code)

class DelayMockView(APIView):
    """
    延迟响应接口
    """
    authentication_classes = []
    permission_classes = []

    def get(self, request, seconds):
        seconds = float(seconds)
        time.sleep(seconds)
        return Response({
            "message": f"Delayed for {seconds} seconds",
            "slept": seconds
        })

class LoginMockView(APIView):
    """
    登录模拟接口
    """
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        
        # 这是一个模拟登录，但在实际中，为了让 IsAuthenticated 生效
        # 我们必须生成一个真实的、带有签名的 JWT Token
        if username == "admin" and password == "123456":
            # 1. 获取或创建用户（为了 Token 载荷）
            user, created = User.objects.get_or_create(username=username)
            if created:
                user.set_password(password)
            
            # 确保用户是激活状态，否则 Token 会被标记为无效
            if not user.is_active:
                user.is_active = True
                
            user.save()
            
            # 2. 生成真实 JWT
            refresh = RefreshToken.for_user(user)
            
            return Response({
                "token": str(refresh.access_token),
                "user": {"id": user.id, "name": user.username}
            })
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

class SecureDataMockView(APIView):
    """
    需鉴权数据接口 - 这个接口需要认证
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return Response({
            "data": "This is secure data",
            "user": str(request.user),
            "timestamp": time.time()
        })
