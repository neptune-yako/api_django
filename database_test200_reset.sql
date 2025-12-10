# Test管理接口自动化测试数据 - 完整重置脚本
# 说明：先删除ID=200的所有数据（如果存在），然后重新创建
# 如果数据不存在则自动跳过，不会报错

# ============================================
# 第一部分：删除旧数据（按依赖关系逆序删除）
# ============================================

# 删除测试计划关联的测试套件
DELETE FROM `plan_scene` WHERE `id` = 200;

# 删除测试计划
DELETE FROM `plan` WHERE `id` = 200;

# 删除测试套件下的测试用例（步骤）
DELETE FROM `step` WHERE `id` IN (200, 201, 202, 203, 204, 205, 206, 207, 208);

# 删除测试套件
DELETE FROM `scene` WHERE `id` = 200;

# 删除测试用例
DELETE FROM `case` WHERE `id` IN (200, 201, 202, 203, 204, 205, 206, 207, 208);

# 删除测试接口
DELETE FROM `interface` WHERE `id` IN (200, 201, 202, 203, 204, 205, 206, 207, 208);

# 删除测试环境
DELETE FROM `environment` WHERE `id` = 200;

# 删除测试项目
DELETE FROM `project` WHERE `id` = 200;

# 删除测试用户（可选，如果不想删除用户可以注释掉这一行）
DELETE FROM `user` WHERE `id` = 200;

# ============================================
# 第二部分：重新创建数据
# ============================================

