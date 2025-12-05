from rest_framework.routers import DefaultRouter
from .views import BugView

# 创建一个路由对象
router = DefaultRouter()
# 注册bug管理的路由
router.register('bug', BugView)

urlpatterns = router.urls
