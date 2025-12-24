from .server_views import JenkinsTestView, JenkinsServerViewSet
from .job_local_views import JenkinsJobViewSet, SyncJenkinsJobsView, CleanupJenkinsJobsView
from .job_remote_views import (
    JenkinsJobsView, JenkinsJobValidateView,
    JenkinsJobCopyView, JenkinsJobToggleView, JenkinsJobBuildView
)
from .job_manage_views import JenkinsJobManageView
# from .job_edit_views import JenkinsJobEditView
from .task_views import TaskStatusView
from .template_views import JenkinsTemplateListView, JenkinsTemplateDetailView
from .build_views import JenkinsBuildLatestView, JenkinsBuildAllureView
from .allure_views import AllureProxyView, SyncBuildResultView
from .node_views import (
    JenkinsNodesListView, JenkinsNodeGetConfigView, JenkinsNodeUpdateIPView,
    JenkinsNodeCreateView, JenkinsNodeDeleteView, JenkinsNodeInfoView,
    JenkinsNodeToggleView, JenkinsNodeReconnectView, JenkinsNodeLabelsView,
    JenkinsCredentialsListView, JenkinsNodeSyncView, JenkinsNodesSyncFromJenkinsView
)
