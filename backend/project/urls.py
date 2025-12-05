from rest_framework.routers import DefaultRouter
from .views import ProjectView, EnvironmentView, FileView

# 创建一个路由对象
router = DefaultRouter()
# 注册project项目管理的路由
router.register('project', ProjectView)
# 注册environment环境管理的路由
router.register('environment', EnvironmentView)
# 注册file文件上传的路由
router.register('file', FileView)

urlpatterns = router.urls
