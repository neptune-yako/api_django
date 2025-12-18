"""
Allure 报告解析工具

负责请求 Jenkins Allure 插件生成的 JSON 文件，
并解析为符合数据库模型的数据结构。
"""
import requests
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger('django')

class AllureParser:
    """Allure 报告解析器"""
    
    def __init__(self, base_url: str, username: str = None, token: str = None):
        """
        初始化解析器
        :param base_url: Allure 报告的基础 URL，例如 http://jenkins/job/test/1/allure/
        :param username: Jenkins 用户名（可选）
        :param token: Jenkins Token（可选）
        """
        self.base_url = base_url.rstrip('/')
        self.auth = (username, token) if username and token else None
        self.timeout = 10  # 请求超时时间（秒）

    def get_summary(self) -> Optional[Dict]:
        """
        获取概要统计数据 (summary.json)
        :return: 包含统计数据的字典，失败返回 None
        """
        url = f"{self.base_url}/widgets/summary.json"
        try:
            response = requests.get(url, auth=self.auth, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            # 提取关键字段
            statistic = data.get('statistic', {})
            time_data = data.get('time', {})
            
            return {
                'total': statistic.get('total', 0),
                'passed': statistic.get('passed', 0),
                'failed': statistic.get('failed', 0),
                'broken': statistic.get('broken', 0),
                'skipped': statistic.get('skipped', 0),
                'duration': time_data.get('duration', 0),
                'start_timestamp': time_data.get('start', 0),
                'stop_timestamp': time_data.get('stop', 0),
                # 计算通过率
                'pass_rate': self._calculate_pass_rate(
                    statistic.get('passed', 0), 
                    statistic.get('total', 0)
                )
            }
        except Exception as e:
            logger.error(f"Failed to get Allure summary from {url}: {str(e)}")
            return None

    def get_test_cases(self) -> List[Dict]:
        """
        获取测试用例详情 (suites.json)
        :return: 测试用例列表
        """
        url = f"{self.base_url}/data/suites.json"
        test_cases = []
        
        try:
            response = requests.get(url, auth=self.auth, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            # 递归解析树状结构
            children = data.get('children', [])
            self._parse_children(children, test_cases)
            
            return test_cases
            
        except Exception as e:
            logger.error(f"Failed to get Allure suites from {url}: {str(e)}")
            return []

    def _parse_children(self, children: List[Dict], result_list: List[Dict], parent_name: str = ""):
        """
        递归解析 suites.json 的 children 节点
        :param children: 子节点列表
        :param result_list: 结果列表
        :param parent_name: 父节点名称（用于拼接 full_name）
        """
        for child in children:
            # 如果还有 children，说明是目录/套件，继续递归
            if 'children' in child:
                current_name = f"{parent_name}/{child.get('name')}" if parent_name else child.get('name')
                self._parse_children(child['children'], result_list, current_name)
            else:
                # 是叶子节点（测试用例）
                test_case = self._extract_test_case_info(child, parent_name)
                if test_case:
                    result_list.append(test_case)

    def _extract_test_case_info(self, child: Dict, suite_name: str) -> Dict:
        """从叶子节点提取用例信息"""
        uid = child.get('uid')
        if not uid:
            return None
            
        time_info = child.get('time', {})
        
        # 提取步骤
        raw_steps = child.get('steps', [])
        steps = self._format_steps(raw_steps)
        
        # 提取附件
        raw_attachments = child.get('attachments', [])
        attachments = self._format_attachments(raw_attachments)
        
        return {
            'uid': uid,
            'name': child.get('name', 'Unknown'),
            'full_name': f"{suite_name}/{child.get('name')}" if suite_name else child.get('name'),
            'status': child.get('status', 'unknown'),
            'time': time_info, # 保留原始时间信息
            'duration': time_info.get('duration', 0),
            'description': child.get('description', ''),
            'error_message': child.get('statusMessage'),
            'error_trace': child.get('statusTrace'),
            'steps': steps,
            'attachments': attachments,
            'labels': child.get('labels', []),
            'parameters': child.get('parameters', []),
            # historyId 通常在 retries/history 节点中，或者直接在 attributes
            # suites.json 有时不直接包含 historyId，可能需要单独处理，
            # 这里的实现先尝试获取，如果没有则用 uid 代替（注意：实际 Allure 版本可能有差异）
            'history_id': child.get('historyId', uid) 
        }

    def _format_steps(self, steps: List[Dict]) -> List[Dict]:
        """格式化步骤信息"""
        formatted = []
        for step in steps:
            formatted.append({
                'name': step.get('name'),
                'status': step.get('status'),
                'duration': step.get('time', {}).get('duration', 0),
                'attachments': self._format_attachments(step.get('attachments', [])),
                # 支持嵌套步骤
                'steps': self._format_steps(step.get('steps', []))
            })
        return formatted

    def _format_attachments(self, attachments: List[Dict]) -> List[Dict]:
        """
        格式化附件信息
        注意：这里只存储元数据，下载需要拼接 URL
        URL 格式: {base_url}/data/attachments/{source}
        """
        formatted = []
        for att in attachments:
            formatted.append({
                'name': att.get('name'),
                'source': att.get('source'), # 关键字段，文件名
                'type': att.get('type'),
                'size': att.get('size')
            })
        return formatted

    @staticmethod
    def _calculate_pass_rate(passed: int, total: int) -> float:
        """计算通过率"""
        if total <= 0:
            return 0.0
        return round((passed / total) * 100, 2)
