# 全局工具函数，可以在测试用例前后置脚本中直接调用
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
