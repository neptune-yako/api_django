from rest_framework.views import APIView
from ..utils import R
import logging

logger = logging.getLogger(__name__)

# 模板管理
class JenkinsTemplateListView(APIView):
    """获取所有可用的 Job 模板列表"""
    def get(self, request):
        try:
            from ..template_manager import get_template_manager
            manager = get_template_manager()
            templates = manager.get_all_templates()
            return R.success(message=f"成功获取 {len(templates)} 个模板", data=templates)
        except Exception as e:
            logger.error(f"获取模板列表失败: {str(e)}")
            return R.internal_error(message=str(e))


class JenkinsTemplateDetailView(APIView):
    """获取指定类型的模板内容"""
    def get(self, request, template_type):
        try:
            from ..template_manager import get_template_manager
            manager = get_template_manager()
            
            info_success, info_msg, template_info = manager.get_template_info(template_type)
            if not info_success:
                return R.bad_request(message=info_msg)
            
            load_success, load_msg, xml_content = manager.load_template(template_type)
            if not load_success:
                return R.jenkins_error(message=load_msg)
            
            return R.success(
                message=load_msg,
                data={
                    'type': template_type,
                    'name': template_info['name'],
                    'description': template_info['description'],
                    'xml_content': xml_content
                }
            )
        except Exception as e:
            logger.error(f"获取模板失败: {str(e)}")
            return R.internal_error(message=str(e))
