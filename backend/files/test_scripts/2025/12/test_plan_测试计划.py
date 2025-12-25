"""
测试计划: 测试计划
计划ID: 4
测试环境: b
"""

import pytest
import requests
import json
import re
from jsonpath import jsonpath
from requests_toolbelt import MultipartEncoder

# 环境配置
class ENV:
    """全局环境变量"""
    host = '47.113.217.26'
    headers = {}


# 临时环境变量(测试运行时使用)
env = {}

# 全局工具函数
# 全局工具函数，可以在测试用例的前置、断言脚本中直接调用
import base64
import hashlib
import time
# 生成各种伪数据的库
from faker import Faker

# 实例化，中文
fk = Faker(locale='zh_CN')


def mobile():
    """随机生成手机号"""
    return fk.phone_number()


def name():
    """随机生成中文名字"""
    return fk.name()


def address():
    """随机生成一个地址"""
    return fk.address()


def city():
    """随机生成一个城市名"""
    return fk.city()


def company():
    """随机生成一个公司名"""
    return fk.company()


def postcode():
    """随机生成一个邮编"""
    return fk.postcode()


def email():
    """随机生成一个邮箱号"""
    return fk.email()


def date():
    """随机生成一个日期1987-08-31"""
    return fk.date()


def date_time():
    """随机生成一个时间1988-12-11 01:35:30"""
    return fk.date_time()


def ipv4():
    """随机生成一个ipv4的地址18.63.34.130"""
    return fk.ipv4()


def timestamp():
    """生成当前时间戳1714358666.4879088"""
    return time.time()


def md5_encode(args):
    """md5加密，以指定的编码格式编码字符串"""
    # 先把变量转成utf-8的编码格式
    args = str(args).encode('utf-8')
    # md5加密
    args_value = hashlib.md5(args).hexdigest()
    # 返回
    return args_value


def base64_encode(args):
    """base64编码"""
    # 先把变量转成utf-8的编码格式
    args = str(args).encode('utf-8')
    # base64加密
    base64_value = base64.b64encode(args).decode(encoding='utf-8')
    # 返回
    return base64_value


def base64_decode(args):
    """base64解密"""
    # 原文转为二进制
    args = str(args).encode("utf-8")
    # base64解密(二进制)
    decode_value = base64.b64decode(args)
    # 转成字符串
    encode_str = decode_value.decode("utf-8")
    return encode_str


def sha1_encode(params):
    """参数sha1加密"""
    enc_data = hashlib.sha1()
    enc_data.update(params.encode(encoding="utf-8"))
    return enc_data.hexdigest()


def sha256_encode(params):
    """参数sha256加密"""
    enc_data = hashlib.sha256()
    enc_data.update(params.encode(encoding="utf-8"))
    return enc_data.hexdigest()


def sha512_encode(params):
    """参数sha512加密"""
    enc_data = hashlib.sha512()
    enc_data.update(params.encode(encoding="utf-8"))
    return enc_data.hexdigest()

class BaseTest:
    """测试基类,提供通用的测试方法"""
    
    session = requests.Session()
    
    @classmethod
    def send_request(cls, method, url, **kwargs):
        """发送HTTP请求"""
        full_url = ENV.host + url if not url.startswith("http") else url
        response = cls.session.request(method, full_url, **kwargs)
        return response
    
    @classmethod
    def replace_variables(cls, text):
        """替换文本中的变量引用 {{var}}"""
        if not isinstance(text, str):
            return text
        
        def replace_func(match):
            var_name = match.group(1)
            # 先从临时环境变量中查找
            if var_name in env:
                return str(env[var_name])
            # 再从全局环境变量中查找
            if hasattr(ENV, var_name):
                return str(getattr(ENV, var_name))
            return match.group(0)
        
        return re.sub(r'{{(.*?)}}', replace_func, text)
    
    @classmethod
    def replace_data(cls, data):
        """递归替换数据结构中的变量"""
        if isinstance(data, dict):
            return {k: cls.replace_data(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [cls.replace_data(item) for item in data]
        elif isinstance(data, str):
            return cls.replace_variables(data)
        return data

class Test1_login(BaseTest):
    """测试套件: login"""

    def test_1_true(self):
        """测试用例: true"""
        # 前置脚本

        # 发送请求
        method = 'POST'
        url = 'https://coffeeend.morry.online/auth/login'
        headers = {
        "accept": "application/json",
        "Content-Type": "application/json"
}
        headers = self.replace_data(headers)
        request_data = {
        "json": {
                "password": "123456",
                "username": "test"
        }
}
        request_data = self.replace_data(request_data)
        # 判断Content-Type来决定发送方式
        content_type = headers.get("Content-Type", "")
        if "application/json" in content_type:
            response = self.send_request(method, url, headers=headers, json=request_data)
        else:
            response = self.send_request(method, url, headers=headers, data=request_data)

        # 断言脚本

    def test_2_false(self):
        """测试用例: false"""
        # 前置脚本

        # 发送请求
        method = 'POST'
        url = 'https://coffeeend.morry.online/auth/login'
        headers = {
        "accept": "application/json",
        "Content-Type": "application/json"
}
        headers = self.replace_data(headers)
        request_data = {
        "json": {
                "password": "123",
                "username": "test"
        }
}
        request_data = self.replace_data(request_data)
        # 判断Content-Type来决定发送方式
        content_type = headers.get("Content-Type", "")
        if "application/json" in content_type:
            response = self.send_request(method, url, headers=headers, json=request_data)
        else:
            response = self.send_request(method, url, headers=headers, data=request_data)

        # 断言脚本