# 添加用户admin/123456（如果已存在则跳过）
INSERT INTO `user` (`id`, `password`, `last_login`, `is_superuser`, `username`, `first_name`, `last_name`, `email`, `is_staff`, `is_active`, `date_joined`, `mobile`, `nickname`, `update_time`) VALUES (200, 'pbkdf2_sha256$870000$eiOmrq3jZ9DkWHw1T7M0C4$UcifOYW+o58jfIVGsk8ihdejjkOaDW35tVTaaS7XZ+I=', '2025-12-08 18:20:00.000000', 1, 'testuser', '', '', 'testuser@example.com', 1, 1, '2025-12-08 18:20:00.000000', '13900139000', '测试用户', '2025-12-08 18:20:00.000000');
# 添加测试项目
INSERT INTO `project` (`id`, `name`, `username`, `create_time`, `update_time`) VALUES (200, 'Test管理接口测试项目', 'testuser', '2025-12-08 18:20:00.000000', '2025-12-08 18:20:00.000000');
# 添加测试环境，其中包含了数据库的配置，需要修改成自己的数据库
INSERT INTO `environment` (`id`, `global_variable`, `debug_global_variable`, `db`, `headers`, `global_func`, `name`, `host`, `create_time`, `project_id`, `username`, `update_time`) VALUES (200, '{}', '{\"test_id\": \"\"}', '[{\"name\": \"library_db\", \"type\": \"mysql\", \"config\": {\"host\": \"127.0.0.1\", \"port\": 3306, \"user\": \"root\", \"database\": \"library_management\", \"password\": \"123456\"}}]', '{\"Content-Type\": \"application/json\"}', '# 全局工具函数，可以在测试用例的前置、断言脚本中直接调用\nimport base64\nimport hashlib\nimport time\n# 生成各种各样的伪数据的库\nfrom faker import Faker\n\n# 实例化，生成中文的随机数\nfk = Faker(locale=\'zh_CN\')\n\n\ndef mobile():\n    \"\"\"随机生成手机号\"\"\"\n    return fk.phone_number()\n\n\ndef name():\n    \"\"\"随机生成中文名字\"\"\"\n    return fk.name()\n\n\ndef address():\n    \"\"\"随机生成一个地址\"\"\"\n    return fk.address()\n\n\ndef city():\n    \"\"\"随机生成一个城市名\"\"\"\n    return fk.city()\n\n\ndef company():\n    \"\"\"随机生成一个公司名\"\"\"\n    return fk.company()\n\n\ndef postcode():\n    \"\"\"随机生成一个邮编\"\"\"\n    return fk.postcode()\n\n\ndef email():\n    \"\"\"随机生成一个邮箱号\"\"\"\n    return fk.email()\n\n\ndef date():\n    \"\"\"随机生成一个日期1987-08-31\"\"\"\n    return fk.date()\n\n\ndef date_time():\n    \"\"\"随机生成一个时间1988-12-11 01:35:30\"\"\"\n    return fk.date_time()\n\n\ndef ipv4():\n    \"\"\"随机生成一个ipv4的地址18.63.34.130\"\"\"\n    return fk.ipv4()\n\n\ndef timestamp():\n    \"\"\"生成当前时间戳1714358666.4879088\"\"\"\n    return time.time()\n\n\ndef md5_encode(args):\n    \"\"\"md5加密，以指定的编码格式编码字符串\"\"\"\n    # 先把变量转成utf-8的编码格式\n    args = str(args).encode(\'utf-8\')\n    # md5加密\n    args_value = hashlib.md5(args).hexdigest()\n    # 返回\n    return args_value\n\n\ndef base64_encode(args):\n    \"\"\"base64编码\"\"\"\n    # 先把变量转成utf-8的编码格式\n    args = str(args).encode(\'utf-8\')\n    # base64加密\n    base64_value = base64.b64encode(args).decode(encoding=\'utf-8\')\n    # 返回\n    return base64_value\n\n\ndef base64_decode(args):\n    \"\"\"base64解密\"\"\"\n    # 原文转为二进制\n    args = str(args).encode(\"utf-8\")\n    # base64解密(二进制)\n    decode_value = base64.b64decode(args)\n    # 转成字符串\n    encode_str = decode_value.decode(\"utf-8\")\n    return encode_str\n\n\ndef sha1_encode(params):\n    \"\"\"参数sha1加密\"\"\"\n    enc_data = hashlib.sha1()\n    enc_data.update(params.encode(encoding=\"utf-8\"))\n    return enc_data.hexdigest()\n\n\ndef sha256_encode(params):\n    \"\"\"参数sha256加密\"\"\"\n    enc_data = hashlib.sha256()\n    enc_data.update(params.encode(encoding=\"utf-8\"))\n    return enc_data.hexdigest()\n\n\ndef sha512_encode(params):\n    \"\"\"参数sha512加密\"\"\"\n    enc_data = hashlib.sha512()\n    enc_data.update(params.encode(encoding=\"utf-8\"))\n    return enc_data.hexdigest()', '本地测试环境', 'http://localhost:8082', '2025-12-08 18:20:00.000000', 200, 'testuser', '2025-12-08 18:20:00.000000');
# 添加测试接口
INSERT INTO `interface` (`id`, `name`, `url`, `method`, `create_time`, `project_id`, `username`, `update_time`) VALUES (200, '连通性测试-GET', '/api/test/lianjie', 'GET', '2025-12-08 18:20:00.000000', 200, 'testuser', '2025-12-08 18:20:00.000000');
INSERT INTO `interface` (`id`, `name`, `url`, `method`, `create_time`, `project_id`, `username`, `update_time`) VALUES (206, '连通性测试-POST', '/api/test/lianjie', 'POST', '2025-12-08 18:20:00.000000', 200, 'testuser', '2025-12-08 18:20:00.000000');
INSERT INTO `interface` (`id`, `name`, `url`, `method`, `create_time`, `project_id`, `username`, `update_time`) VALUES (207, '连通性测试-PUT', '/api/test/lianjie', 'PUT', '2025-12-08 18:20:00.000000', 200, 'testuser', '2025-12-08 18:20:00.000000');
INSERT INTO `interface` (`id`, `name`, `url`, `method`, `create_time`, `project_id`, `username`, `update_time`) VALUES (208, '连通性测试-DELETE', '/api/test/lianjie', 'DELETE', '2025-12-08 18:20:00.000000', 200, 'testuser', '2025-12-08 18:20:00.000000');
INSERT INTO `interface` (`id`, `name`, `url`, `method`, `create_time`, `project_id`, `username`, `update_time`) VALUES (201, '创建Test', '/api/test', 'POST', '2025-12-08 18:20:00.000000', 200, 'testuser', '2025-12-08 18:20:00.000000');
INSERT INTO `interface` (`id`, `name`, `url`, `method`, `create_time`, `project_id`, `username`, `update_time`) VALUES (202, '获取所有Test', '/api/test', 'GET', '2025-12-08 18:20:00.000000', 200, 'testuser', '2025-12-08 18:20:00.000000');
INSERT INTO `interface` (`id`, `name`, `url`, `method`, `create_time`, `project_id`, `username`, `update_time`) VALUES (203, '根据ID获取Test', '/api/test/${{test_id}}', 'GET', '2025-12-08 18:20:00.000000', 200, 'testuser', '2025-12-08 18:20:00.000000');
INSERT INTO `interface` (`id`, `name`, `url`, `method`, `create_time`, `project_id`, `username`, `update_time`) VALUES (204, '更新Test', '/api/test', 'PUT', '2025-12-08 18:20:00.000000', 200, 'testuser', '2025-12-08 18:20:00.000000');
INSERT INTO `interface` (`id`, `name`, `url`, `method`, `create_time`, `project_id`, `username`, `update_time`) VALUES (205, '删除Test', '/api/test/${{test_id}}', 'DELETE', '2025-12-08 18:20:00.000000', 200, 'testuser', '2025-12-08 18:20:00.000000');
# 添加测试用例
INSERT INTO `case` (`id`, `title`, `headers`, `request`, `file`, `setup_script`, `teardown_script`, `create_time`, `interface_id`, `username`, `update_time`) VALUES (200, '测试连接-GET', '{}', '{\"json\": {}, \"params\": {}}', '[]', '# 前置脚本(python)\n# global_func：全局工具函数\n# data：用例数据\n# env：临时环境\n# ENV：全局环境\n# db：数据库操作对象', '# 断言脚本(python)\n# global_func：全局工具函数\n# data：用例数据\n# response：响应对象response\n# env：临时环境\n# ENV：全局环境\n# db：数据库操作对象\n\n# http状态码是否为200\ntest.assertion(\"相等\",200,response.status_code)\n\n# 验证响应消息\ntest.assertion(\"包含\",\"连接成功\",response.text)', '2025-12-08 18:20:00.000000', 200, 'testuser', '2025-12-08 18:20:00.000000');
INSERT INTO `case` (`id`, `title`, `headers`, `request`, `file`, `setup_script`, `teardown_script`, `create_time`, `interface_id`, `username`, `update_time`) VALUES (206, '测试连接-POST', '{}', '{\"json\": {}, \"params\": {}}', '[]', '# 前置脚本(python)\n# global_func：全局工具函数\n# data：用例数据\n# env：临时环境\n# ENV：全局环境\n# db：数据库操作对象', '# 断言脚本(python)\n# global_func：全局工具函数\n# data：用例数据\n# response：响应对象response\n# env：临时环境\n# ENV：全局环境\n# db：数据库操作对象\n\n# http状态码是否为200\ntest.assertion(\"相等\",200,response.status_code)\n\n# 验证响应消息\ntest.assertion(\"包含\",\"连接成功\",response.text)', '2025-12-08 18:20:00.000000', 206, 'testuser', '2025-12-08 18:20:00.000000');
INSERT INTO `case` (`id`, `title`, `headers`, `request`, `file`, `setup_script`, `teardown_script`, `create_time`, `interface_id`, `username`, `update_time`) VALUES (207, '测试连接-PUT', '{}', '{\"json\": {}, \"params\": {}}', '[]', '# 前置脚本(python)\n# global_func：全局工具函数\n# data：用例数据\n# env：临时环境\n# ENV：全局环境\n# db：数据库操作对象', '# 断言脚本(python)\n# global_func：全局工具函数\n# data：用例数据\n# response：响应对象response\n# env：临时环境\n# ENV：全局环境\n# db：数据库操作对象\n\n# http状态码是否为200\ntest.assertion(\"相等\",200,response.status_code)\n\n# 验证响应消息\ntest.assertion(\"包含\",\"连接成功\",response.text)', '2025-12-08 18:20:00.000000', 207, 'testuser', '2025-12-08 18:20:00.000000');
INSERT INTO `case` (`id`, `title`, `headers`, `request`, `file`, `setup_script`, `teardown_script`, `create_time`, `interface_id`, `username`, `update_time`) VALUES (208, '测试连接-DELETE', '{}', '{\"json\": {}, \"params\": {}}', '[]', '# 前置脚本(python)\n# global_func：全局工具函数\n# data：用例数据\n# env：临时环境\n# ENV：全局环境\n# db：数据库操作对象', '# 断言脚本(python)\n# global_func：全局工具函数\n# data：用例数据\n# response：响应对象response\n# env：临时环境\n# ENV：全局环境\n# db：数据库操作对象\n\n# http状态码是否为200\ntest.assertion(\"相等\",200,response.status_code)\n\n# 验证响应消息\ntest.assertion(\"包含\",\"连接成功\",response.text)', '2025-12-08 18:20:00.000000', 208, 'testuser', '2025-12-08 18:20:00.000000');
INSERT INTO `case` (`id`, `title`, `headers`, `request`, `file`, `setup_script`, `teardown_script`, `create_time`, `interface_id`, `username`, `update_time`) VALUES (201, '正常创建Test记录', '{\"Content-Type\": \"application/json\"}', '{\"json\": {\"name\": \"测试数据${{timestamp}}\", \"description\": \"这是一条测试数据\"}, \"params\": {}}', '[]', '# 前置脚本(python)\n# global_func：全局工具函数\n# data：用例数据\n# env：临时环境\n# ENV：全局环境\n# db：数据库操作对象\n\n# 生成时间戳作为唯一标识\ntimestamp = int(global_func.timestamp())\ntest.save_env_variable(\"timestamp\", timestamp)', '# 断言脚本(python)\n# global_func：全局工具函数\n# data：用例数据\n# response：响应对象response\n# env：临时环境\n# ENV：全局环境\n# db：数据库操作对象\n\n# http状态码是否为200\ntest.assertion(\"相等\",200,response.status_code)\n\n# 提取返回的ID\ntest_id = test.json_extract(response.json(),\"$..data.id\")\ntest.save_env_variable(\"test_id\",test_id)\n\n# 验证创建成功\ntest.assertion(\"包含\",\"ok\",response.text)', '2025-12-08 18:20:00.000000', 201, 'testuser', '2025-12-08 18:20:00.000000');
INSERT INTO `case` (`id`, `title`, `headers`, `request`, `file`, `setup_script`, `teardown_script`, `create_time`, `interface_id`, `username`, `update_time`) VALUES (202, '获取所有Test记录', '{}', '{\"json\": {}, \"params\": {}}', '[]', '# 前置脚本(python)\n# global_func：全局工具函数\n# data：用例数据\n# env：临时环境\n# ENV：全局环境\n# db：数据库操作对象', '# 断言脚本(python)\n# global_func：全局工具函数\n# data：用例数据\n# response：响应对象response\n# env：临时环境\n# ENV：全局环境\n# db：数据库操作对象\n\n# http状态码是否为200\ntest.assertion(\"相等\",200,response.status_code)\n\n# 验证返回了数据列表\ntest.assertion(\"包含\",\"data\",response.text)', '2025-12-08 18:20:00.000000', 202, 'testuser', '2025-12-08 18:20:00.000000');
INSERT INTO `case` (`id`, `title`, `headers`, `request`, `file`, `setup_script`, `teardown_script`, `create_time`, `interface_id`, `username`, `update_time`) VALUES (203, '根据ID获取Test记录', '{}', '{\"json\": {}, \"params\": {}}', '[]', '# 前置脚本(python)\n# global_func：全局工具函数\n# data：用例数据\n# env：临时环境\n# ENV：全局环境\n# db：数据库操作对象', '# 断言脚本(python)\n# global_func：全局工具函数\n# data：用例数据\n# response：响应对象response\n# env：临时环境\n# ENV：全局环境\n# db：数据库操作对象\n\n# http状态码是否为200\ntest.assertion(\"相等\",200,response.status_code)\n\n# 验证返回了指定ID的数据\ntest.assertion(\"包含\",\"data\",response.text)', '2025-12-08 18:20:00.000000', 203, 'testuser', '2025-12-08 18:20:00.000000');
INSERT INTO `case` (`id`, `title`, `headers`, `request`, `file`, `setup_script`, `teardown_script`, `create_time`, `interface_id`, `username`, `update_time`) VALUES (204, '更新Test记录', '{\"Content-Type\": \"application/json\"}', '{\"json\": {\"id\": \"${{test_id}}\", \"name\": \"更新后的名称\", \"description\": \"这是更新后的描述\"}, \"params\": {}}', '[]', '# 前置脚本(python)\n# global_func：全局工具函数\n# data：用例数据\n# env：临时环境\n# ENV：全局环境\n# db：数据库操作对象', '# 断言脚本(python)\n# global_func：全局工具函数\n# data：用例数据\n# response：响应对象response\n# env：临时环境\n# ENV：全局环境\n# db：数据库操作对象\n\n# http状态码是否为200\ntest.assertion(\"相等\",200,response.status_code)\n\n# 验证更新成功\ntest.assertion(\"包含\",\"ok\",response.text)', '2025-12-08 18:20:00.000000', 204, 'testuser', '2025-12-08 18:20:00.000000');
INSERT INTO `case` (`id`, `title`, `headers`, `request`, `file`, `setup_script`, `teardown_script`, `create_time`, `interface_id`, `username`, `update_time`) VALUES (205, '删除Test记录', '{}', '{\"json\": {}, \"params\": {}}', '[]', '# 前置脚本(python)\n# global_func：全局工具函数\n# data：用例数据\n# env：临时环境\n# ENV：全局环境\n# db：数据库操作对象', '# 断言脚本(python)\n# global_func：全局工具函数\n# data：用例数据\n# response：响应对象response\n# env：临时环境\n# ENV：全局环境\n# db：数据库操作对象\n\n# http状态码是否为200\ntest.assertion(\"相等\",200,response.status_code)\n\n# 验证删除成功\ntest.assertion(\"包含\",\"删除成功\",response.text)', '2025-12-08 18:20:00.000000', 205, 'testuser', '2025-12-08 18:20:00.000000');
# 添加测试套件
INSERT INTO `scene` (`id`, `name`, `create_time`, `username`, `project_id`, `update_time`) VALUES (200, 'Test管理完整流程测试套件', '2025-12-08 18:20:00.000000', 'testuser', 200, '2025-12-08 18:20:00.000000');
# 添加测试套件下的测试用例
INSERT INTO `step` (`id`, `sort`, `create_time`, `icase_id`, `scene_id`, `update_time`) VALUES (200, 1, '2025-12-08 18:20:00.000000', 200, 200, '2025-12-08 18:20:00.000000');
INSERT INTO `step` (`id`, `sort`, `create_time`, `icase_id`, `scene_id`, `update_time`) VALUES (201, 2, '2025-12-08 18:20:00.000000', 201, 200, '2025-12-08 18:20:00.000000');
INSERT INTO `step` (`id`, `sort`, `create_time`, `icase_id`, `scene_id`, `update_time`) VALUES (202, 3, '2025-12-08 18:20:00.000000', 202, 200, '2025-12-08 18:20:00.000000');
INSERT INTO `step` (`id`, `sort`, `create_time`, `icase_id`, `scene_id`, `update_time`) VALUES (203, 4, '2025-12-08 18:20:00.000000', 203, 200, '2025-12-08 18:20:00.000000');
INSERT INTO `step` (`id`, `sort`, `create_time`, `icase_id`, `scene_id`, `update_time`) VALUES (204, 5, '2025-12-08 18:20:00.000000', 204, 200, '2025-12-08 18:20:00.000000');
INSERT INTO `step` (`id`, `sort`, `create_time`, `icase_id`, `scene_id`, `update_time`) VALUES (205, 6, '2025-12-08 18:20:00.000000', 205, 200, '2025-12-08 18:20:00.000000');
INSERT INTO `step` (`id`, `sort`, `create_time`, `icase_id`, `scene_id`, `update_time`) VALUES (206, 7, '2025-12-08 18:20:00.000000', 206, 200, '2025-12-08 18:20:00.000000');
INSERT INTO `step` (`id`, `sort`, `create_time`, `icase_id`, `scene_id`, `update_time`) VALUES (207, 8, '2025-12-08 18:20:00.000000', 207, 200, '2025-12-08 18:20:00.000000');
INSERT INTO `step` (`id`, `sort`, `create_time`, `icase_id`, `scene_id`, `update_time`) VALUES (208, 9, '2025-12-08 18:20:00.000000', 208, 200, '2025-12-08 18:20:00.000000');
# 添加测试计划
INSERT INTO `plan` (`id`, `name`, `create_time`, `username`, `project_id`, `update_time`) VALUES (200, 'Test管理接口自动化测试计划', '2025-12-08 18:20:00.000000', 'testuser', 200, '2025-12-08 18:20:00.000000');
# 添加测试计划下的测试套件
INSERT INTO `plan_scene` (`id`, `plan_id`, `scene_id`) VALUES (200, 200, 200);

# ============================================
# 执行完成
# ============================================
# 说明：
# 1. 已删除所有ID=200相关的数据
# 2. 已重新创建完整的测试数据
# 3. 如果数据不存在，DELETE语句会自动跳过，不会报错
