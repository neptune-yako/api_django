"""
参数解析器 - 用于动态插槽功能

提供 XML 配置中参数占位符的提取、替换和验证功能
"""
import re
import xml.sax.saxutils as saxutils
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)


def extract_jenkins_native_params(xml_content: str) -> List[str]:
    """
    从 Jenkins parameters 块中提取参数名
    
    支持的参数类型:
    - string(name: 'xxx', ...)
    - booleanParam(name: 'xxx', ...)
    - choice(name: 'xxx', choices: [...])
    - password(name: 'xxx', ...)
    - text(name: 'xxx', ...)
    
    Args:
        xml_content: XML 配置字符串
        
    Returns:
        list: 参数名列表
        
    Example:
        >>> xml = "parameters { string(name: 'score', ...) }"
        >>> extract_jenkins_native_params(xml)
        ['score']
    """
    if not xml_content:
        return []
    
    params = []
    
    try:
        # 匹配各种 Jenkins 参数类型
        patterns = [
            r"string\(name:\s*['\"]([\w]+)['\"]",
            r"booleanParam\(name:\s*['\"]([\w]+)['\"]",
            r"choice\(name:\s*['\"]([\w]+)['\"]",
            r"password\(name:\s*['\"]([\w]+)['\"]",
            r"text\(name:\s*['\"]([\w]+)['\"]",
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, xml_content)
            params.extend(matches)
        
        logger.info(f"从 Jenkins parameters 块中提取到 {len(params)} 个参数: {params}")
        return params
        
    except Exception as e:
        logger.error(f"提取 Jenkins 参数失败: {str(e)}")
        return []


def extract_params(xml_content: str) -> List[str]:
    """
    从 XML 配置中提取所有动态参数（支持两种格式）
    
    支持格式:
    1. {{}} 占位符: {{score}}, {{name}}
    2. Jenkins parameters 块: string(name: 'score', ...)
    
    Args:
        xml_content: XML 配置字符串
        
    Returns:
        list: 去重后的参数名列表（按字母顺序排序）
        
    Example:
        >>> xml = '<script>echo {{score}}</script>'
        >>> extract_params(xml)
        ['score']
        >>> xml2 = "parameters { string(name: 'age', ...) }"
        >>> extract_params(xml2)
        ['age']
    """
    if not xml_content:
        return []
    
    params = set()
    
    try:
        # 方式 1: 提取 {{}} 占位符
        pattern_placeholder = r'\{\{([a-zA-Z_][a-zA-Z0-9_]*)\}\}'
        placeholder_matches = re.findall(pattern_placeholder, xml_content)
        params.update(placeholder_matches)
        
        # 方式 2: 提取 Jenkins parameters 块
        jenkins_params = extract_jenkins_native_params(xml_content)
        params.update(jenkins_params)
        
        # 过滤系统保留占位符
        reserved_placeholders = {'description', 'agent_label'}
        params = params - reserved_placeholders
        
        # 返回排序后的列表
        result = sorted(list(params))
        
        logger.info(f"从 XML 中提取到 {len(result)} 个动态参数: {result}")
        return result
        
    except Exception as e:
        logger.error(f"提取参数失败: {str(e)}")
        return []


def replace_params(xml_content: str, params_dict: Dict[str, str]) -> str:
    """
    替换 XML 中的参数占位符
    
    Args:
        xml_content: 原始 XML 配置
        params_dict: 参数键值对，例如 {"score": "95", "env": "prod"}
        
    Returns:
        str: 替换后的 XML 字符串
        
    Raises:
        ValueError: 参数值验证失败时抛出
        
    Example:
        >>> xml = '<script>echo {{score}}</script>'
        >>> replace_params(xml, {"score": "95"})
        '<script>echo 95</script>'
    """
    if not xml_content:
        return xml_content
    
    if not params_dict:
        logger.warning("参数字典为空，未进行任何替换")
        return xml_content
    
    result_xml = xml_content
    replaced_count = 0
    
    try:
        for key, value in params_dict.items():
            # 验证参数值
            is_valid, error_msg = validate_param_value(value)
            if not is_valid:
                raise ValueError(f"参数 '{key}' 的值验证失败: {error_msg}")
            
            # XML 转义处理
            safe_value = escape_xml_value(value)
            
            # 构建占位符
            placeholder = f'{{{{{key}}}}}'
            
            # 执行替换
            if placeholder in result_xml:
                result_xml = result_xml.replace(placeholder, safe_value)
                replaced_count += 1
                logger.debug(f"替换参数 '{key}': {placeholder} -> {safe_value}")
        
        logger.info(f"参数替换完成，共替换 {replaced_count} 个参数")
        return result_xml
        
    except Exception as e:
        logger.error(f"参数替换失败: {str(e)}")
        raise


