from django.core.exceptions import ValidationError


def validate_build_number(value):
    """
    验证构建号
    
    :param value: 构建号
    :raises ValidationError: 如果构建号无效
    """
    if value < 1:
        raise ValidationError("构建号必须大于 0")
    
    if value > 999999:
        raise ValidationError("构建号过大，最大值为 999999")
    
    return value


def validate_timestamp(value):
    """
    验证时间戳格式
    
    :param value: 时间戳字符串
    :raises ValidationError: 如果格式无效
    """
    if not value:
        raise ValidationError("时间戳不能为空")
    
    if len(value) > 20:
        raise ValidationError("时间戳长度不能超过 20 个字符")
    
    return value
