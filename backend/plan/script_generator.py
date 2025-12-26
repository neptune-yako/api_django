"""
测试计划脚本生成器
将测试计划转换为可执行的Python测试脚本(基于pytest)
"""
import json
import re
from .models import Plan
from project.models import Environment
from scene.serializer import SceneRunSerializer


def extract_plan_data(plan_id, env_id):
    """
    提取测试计划的完整数据
    :param plan_id: 测试计划ID
    :param env_id: 测试环境ID
    :return: 包含测试计划和环境配置的字典
    """
    # 获取测试计划
    plan = Plan.objects.get(id=plan_id)
    # 获取测试环境
    env = Environment.objects.get(id=env_id)
    
    # 获取所有测试套件
    scene_list = plan.scene.all()
    
    # 组装套件数据
    scenes_data = []
    for scene in scene_list:
        # 获取套件中的测试步骤
        steps = scene.step_set.all()
        steps_serializer = SceneRunSerializer(steps, many=True)
        sorted_steps = sorted(steps_serializer.data, key=lambda x: x.get('sort', 0))
        
        scenes_data.append({
            'name': scene.name,
            'cases': [step['icase'] for step in sorted_steps]
        })
    
    # 组装环境配置
    env_config = {
        'host': env.host,
        'headers': env.headers,
        'global_variable': env.global_variable,
        'db': env.db,
        'global_func': env.global_func
    }
    
    return {
        'plan_name': plan.name,
        'plan_id': plan.id,
        'env_name': env.name,
        'scenes': scenes_data,
        'env_config': env_config
    }


def generate_pytest_script(plan_data):
    """
    生成pytest格式的Python测试脚本
    :param plan_data: 测试计划数据
    :return: Python脚本内容(字符串)
    """
    script_lines = []
    
    # 生成文件头部注释
    script_lines.extend([
        '"""',
        f'测试计划: {plan_data["plan_name"]}',
        f'计划ID: {plan_data["plan_id"]}',
        f'测试环境: {plan_data["env_name"]}',
        '"""',
        ''
    ])
    
    # 生成导入语句
    script_lines.extend(generate_imports())
    script_lines.append('')
    
    # 生成环境配置
    script_lines.extend(generate_env_config(plan_data['env_config']))
    script_lines.append('')
    
    # 生成BaseTest基类
    script_lines.extend(generate_base_test_class())
    script_lines.append('')
    
    # 为每个测试套件生成测试类
    for idx, scene in enumerate(plan_data['scenes'], 1):
        script_lines.extend(generate_test_class(scene, idx))
        script_lines.append('')
    
    return '\n'.join(script_lines)


def generate_imports():
    """生成必要的import语句"""
    return [
        'import pytest',
        'import requests',
        'import json',
        'import re',
        'from jsonpath import jsonpath',
        'from requests_toolbelt import MultipartEncoder',
    ]


def generate_env_config(env_config):
    """生成环境配置代码"""
    lines = [
        '# 环境配置',
        'class ENV:',
        f'    """全局环境变量"""',
    ]
    
    # 添加基本配置
    lines.append(f'    host = {repr(env_config["host"])}')
    lines.append(f'    headers = {json.dumps(env_config["headers"], ensure_ascii=False, indent=4)}')
    
    # 添加全局变量
    if env_config.get('global_variable'):
        lines.append('')
        lines.append('    # 全局变量')
        for key, value in env_config['global_variable'].items():
            lines.append(f'    {key} = {repr(value)}')
    
    lines.append('')
    lines.append('')
    lines.append('# 临时环境变量(测试运行时使用)')
    lines.append('env = {}')
    
    # 数据库配置
    if env_config.get('db'):
        lines.append('')
        lines.append('# 数据库配置')
        lines.append(f'DB_CONFIG = {json.dumps(env_config["db"], ensure_ascii=False, indent=4)}')
    
    # 全局函数
    if env_config.get('global_func'):
        lines.append('')
        lines.append('# 全局工具函数')
        lines.append(env_config['global_func'])
    
    return lines


def generate_base_test_class():
    """生成BaseTest基类"""
    return [
        'class BaseTest:',
        '    """测试基类,提供通用的测试方法"""',
        '    ',
        '    session = requests.Session()',
        '    ',
        '    @classmethod',
        '    def send_request(cls, method, url, **kwargs):',
        '        """发送HTTP请求"""',
        '        full_url = ENV.host + url if not url.startswith("http") else url',
        '        response = cls.session.request(method, full_url, **kwargs)',
        '        return response',
        '    ',
        '    @classmethod',
        '    def replace_variables(cls, text):',
        '        """替换文本中的变量引用 {{var}}"""',
        '        if not isinstance(text, str):',
        '            return text',
        '        ',
        '        def replace_func(match):',
        '            var_name = match.group(1)',
        '            # 先从临时环境变量中查找',
        '            if var_name in env:',
        '                return str(env[var_name])',
        '            # 再从全局环境变量中查找',
        '            if hasattr(ENV, var_name):',
        '                return str(getattr(ENV, var_name))',
        '            return match.group(0)',
        '        ',
        '        return re.sub(r\'{{(.*?)}}\', replace_func, text)',
        '    ',
        '    @classmethod',
        '    def replace_data(cls, data):',
        '        """递归替换数据结构中的变量"""',
        '        if isinstance(data, dict):',
        '            return {k: cls.replace_data(v) for k, v in data.items()}',
        '        elif isinstance(data, list):',
        '            return [cls.replace_data(item) for item in data]',
        '        elif isinstance(data, str):',
        '            return cls.replace_variables(data)',
        '        return data',
    ]


