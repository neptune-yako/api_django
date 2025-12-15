"""
Jenkins Integration Utils

统一响应、错误码、异常等工具类
"""
from .response import R, ApiResponse
from .codes import ResponseCode, ResponseMessage
from .exceptions import (
    JenkinsException,
    JenkinsConnectionException,
    JobNotFoundException,
    JobAlreadyExistsException,
    XMLValidationException,
    BuildException,
    JenkinsOperationException
)

__all__ = [
    # 响应类
    'R',
    'ApiResponse',
    
    # 错误码
    'ResponseCode',
    'ResponseMessage',
    
    # 异常类
    'JenkinsException',
    'JenkinsConnectionException',
    'JobNotFoundException',
    'JobAlreadyExistsException',
    'XMLValidationException',
    'BuildException',
    'JenkinsOperationException',
]
