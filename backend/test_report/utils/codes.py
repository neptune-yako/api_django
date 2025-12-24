"""
测试报告模块响应码定义

定义 test_report 模块专用的业务错误码和消息
"""


class ReportResponseCode:
    """测试报告响应状态码"""
    
    # ===== 成功 =====
    SUCCESS = 200
    
    # ===== 客户端错误 4xx =====
    BAD_REQUEST = 400          # 请求参数错误
    NOT_FOUND = 404            # 资源未找到
    
    # ===== 服务器错误 5xx =====
    INTERNAL_ERROR = 500       # 内部服务器错误
    
    # ===== 测试报告业务错误码 6xxx =====
    REPORT_FETCH_FAILED = 6001        # 报告获取失败
    REPORT_PARSE_FAILED = 6002        # 报告解析失败
    REPORT_NOT_FOUND = 6003           # 报告不存在
    REPORT_ALREADY_EXISTS = 6004      # 报告已存在
    ALLURE_DATA_INVALID = 6005        # Allure 数据格式无效
    EXECUTION_NOT_FOUND = 6006        # 执行记录不存在
    SYNC_IN_PROGRESS = 6007           # 同步正在进行中


class ReportResponseMessage:
    """测试报告常用响应消息"""
    
    # ===== 成功消息 =====
    SUCCESS = "操作成功"
    SYNC_SUCCESS = "报告同步成功"
    FETCH_SUCCESS = "报告获取成功"
    
    # ===== 通用错误消息 =====
    PARAM_ERROR = "请求参数错误"
    PARAM_MISSING = "缺少必要参数"
    INTERNAL_ERROR = "服务器内部错误"
    
    # ===== 报告相关消息 =====
    REPORT_FETCHING = "正在获取报告数据"
    REPORT_FETCH_FAILED = "报告获取失败"
    REPORT_PARSE_FAILED = "报告解析失败"
    REPORT_NOT_FOUND = "报告不存在"
    REPORT_ALREADY_EXISTS = "报告已存在"
    
    ALLURE_DATA_INVALID = "Allure 数据格式无效"
    ALLURE_CONNECTION_FAILED = "无法连接到 Allure 报告服务"
    
    EXECUTION_NOT_FOUND = "执行记录不存在"
    EXECUTION_CREATED = "执行记录创建成功"
    
    SYNC_IN_PROGRESS = "同步正在进行中，请稍后"
    SYNC_COMPLETED = "同步已完成"
