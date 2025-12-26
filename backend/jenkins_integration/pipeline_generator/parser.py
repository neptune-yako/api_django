"""
Pipeline 脚本解析器
从 Jenkins Pipeline 脚本中提取配置信息，转换为可视化构建器的 pipeline_config 格式
"""

import re
import logging
from typing import Dict, Any, List, Optional
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)


def parse_pipeline_script(script: str) -> Dict[str, Any]:
    """
    解析 Pipeline 脚本，提取可视化配置
    
    Args:
        script: Jenkins Pipeline 脚本内容
        
    Returns:
        pipeline_config 字典，包含:
        - type: 'simple' 或 'custom'
        - simple: { preScript, testCommand, postScript } (仅 simple 类型)
        - custom: [ {name, script}, ... ] (仅 custom 类型)
        - parseable: bool 是否成功解析
    """
    config = {
        'type': 'simple',
        'simple': {},
        'custom': [],
        'parseable': False
    }
    
    try:
        # 移除多余空白
        script = script.strip()
        
        # 检测复杂特征（不支持解析）
        if _is_complex_pipeline(script):
            logger.info("检测到复杂 Pipeline，无法解析为可视化配置")
            return config
        
        # 提取所有 stage
        stages = _extract_stages(script)
        
        if not stages:
            logger.warning("未能提取到任何 stage")
            return config
        
        # 尝试匹配简单模式（3个固定stage）
        simple_config = _try_parse_simple_pattern(stages)
        if simple_config:
            config['type'] = 'simple'
            config['simple'] = simple_config
            config['parseable'] = True
            logger.info(f"成功解析为简单模式: {len(stages)} stages")
            return config
        
        # 否则解析为自定义模式
        custom_config = _parse_custom_pattern(stages)
        if custom_config:
            config['type'] = 'custom'
            config['custom'] = custom_config
            config['parseable'] = True
            logger.info(f"成功解析为自定义模式: {len(custom_config)} stages")
            return config
        
    except Exception as e:
        logger.error(f"解析 Pipeline 脚本失败: {e}")
    
    return config


def parse_config_xml_to_pipeline_config(config_xml: str) -> Optional[Dict[str, Any]]:
    """
    从完整的 config_xml 中提取 script 并解析
    
    Args:
        config_xml: Jenkins Job 完整 XML 配置
        
    Returns:
        pipeline_config 字典或 None
    """
    try:
        root = ET.fromstring(config_xml)
        
        # 查找 <script> 标签
        script_elem = root.find('.//definition/script')
        if script_elem is None or not script_elem.text:
            logger.warning("config_xml 中未找到 <script> 标签")
            return None
        
        script = script_elem.text.strip()
        return parse_pipeline_script(script)
        
    except Exception as e:
        logger.error(f"从 config_xml 提取 script 失败: {e}")
        return None


def _is_complex_pipeline(script: str) -> bool:
    """检测是否为复杂 Pipeline（不支持可视化解析）"""
    complex_patterns = [
        r'@Library',  # 使用共享库
        r'\bdef\s+\w+\s*\(',  # 自定义函数定义
        r'\bfor\s*\(',  # for 循环
        r'\bwhile\s*\(',  # while 循环
        r'\bif\s*\(.+\)\s*{',  # 复杂条件判断
        r'parallel\s*{',  # parallel 块
        r'matrix\s*{',  # matrix 块
        r'environment\s*{',  # environment 块（暂不支持）
    ]
    
    for pattern in complex_patterns:
        if re.search(pattern, script):
            return True
    
    return False


def _extract_stages(script: str) -> List[Dict[str, str]]:
    """
    提取所有 stage 定义
    
    Returns:
        [ {name: str, content: str}, ... ]
    """
    stages = []
    
    # 匹配 stage('name') { ... }
    # 需要处理嵌套的花括号
    pattern = r"stage\s*\(\s*['\"]([^'\"]+)['\"]\s*\)\s*\{"
    
    matches = list(re.finditer(pattern, script))
    
    for i, match in enumerate(matches):
        stage_name = match.group(1)
        start_pos = match.end()
        
        # 找到匹配的结束花括号
        end_pos = _find_matching_brace(script, start_pos)
        
        if end_pos == -1:
            continue
        
        stage_content = script[start_pos:end_pos].strip()
        
        stages.append({
            'name': stage_name,
            'content': stage_content
        })
    
    return stages


def _find_matching_brace(text: str, start: int) -> int:
    """找到匹配的结束花括号位置"""
    depth = 1
    i = start
    
    while i < len(text) and depth > 0:
        if text[i] == '{':
            depth += 1
        elif text[i] == '}':
            depth -= 1
        i += 1
    
    return i - 1 if depth == 0 else -1


def _try_parse_simple_pattern(stages: List[Dict[str, str]]) -> Optional[Dict[str, str]]:
    """
    尝试匹配简单模式（3个固定stage）
    
    Returns:
        { preScript, testCommand, postScript } 或 None
    """
    # 跳过第一个 "环境信息" stage（如果存在）
    filtered_stages = [s for s in stages if s['name'] not in ['环境信息', 'Environment Info']]
    
    if len(filtered_stages) < 2:
        return None
    
    # 期望的 stage 名称模式
    prepare_names = ['准备环境', 'Prepare', 'Setup', 'Environment']
    test_names = ['执行测试', 'Test', 'Run Tests', 'Execute']
    report_names = ['生成报告', 'Report', 'Generate Report', 'Publish']
    
    config = {
        'preScript': '',
        'testCommand': '',
        'postScript': ''
    }
    
    for stage in filtered_stages:
        name = stage['name']
        script = _extract_sh_command(stage['content'])
        
        if any(n in name for n in prepare_names):
            config['preScript'] = script
        elif any(n in name for n in test_names):
            config['testCommand'] = script
        elif any(n in name for n in report_names):
            config['postScript'] = script
    
    # 至少要有测试命令
    if config['testCommand']:
        return config
    
    return None


def _parse_custom_pattern(stages: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    解析为自定义模式
    
    Returns:
        [ {name, script}, ... ]
    """
    custom_stages = []
    
    for stage in stages:
        # 跳过 "环境信息" stage（这是系统自动添加的）
        if stage['name'] in ['环境信息', 'Environment Info']:
            continue
        
        script = _extract_sh_command(stage['content'])
        
        custom_stages.append({
            'name': stage['name'],
            'script': script
        })
    
    return custom_stages


def _extract_sh_command(stage_content: str) -> str:
    """
    从 stage 内容中提取 sh 命令
    
    处理:
    - sh 'command'
    - sh '''command'''
    - sh \"\"\"command\"\"\"
    """
    # 匹配 sh '''...''' 或 sh '...'
    patterns = [
        r"sh\s+'''(.+?)'''",  # 三引号
        r"sh\s+\"\"\"(.+?)\"\"\"",  # 三双引号
        r"sh\s+'([^']+)'",  # 单引号
        r'sh\s+"([^"]+)"',  # 双引号
    ]
    
    for pattern in patterns:
        match = re.search(pattern, stage_content, re.DOTALL)
        if match:
            return match.group(1).strip()
    
    # 如果没有找到 sh，返回整个 steps 内容
    steps_match = re.search(r'steps\s*\{(.+)\}', stage_content, re.DOTALL)
    if steps_match:
        return steps_match.group(1).strip()
    
    return stage_content.strip()
