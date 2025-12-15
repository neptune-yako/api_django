"""
统一响应封装类

类似 Spring Boot 的 R<T> 通用响应类
提供统一的 API 响应格式
"""
from rest_framework.response import Response
from rest_framework import status as http_status
from .codes import ResponseCode, ResponseMessage


class R:
    """
    统一响应类
    
    类似 Spring Boot 的:
    @Data
    public class R<T> {
        private int code;
        private String message;
        private T data;
    }
    
    使用示例:
        # 成功响应
        return R.success(data={'user': 'akko'})
        return R.success(message="创建成功", data={'id': 123})
        
        # 失败响应
        return R.error(message="参数错误")
        return R.error(code=ResponseCode.NOT_FOUND, message="资源不存在")
    """
    
    @staticmethod
    def success(message=None, data=None, code=None):
        """
        成功响应
        
        Args:
            message: 响应消息，默认 "操作成功"
            data: 响应数据
            code: 响应码，默认 200
            
        Returns:
            Response: DRF Response 对象
        """
        return Response({
            'code': code or ResponseCode.SUCCESS,
            'message': message or ResponseMessage.SUCCESS,
            'data': data
        }, status=http_status.HTTP_200_OK)
    
    @staticmethod
    def error(message=None, code=None, data=None, http_code=None):
        """
        失败响应
        
        Args:
            message: 错误消息，默认 "服务器内部错误"
            code: 业务错误码，默认 500
            data: 额外数据（如错误详情）
            http_code: HTTP 状态码，默认根据 code 自动判断
            
        Returns:
            Response: DRF Response 对象
        """
        business_code = code or ResponseCode.INTERNAL_ERROR
        
        # 根据业务错误码自动判断 HTTP 状态码
        if http_code is None:
            if business_code == ResponseCode.BAD_REQUEST or 5000 <= business_code < 5100:
                http_code = http_status.HTTP_400_BAD_REQUEST
            elif business_code == ResponseCode.NOT_FOUND:
                http_code = http_status.HTTP_404_NOT_FOUND
            elif business_code == ResponseCode.UNAUTHORIZED:
                http_code = http_status.HTTP_401_UNAUTHORIZED
            elif business_code == ResponseCode.FORBIDDEN:
                http_code = http_status.HTTP_403_FORBIDDEN
            else:
                http_code = http_status.HTTP_500_INTERNAL_SERVER_ERROR
        
        return Response({
            'code': business_code,
            'message': message or ResponseMessage.INTERNAL_ERROR,
            'data': data
        }, status=http_code)
    
    @staticmethod
    def bad_request(message=None, data=None):
        """400 请求参数错误"""
        return R.error(
            message=message or ResponseMessage.PARAM_ERROR,
            code=ResponseCode.BAD_REQUEST,
            data=data
        )
    
    @staticmethod
    def not_found(message=None, data=None):
        """404 资源不存在"""
        return R.error(
            message=message or "资源不存在",
            code=ResponseCode.NOT_FOUND,
            data=data
        )
    
    @staticmethod
    def internal_error(message=None, data=None):
        """500 服务器内部错误"""
        return R.error(
            message=message or ResponseMessage.INTERNAL_ERROR,
            code=ResponseCode.INTERNAL_ERROR,
            data=data
        )
    
    @staticmethod
    def jenkins_error(message, code=None, data=None):
        """Jenkins 相关错误"""
        return R.error(
            message=message,
            code=code or ResponseCode.JENKINS_OPERATION_FAILED,
            data=data
        )


class ApiResponse:
    """
    API 响应助手类（可选）
    
    提供更多便捷方法
    """
    
    @staticmethod
    def paginate(data, total, page=1, page_size=10, message="查询成功"):
        """
        分页响应
        
        Args:
            data: 当前页数据列表
            total: 总记录数
            page: 当前页码
            page_size: 每页大小
            message: 响应消息
        """
        return R.success(
            message=message,
            data={
                'list': data,
                'total': total,
                'page': page,
                'page_size': page_size,
                'total_pages': (total + page_size - 1) // page_size
            }
        )
    
    @staticmethod
    def created(message="创建成功", data=None):
        """创建资源成功（201）"""
        return Response({
            'code': ResponseCode.SUCCESS,
            'message': message,
            'data': data
        }, status=http_status.HTTP_201_CREATED)
    
    @staticmethod
    def no_content(message="删除成功"):
        """无内容响应（204）"""
        return Response({
            'code': ResponseCode.SUCCESS,
            'message': message,
            'data': None
        }, status=http_status.HTTP_204_NO_CONTENT)
