from rest_framework.routers import DefaultRouter
from .views import InterfaceView, CaseView

# 创建一个路由对象
router = DefaultRouter()
# 注册interface接口管理的路由
router.register('interface', InterfaceView)
# 注册case测试用例管理的路由
router.register('case', CaseView)

urlpatterns = router.urls
