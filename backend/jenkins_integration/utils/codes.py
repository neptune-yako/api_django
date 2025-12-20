"""
统一响应码定义

类似 Spring Boot 的 ErrorCode 枚举
"""


class ResponseCode:
    """HTTP 响应状态码"""
    
    # ===== 成功 =====
    SUCCESS = 200
    
    # ===== 客户端错误 4xx =====
    BAD_REQUEST = 400          # 请求参数错误
    UNAUTHORIZED = 401         # 未授权
    FORBIDDEN = 403            # 禁止访问
    NOT_FOUND = 404            # 资源未找到
    
    # ===== 服务器错误 5xx =====
    INTERNAL_ERROR = 500       # 内部服务器错误
    SERVICE_UNAVAILABLE = 503  # 服务不可用
    
    # ===== Jenkins 业务错误码 5xxx =====
    JENKINS_CONNECTION_FAILED = 5001    # Jenkins 连接失败
    JENKINS_JOB_NOT_FOUND = 5002        # Job 不存在
    JENKINS_JOB_ALREADY_EXISTS = 5003   # Job 已存在
    JENKINS_XML_INVALID = 5004          # XML 格式无效
    JENKINS_BUILD_FAILED = 5005         # 构建失败
    JENKINS_OPERATION_FAILED = 5006     # Jenkins 操作失败


class ResponseMessage:
    """常用响应消息"""
    
    # ===== 成功消息 =====
    SUCCESS = "操作成功"
    
    # ===== 通用错误消息 =====
    PARAM_ERROR = "请求参数错误"
    PARAM_MISSING = "缺少必要参数"
    INTERNAL_ERROR = "服务器内部错误"
    
    # ===== Jenkins 相关消息 =====
    JENKINS_CONNECTED = "Jenkins 连接成功"
    JENKINS_CONNECTION_FAILED = "Jenkins 连接失败"
    
    CREATED = "创建成功"
    UPDATED = "更新成功"
    DELETED = "删除成功"
    
    JOB_CREATED = "Job 创建成功"
    JOB_UPDATED = "Job 更新成功"
    JOB_DELETED = "Job 删除成功"
    JOB_NOT_FOUND = "Job 不存在"
    JOB_ALREADY_EXISTS = "Job 已存在"
    
    XML_VALID = "XML 格式正确"
    XML_INVALID = "XML 格式错误"
    
    BUILD_TRIGGERED = "构建已触发"
    BUILD_FAILED = "构建失败"