def validate_param_value(value: str, max_length: int = 10000) -> Tuple[bool, str]:
    """
    验证参数值的安全性和合法性
    
    Args:
        value: 参数值
        max_length: 最大长度限制（默认 10000 字符）
        
    Returns:
        tuple: (is_valid, error_message)
            - is_valid: True 表示验证通过，False 表示验证失败
            - error_message: 失败时的错误信息，成功时为 None
            
    Example:
        >>> validate_param_value("normal value")
        (True, None)
        >>> validate_param_value("a" * 20000)
        (False, "参数值过长，最大 10000 字符")
    """
    # 类型转换
    if not isinstance(value, str):
        value = str(value)
    
    # 长度检查
    if len(value) > max_length:
        return False, f"参数值过长，最大 {max_length} 字符"
    
    # 可以添加更多验证规则
    # 例如：
    # - 禁止某些危险字符
    # - SQL 注入检测
    # - XSS 攻击检测
    
    return True, None


def escape_xml_value(value: str) -> str:
    """
    对参数值进行 XML 转义
    
    Args:
        value: 原始参数值
        
    Returns:
        str: 转义后的安全值
        
    Example:
        >>> escape_xml_value("<script>alert('xss')</script>")
        "&lt;script&gt;alert('xss')&lt;/script&gt;"
    """
    if not isinstance(value, str):
        value = str(value)
    
    # 使用标准库进行 XML 转义
    # 会转义: & < > " '
    return saxutils.escape(value)


def get_missing_params(xml_content: str, params_dict: Dict[str, str]) -> List[str]:
    """
    检查哪些参数在 XML 中存在但用户未提供
    
    Args:
        xml_content: XML 配置
        params_dict: 用户提供的参数字典
        
    Returns:
        list: 缺失的参数名列表
        
    Example:
        >>> xml = '<script>{{a}} {{b}} {{c}}</script>'
        >>> get_missing_params(xml, {"a": "1", "b": "2"})
        ['c']
    """
    required_params = set(extract_params(xml_content))
    provided_params = set(params_dict.keys())
    missing = required_params - provided_params
    
    return sorted(list(missing))


def has_jenkins_native_params(xml_content: str) -> bool:
    """
    检查是否包含 Jenkins 原生参数定义
    
    Args:
        xml_content: XML 配置
        
    Returns:
        bool: True 表示包含 Jenkins parameters 块
        
    Example:
        >>> has_jenkins_native_params('parameters { string(...) }')
        True
    """
    if not xml_content:
        return False
    
    return bool(re.search(r'parameters\s*\{', xml_content))


def has_dynamic_params(xml_content: str) -> bool:
    """
    快速检查 XML 是否包含动态参数（任意格式）
    
    支持两种格式:
    1. {{}} 占位符
    2. Jenkins parameters 块
    
    Args:
        xml_content: XML 配置
        
    Returns:
        bool: True 表示包含动态参数，False 表示不包含
        
    Example:
        >>> has_dynamic_params('<script>echo {{score}}</script>')
        True
        >>> has_dynamic_params('parameters { string(...) }')
        True
        >>> has_dynamic_params('<script>echo hello</script>')
        False
    """
    if not xml_content:
        return False
    
    # 检查 {{}} 占位符
    if re.search(r'\{\{[a-zA-Z_][a-zA-Z0-9_]*\}\}', xml_content):
        return True
    
    # 检查 Jenkins parameters 块
    if has_jenkins_native_params(xml_content):
        return True
    
    return False
