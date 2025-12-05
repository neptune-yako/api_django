from rest_framework.routers import DefaultRouter
from .views import CronjobView

# 创建一个路由对象
router = DefaultRouter()
# 注册cronjob定时任务的路由
router.register('cronjob', CronjobView)

urlpatterns = router.urls
