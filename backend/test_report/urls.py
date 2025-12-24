from django.urls import path
from .views import SyncAllureReportView

urlpatterns = [
    path('sync/', SyncAllureReportView.as_view(), name='sync_report'),
]