def generate_test_class(scene_data, scene_index):
    """
    生成测试类代码
    :param scene_data: 测试套件数据
    :param scene_index: 套件索引
    :return: 测试类代码行列表
    """
    # 生成安全的类名(移除特殊字符)
    safe_class_name = f'Test{scene_index}_{sanitize_name(scene_data["name"])}'
    
    lines = [
        f'class {safe_class_name}(BaseTest):',
        f'    """测试套件: {scene_data["name"]}"""',
        ''
    ]
    
    # 为每个测试用例生成测试方法
    for idx, case in enumerate(scene_data['cases'], 1):
        lines.extend(generate_test_method(case, idx))
        lines.append('')
    
    return lines


def generate_test_method(case_data, case_index):
    """
    生成测试方法代码
    :param case_data: 测试用例数据
    :param case_index: 用例索引
    :return: 测试方法代码行列表
    """
    # 生成安全的方法名
    safe_method_name = f'test_{case_index}_{sanitize_name(case_data["title"])}'
    
    lines = [
        f'    def {safe_method_name}(self):',
        f'        """测试用例: {case_data["title"]}"""',
    ]
    
    # 添加前置脚本
    if case_data.get('setup_script') and case_data['setup_script'].strip():
        lines.append('        # 前置脚本')
        setup_lines = case_data['setup_script'].strip().split('\n')
        for line in setup_lines:
            if line.strip() and not line.strip().startswith('#'):
                lines.append(f'        {line}')
        lines.append('')
    
    # 准备请求数据
    interface = case_data['interface']
    method = interface['method']
    url = interface['url']
    
    lines.append('        # 发送请求')
    lines.append(f'        method = {repr(method)}')
    lines.append(f'        url = {repr(url)}')
    
    # 处理请求头
    if case_data.get('headers'):
        lines.append(f'        headers = {json.dumps(case_data["headers"], ensure_ascii=False, indent=8)}')
        lines.append('        headers = self.replace_data(headers)')
    else:
        lines.append('        headers = ENV.headers.copy()')
    
    # 处理请求参数
    if case_data.get('request'):
        request_data = case_data['request']
        lines.append(f'        request_data = {json.dumps(request_data, ensure_ascii=False, indent=8)}')
        lines.append('        request_data = self.replace_data(request_data)')
        
        # 根据请求方法确定参数类型
        if method.upper() in ['GET', 'DELETE']:
            lines.append('        params = request_data')
            lines.append('        response = self.send_request(method, url, headers=headers, params=params)')
        else:
            lines.append('        # 判断Content-Type来决定发送方式')
            lines.append('        content_type = headers.get("Content-Type", "")')
            lines.append('        if "application/json" in content_type:')
            lines.append('            response = self.send_request(method, url, headers=headers, json=request_data)')
            lines.append('        else:')
            lines.append('            response = self.send_request(method, url, headers=headers, data=request_data)')
    else:
        lines.append('        response = self.send_request(method, url, headers=headers)')
    
    lines.append('')
    
    # 添加断言脚本
    if case_data.get('teardown_script') and case_data['teardown_script'].strip():
        lines.append('        # 断言脚本')
        teardown_lines = case_data['teardown_script'].strip().split('\n')
        for line in teardown_lines:
            if line.strip() and not line.strip().startswith('#'):
                lines.append(f'        {line}')
    else:
        # 默认断言状态码
        lines.append('        # 默认断言: 检查状态码')
        lines.append('        assert response.status_code == 200, f"请求失败: {response.status_code}"')
    

    
    return lines


def sanitize_name(name):
    """
    清理名称,移除特殊字符,使其适合作为Python标识符
    :param name: 原始名称
    :return: 清理后的名称
    """
    # 移除或替换特殊字符
    sanitized = re.sub(r'[^\w\u4e00-\u9fff]', '_', name)
    # 移除连续的下划线
    sanitized = re.sub(r'_+', '_', sanitized)
    # 移除首尾下划线
    sanitized = sanitized.strip('_')
    return sanitized if sanitized else 'TestCase'
