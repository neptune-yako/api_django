"""
测试报告模块自定义异常类

定义 test_report 模块专用的异常体系
"""


class ReportException(Exception):
    """测试报告相关异常基类"""
    
    def __init__(self, message="测试报告操作失败", code=6000):
        self.message = message
        self.code = code
        super().__init__(self.message)


class ReportFetchException(ReportException):
    """报告获取异常"""
    
    def __init__(self, message="报告获取失败", job_name=None, build_number=None):
        super().__init__(message, code=6001)
        self.job_name = job_name
        self.build_number = build_number


class ReportParseException(ReportException):
    """报告解析异常"""
    
    def __init__(self, message="报告解析失败", file_path=None):
        super().__init__(message, code=6002)
        self.file_path = file_path


class ReportNotFoundException(ReportException):
    """报告不存在异常"""
    
    def __init__(self, execution_id=None):
        message = f"报告不存在 [ID: {execution_id}]" if execution_id else "报告不存在"
        super().__init__(message, code=6003)
        self.execution_id = execution_id


class ReportAlreadyExistsException(ReportException):
    """报告已存在异常"""
    
    def __init__(self, job_name, build_number):
        message = f"报告已存在 [Job: {job_name}, Build: {build_number}]"
        super().__init__(message, code=6004)
        self.job_name = job_name
        self.build_number = build_number


class AllureDataInvalidException(ReportException):
    """Allure 数据格式无效异常"""
    
    def __init__(self, message="Allure 数据格式无效", details=None):
        super().__init__(message, code=6005)
        self.details = details


class ExecutionNotFoundException(ReportException):
    """执行记录不存在异常"""
    
    def __init__(self, execution_id):
        message = f"执行记录不存在 [ID: {execution_id}]"
        super().__init__(message, code=6006)
        self.execution_id = execution_id


class SyncInProgressException(ReportException):
    """同步正在进行中异常"""
    
    def __init__(self, job_name, build_number):
        message = f"同步正在进行中 [Job: {job_name}, Build: {build_number}]"
        super().__init__(message, code=6007)
        self.job_name = job_name
        self.build_number = build_number
