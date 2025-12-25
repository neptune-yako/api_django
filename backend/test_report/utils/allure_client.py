import requests
import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger('django')

class AllureClient:
    """
    Allure 报告数据获取与解析客户端
    负责从 Jenkins 获取 JSON 数据并清洗为符合 test_report 模型的数据结构
    """

    def __init__(self, base_url: str, username: str = None, token: str = None):
        """
        :param base_url: Jenkins Allure 报告根路径，例如 http://jenkins/job/xxx/123/allure
        """
        self.base_url = base_url.rstrip('/')
        self.auth = (username, token) if username and token else None
        self.timeout = 15

    def _get_json(self, path: str) -> Optional[Dict]:
        """通用 JSON 获取方法"""
        url = f"{self.base_url}/{path}"
        try:
            response = requests.get(url, auth=self.auth, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"[AllureClient] Failed to fetch {url}: {str(e)}")
            return None

    # ==================== 1. TestExecution (Summary) ====================
    def get_execution_summary(self) -> Optional[Dict]:
        """
        获取总览数据 (对应 TestExecution 表)
        数据源: widgets/summary.json
        """
        data = self._get_json("widgets/summary.json")
        if not data:
            return None
        
        statistic = data.get('statistic', {})
        time_data = data.get('time', {})
        
        # 计算通过率
        passed = statistic.get('passed', 0)
        total = statistic.get('total', 0)
        pass_rate = round((passed / total) * 100, 2) if total > 0 else 0.00
        
        # 转换时间戳 (Allure 时间戳通常是毫秒)
        # 兼容不同版本的 Allure JSON 结构
        start_ts = time_data.get('start')
        end_ts = time_data.get('stop')
        
        # 核心逻辑：有则填，无则空，优先取最准确的字段
        
        # 1. execution_time (墙钟时间)
        # 只取 'duration' 字段，如果 JSON 里没有就留空或为 0
        duration_ms = time_data.get('duration', 0)
        
        # 2. sum_duration (累计时间)
        # 优先取 'sumDuration'，如果没有则退而求其次取 'duration'
        sum_duration_ms = time_data.get('sumDuration')
        if sum_duration_ms is None:
            sum_duration_ms = duration_ms
        
        return {
            'total_cases': total,
            'passed_cases': passed,
            'failed_cases': statistic.get('failed', 0),
            'skipped_cases': statistic.get('skipped', 0),
            'broken_cases': statistic.get('broken', 0),
            'unknown_cases': statistic.get('unknown', 0),
            'pass_rate': pass_rate,
            'start_time': datetime.fromtimestamp(start_ts / 1000) if start_ts else None,
            'end_time': datetime.fromtimestamp(end_ts / 1000) if end_ts else None,
            'sum_duration': sum_duration_ms,
            'min_duration': time_data.get('minDuration', 0),
            'max_duration': time_data.get('maxDuration', 0),
            'execution_time': self._format_duration(duration_ms) if duration_ms > 0 else None
        }

    # ==================== 2. TestSuite (Suites) ====================
    def get_suites(self) -> List[Dict]:
        """
        获取测试套件数据 (对应 TestSuite 表)
        数据源: data/suites.json
        逻辑: 遍历第一层 children，将其视为一个 Suite 进行统计汇总
        """
        data = self._get_json("data/suites.json")
        if not data:
            return []

        suites_result = []
        children = data.get('children', [])

        for child in children:
            # child 通常代表一个 Package 或 Class
            suite_name = child.get('name', 'Unknown')
            
            # 递归统计该节点下所有叶子节点的数据
            stats = self._aggregate_node_stats(child)
            
            suites_result.append({
                'suite_name': suite_name,
                'total_cases': stats['total'],
                'passed_cases': stats['passed'],
                'failed_cases': stats['failed'],
                'skipped_cases': stats['skipped'],
                'broken_cases': stats['broken'],
                'unknown_cases': stats['unknown'],
                'pass_rate': stats['pass_rate'],
                'sum_duration': stats['duration'],
                'min_duration': stats['min_duration'] if stats['min_duration'] != float('inf') else 0,
                'max_duration': stats['max_duration'],
                'duration_seconds': round(stats['duration'] / 1000, 3)
            })
            
        return suites_result

    # ==================== 3. Category (Defects) ====================
    def get_categories(self) -> List[Dict]:
        """
        获取缺陷类别数据 (对应 Category 表)
        数据源: data/categories.json
        """
        data = self._get_json("data/categories.json")
        if not data:
            return []

        categories_result = []
        # categories.json 通常是一个列表
        for item in data:
            # 防御性检查: 确保 item 是字典
            if not isinstance(item, dict):
                continue
                
            item_name = item.get('name', 'Unknown')
            children = item.get('children', [])
            count = len(children)
            
            # 简单的 severity 映射逻辑 (根据名称或默认值)
            # 这里的规则可以根据实际项目调整，比如关键词匹配
            severity = 'major' 
            if 'fail' in item_name.lower():
                severity = 'critical'
            elif 'break' in item_name.lower() or 'error' in item_name.lower():
                severity = 'major'
                
            categories_result.append({
                'category_name': item_name,
                'description': item.get('description', ''),
                'count': count,
                'severity': severity
            })
            
        return categories_result

    # ==================== 4. FeatureScenario (Behaviors) ====================
    def get_behaviors(self) -> List[Dict]:
        """
        获取特性场景数据 (对应 FeatureScenario 表)
        数据源: data/behaviors.json
        """
        data = self._get_json("data/behaviors.json")
        if not data:
            return []

        scenarios_result = []
        children = data.get('children', [])
        
        # 这里 Allure 的层级可能是 Epic -> Feature -> Story
        # 也可以直接是 Feature -> Story
        # 我们把第一/二层级视为我们的 "Scenario" 或 "Feature"
        
        for feature in children:
            # 防御性检查: 确保 feature 是字典
            if not isinstance(feature, dict):
                continue
                
            feature_name = feature.get('name', 'Unknown')
            
            # 统计
            stats = self._aggregate_node_stats(feature)
            
            scenarios_result.append({
                'scenario_name': feature_name,
                'count': stats['total'],
                'passed': stats['passed'],
                'failed': stats['failed'] + stats['broken'], # 失败通常包含 failed 和 broken
                'total': stats['total'],
                'pass_rate': stats['pass_rate']
            })
            
        return scenarios_result

    # ==================== 辅助方法 === =================
    def _aggregate_node_stats(self, node: Dict) -> Dict:
        """递归统计一个节点及其子节点的所有 Case 数据"""
        stats = {
            'total': 0, 'passed': 0, 'failed': 0,
            'broken': 0, 'skipped': 0, 'unknown': 0,
            'duration': 0,
            'min_duration': float('inf'),
            'max_duration': 0
        }
        
        # 如果有 children，递归处理
        if 'children' in node:
            for child in node['children']:
                # 防御性检查: 某些 Allure 版本可能在 children 中包含非字典项(如字符串 UID)
                if not isinstance(child, dict):
                    continue
                    
                child_stats = self._aggregate_node_stats(child)
                for key in stats:
                    if key in ['min_duration']:
                        stats[key] = min(stats[key], child_stats[key])
                    elif key in ['max_duration']:
                        stats[key] = max(stats[key], child_stats[key])
                    else:
                        stats[key] += child_stats[key]
        else:
            # 叶子节点 (Test Case)
            status = node.get('status', 'unknown')
            duration = node.get('time', {}).get('duration', 0)
            
            stats['total'] = 1
            stats[status if status in stats else 'unknown'] = 1
            stats['duration'] = duration
            stats['min_duration'] = duration
            stats['max_duration'] = duration

        # 计算通过率 (仅在最外层或需要时使用，这里每次都算一下也无妨)
        stats['pass_rate'] = round((stats['passed'] / stats['total']) * 100, 2) if stats['total'] > 0 else 0.00
        
        return stats

    @staticmethod
    def _format_duration(ms: int) -> str:
        """毫秒转可读字符串: 1h 20m 30s"""
        seconds = ms // 1000
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        
        parts = []
        if h: parts.append(f"{h}h")
        if m: parts.append(f"{m}m")
        parts.append(f"{s}s")
        return " ".join(parts) or "< 1s"
