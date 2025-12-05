from rest_framework.routers import DefaultRouter
from .views import PlanView, ReportView, RecordView

# 创建一个路由对象
router = DefaultRouter()
# 注册plan测试计划的路由
router.register('plan', PlanView)
# 注册record测试运行记录的路由
router.register('record', RecordView)
# 注册report测试报告的路由
router.register('report', ReportView)

urlpatterns = router.urls
