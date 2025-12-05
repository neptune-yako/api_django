from rest_framework.routers import DefaultRouter
from .views import UserView, RoleView

# 创建一个路由对象
router = DefaultRouter()
# 注册user用户管理的路由
router.register('user', UserView)
# 注册role用户角色管理的路由
router.register('role', RoleView)

urlpatterns = router.urls
