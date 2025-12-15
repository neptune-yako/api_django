"""
Jenkins Job 模板管理器

负责加载、管理和验证 Jenkins Job XML 模板
"""
import os
import logging
from typing import Dict, List, Tuple, Optional

logger = logging.getLogger(__name__)


class JobTemplateManager:
    """
    Jenkins Job 模板管理器
    
    职责：
    - 加载 XML 模板文件
    - 提供模板列表
    - 验证模板格式
    """
    
    # 模板类型定义
    TEMPLATE_TYPES = {
        'freestyle': {
            'name': '自由风格项目',
            'description': '适用于简单的 Shell 脚本执行、构建任务',
            'file': 'freestyle.xml',
            'icon': '📋'
        },
        'pipeline': {
            'name': 'Pipeline 流水线',
            'description': '适用于复杂的多阶段 CI/CD 流程',
            'file': 'pipeline.xml',
            'icon': '🔄'
        },
        'maven': {
            'name': 'Maven 项目',
            'description': '适用于 Java Maven 项目构建',
            'file': 'maven.xml',
            'icon': '☕'
        }
    }
    
    def __init__(self):
        """初始化模板管理器"""
        # 模板目录路径
        self.template_dir = os.path.join(
            os.path.dirname(__file__),
            'job_templates'
        )
        
        # 验证模板目录是否存在
        if not os.path.exists(self.template_dir):
            logger.error(f"模板目录不存在: {self.template_dir}")
            raise FileNotFoundError(f"模板目录不存在: {self.template_dir}")
    
    def get_all_templates(self) -> List[Dict]:
        """
        获取所有可用的模板列表
        
        Returns:
            list: 模板信息列表
            [
                {
                    'type': 'freestyle',
                    'name': '自由风格项目',
                    'description': '...',
                    'file': 'freestyle.xml',
                    'icon': '📋'
                },
                ...
            ]
        """
        templates = []
        
        for template_type, info in self.TEMPLATE_TYPES.items():
            template_path = os.path.join(self.template_dir, info['file'])
            
            # 检查模板文件是否存在
            if os.path.exists(template_path):
                templates.append({
                    'type': template_type,
                    'name': info['name'],
                    'description': info['description'],
                    'file': info['file'],
                    'icon': info.get('icon', '📄')
                })
            else:
                logger.warning(f"模板文件不存在: {template_path}")
        
        return templates
    
    def load_template(self, template_type: str) -> Tuple[bool, str, Optional[str]]:
        """
        加载指定类型的模板
        
        Args:
            template_type: 模板类型 (freestyle, pipeline, maven)
            
        Returns:
            tuple: (是否成功, 消息, XML内容)
        """
        try:
            # 验证模板类型
            if template_type not in self.TEMPLATE_TYPES:
                error_msg = f"不支持的模板类型: {template_type}"
                logger.error(error_msg)
                return False, error_msg, None
            
            # 获取模板文件名
            template_info = self.TEMPLATE_TYPES[template_type]
            template_file = template_info['file']
            template_path = os.path.join(self.template_dir, template_file)
            
            # 检查文件是否存在
            if not os.path.exists(template_path):
                error_msg = f"模板文件不存在: {template_file}"
                logger.error(error_msg)
                return False, error_msg, None
            
            # 读取模板内容
            with open(template_path, 'r', encoding='utf-8') as f:
                xml_content = f.read()
            
            logger.info(f"成功加载模板: {template_type}")
            return True, f"成功加载模板 [{template_info['name']}]", xml_content
            
        except Exception as e:
            error_msg = f"加载模板失败: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, None
    
    def get_template_info(self, template_type: str) -> Tuple[bool, str, Optional[Dict]]:
        """
        获取模板详细信息（不包含 XML 内容）
        
        Args:
            template_type: 模板类型
            
        Returns:
            tuple: (是否成功, 消息, 模板信息字典)
        """
        try:
            if template_type not in self.TEMPLATE_TYPES:
                return False, f"模板类型 [{template_type}] 不存在", None
            
            info = self.TEMPLATE_TYPES[template_type].copy()
            info['type'] = template_type
            
            return True, "获取模板信息成功", info
            
        except Exception as e:
            error_msg = f"获取模板信息失败: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, None
    
    def validate_template_file(self, template_type: str) -> Tuple[bool, str]:
        """
        验证模板文件是否存在且可读
        
        Args:
            template_type: 模板类型
            
        Returns:
            tuple: (是否有效, 消息)
        """
        try:
            if template_type not in self.TEMPLATE_TYPES:
                return False, f"未知的模板类型: {template_type}"
            
            template_file = self.TEMPLATE_TYPES[template_type]['file']
            template_path = os.path.join(self.template_dir, template_file)
            
            if not os.path.exists(template_path):
                return False, f"模板文件不存在: {template_file}"
            
            if not os.access(template_path, os.R_OK):
                return False, f"模板文件不可读: {template_file}"
            
            return True, "模板文件有效"
            
        except Exception as e:
            return False, f"验证失败: {str(e)}"


# 全局模板管理器实例（单例模式）
_template_manager_instance = None

def get_template_manager() -> JobTemplateManager:
    """
    获取模板管理器实例（单例）
    
    Returns:
        JobTemplateManager: 模板管理器实例
    """
    global _template_manager_instance
    
    if _template_manager_instance is None:
        _template_manager_instance = JobTemplateManager()
    
    return _template_manager_instance
