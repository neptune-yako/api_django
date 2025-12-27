from rest_framework.permissions import BasePermission


class CanSyncReport(BasePermission):
    """
    权限：允许同步测试报告
    
    规则：
    - 已认证用户
    - 可以根据需要添加更严格的权限（如：is_staff, 特定用户组等）
    """
    
    def has_permission(self, request, view):
        # 当前策略：所有已认证用户都可以同步报告
        # 如果需要限制为管理员，可以改为：
        # return request.user and request.user.is_authenticated and request.user.is_staff
        return request.user and request.user.is_authenticated


class CanViewReport(BasePermission):
    """
    权限：允许查看测试报告
    
    规则：
    - 已认证用户即可查看
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class IsAdminOrReadOnly(BasePermission):
    """
    权限：管理员可以修改，普通用户只读
    
    规则：
    - GET, HEAD, OPTIONS 请求：所有已认证用户
    - POST, PUT, PATCH, DELETE 请求：仅管理员
    """
    
    def has_permission(self, request, view):
        # 读操作：所有已认证用户
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return request.user and request.user.is_authenticated
        
        # 写操作：仅管理员
        return request.user and request.user.is_authenticated and request.user.is_staff
