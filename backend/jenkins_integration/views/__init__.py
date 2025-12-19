from .server_views import JenkinsTestView, JenkinsServerViewSet
from .job_local_views import JenkinsJobViewSet, SyncJenkinsJobsView
from .job_remote_views import (
    JenkinsJobsView, JenkinsJobManageView, JenkinsJobValidateView,
    JenkinsJobCopyView, JenkinsJobToggleView, JenkinsJobBuildView
)
from .template_views import JenkinsTemplateListView, JenkinsTemplateDetailView
from .build_views import JenkinsBuildLatestView, JenkinsBuildAllureView
from .allure_views import AllureProxyView, SyncBuildResultView
