from rest_framework.routers import DefaultRouter
from .views import SceneView, StepView

# 创建一个路由对象
router = DefaultRouter()
# 注册scene测试套件管理的路由
router.register('scene', SceneView)
# 注册step测试用例步骤的路由
router.register('step', StepView)

urlpatterns = router.urls
