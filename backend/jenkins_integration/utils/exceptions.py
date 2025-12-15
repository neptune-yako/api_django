"""
自定义异常类

类似 Spring Boot 的自定义异常体系
"""


class JenkinsException(Exception):
    """Jenkins 相关异常基类"""
    
    def __init__(self, message="Jenkins 操作失败", code=5006):
        self.message = message
        self.code = code
        super().__init__(self.message)


class JenkinsConnectionException(JenkinsException):
    """Jenkins 连接异常"""
    
    def __init__(self, message="Jenkins 连接失败"):
        super().__init__(message, code=5001)


class JobNotFoundException(JenkinsException):
    """Job 不存在异常"""
    
    def __init__(self, job_name):
        message = f"Job [{job_name}] 不存在"
        super().__init__(message, code=5002)
        self.job_name = job_name


class JobAlreadyExistsException(JenkinsException):
    """Job 已存在异常"""
    
    def __init__(self, job_name):
        message = f"Job [{job_name}] 已存在"
        super().__init__(message, code=5003)
        self.job_name = job_name


class XMLValidationException(JenkinsException):
    """XML 校验异常"""
    
    def __init__(self, errors):
        message = "XML 格式错误"
        super().__init__(message, code=5004)
        self.errors = errors


class BuildException(JenkinsException):
    """构建异常"""
    
    def __init__(self, message="构建失败"):
        super().__init__(message, code=5005)


class JenkinsOperationException(JenkinsException):
    """Jenkins 操作异常（通用）"""
    
    def __init__(self, message="Jenkins 操作失败", original_exception=None):
        super().__init__(message, code=5006)
        self.original_exception = original_exception
