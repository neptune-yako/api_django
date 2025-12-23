from .server_views import JenkinsTestView, JenkinsServerViewSet
from .job_local_views import JenkinsJobViewSet, SyncJenkinsJobsView
from .job_remote_views import (
    JenkinsJobsView, JenkinsJobManageView, JenkinsJobValidateView,
    JenkinsJobCopyView, JenkinsJobToggleView, JenkinsJobBuildView
)
from .job_edit_views import JenkinsJobEditView
from .task_views import TaskStatusView
from .template_views import JenkinsTemplateListView, JenkinsTemplateDetailView
from .build_views import JenkinsBuildLatestView, JenkinsBuildAllureView
from .allure_views import AllureProxyView, SyncBuildResultView
from .node_views import JenkinsNodesListView, JenkinsNodeGetConfigView, JenkinsNodeUpdateIPView
