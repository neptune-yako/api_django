"""
P0 功能测试数据生成脚本

使用方法:
1. cd d:\data\xianYu\test_django\api_django\backend
2. python manage.py shell
3. 复制粘贴本脚本内容并执行

或者:
1. python manage.py shell < create_test_data.py
"""

from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from jenkins_integration.models import JenkinsServer, JenkinsJob
from test_report.models import TestExecution, TestSuite, TestSuiteDetail, Category, FeatureScenario

print("🚀 开始创建测试数据...")

# ==================== 1. 创建 Jenkins Server ====================
server, created = JenkinsServer.objects.get_or_create(
    name="测试服务器",
    defaults={
        'url': 'http://localhost:8080',
        'username': 'admin',
        'token': 'test_token_123456',
        'is_active': True,
        'description': '用于 P0 功能测试的 Jenkins 服务器',
        'connection_status': 'connected',
        'created_by': 'admin'
    }
)
print(f"{'✅ 创建' if created else '✅ 已存在'} Jenkins Server: {server.name}")

# ==================== 2. 创建 Jenkins Job ====================
job, created = JenkinsJob.objects.get_or_create(
    server=server,
    name="AutoTest_Demo_Job",
    defaults={
        'display_name': '自动化测试示例任务',
        'description': '用于演示 P0 功能的测试任务',
        'is_active': True,
        'is_buildable': True,
        'job_type': 'freestyle',
        'last_build_number': 42,
        'last_build_status': 'SUCCESS',
        'created_by': 'admin'
    }
)
print(f"{'✅ 创建' if created else '✅ 已存在'} Jenkins Job: {job.name}")

# ==================== 3. 创建 TestExecution ====================
now = timezone.now()
start_time = now - timedelta(minutes=15)
end_time = now - timedelta(minutes=5)

execution, created = TestExecution.objects.get_or_create(
    timestamp=str(int(now.timestamp())),
    defaults={
        'job': job,
        'report_title': '自动化测试报告 - P0 功能演示',
        'total_cases': 15,
        'passed_cases': 12,
        'failed_cases': 2,
        'skipped_cases': 1,
        'broken_cases': 0,
        'unknown_cases': 0,
        'pass_rate': Decimal('80.00'),
        'min_duration': 500,
        'max_duration': 3000,
        'sum_duration': 25000,
        'execution_time': '10分15秒',
        'start_time': start_time,
        'end_time': end_time,
        'status': 'success'
    }
)
print(f"{'✅ 创建' if created else '✅ 已存在'} TestExecution: {execution.report_title}")

# ==================== 4. 创建 TestSuite (3个套件) ====================
suites_data = [
    {
        'suite_name': 'LoginSuite',
        'total_cases': 5,
        'passed_cases': 3,
        'failed_cases': 2,
        'skipped_cases': 0,
        'broken_cases': 0,
        'pass_rate': Decimal('60.00'),
        'duration_seconds': Decimal('8.500')
    },
    {
        'suite_name': 'PaymentSuite',
        'total_cases': 5,
        'passed_cases': 5,
        'failed_cases': 0,
        'skipped_cases': 0,
        'broken_cases': 0,
        'pass_rate': Decimal('100.00'),
        'duration_seconds': Decimal('12.300')
    },
    {
        'suite_name': 'UserManagementSuite',
        'total_cases': 5,
        'passed_cases': 4,
        'failed_cases': 0,
        'skipped_cases': 1,
        'broken_cases': 0,
        'pass_rate': Decimal('80.00'),
        'duration_seconds': Decimal('6.800')
    }
]

suites = []
for suite_data in suites_data:
    suite, created = TestSuite.objects.get_or_create(
        execution=execution,
        suite_name=suite_data['suite_name'],
        defaults=suite_data
    )
    suites.append(suite)
    print(f"  {'✅ 创建' if created else '✅ 已存在'} Suite: {suite.suite_name}")

# ==================== 5. 创建 TestSuiteDetail (15个用例) ====================
# 关键: parent_suite 必须与 TestSuite.suite_name 一致!
cases_data = [
    # LoginSuite - 5个用例 (3通过, 2失败)
    {
        'name': 'test_login_success',
        'description': '验证使用正确的用户名和密码登录成功',
        'parent_suite': 'LoginSuite',
        'suite': 'UserAuth',
        'sub_suite': 'LoginTests',
        'test_class': 'TestLogin',
        'test_method': 'test_login_success',
        'status': 'passed',
        'duration_in_ms': Decimal('1200.500')
    },
    {
        'name': 'test_login_invalid_password',
        'description': '验证使用错误密码登录失败',
        'parent_suite': 'LoginSuite',
        'suite': 'UserAuth',
        'sub_suite': 'LoginTests',
        'test_class': 'TestLogin',
        'test_method': 'test_login_invalid_password',
        'status': 'failed',
        'duration_in_ms': Decimal('850.300')
    },
    {
        'name': 'test_login_empty_username',
        'description': '验证空用户名时登录失败',
        'parent_suite': 'LoginSuite',
        'suite': 'UserAuth',
        'sub_suite': 'LoginTests',
        'test_class': 'TestLogin',
        'test_method': 'test_login_empty_username',
        'status': 'failed',
        'duration_in_ms': Decimal('650.200')
    },
    {
        'name': 'test_logout',
        'description': '验证用户登出功能',
        'parent_suite': 'LoginSuite',
        'suite': 'UserAuth',
        'sub_suite': 'LoginTests',
        'test_class': 'TestLogin',
        'test_method': 'test_logout',
        'status': 'passed',
        'duration_in_ms': Decimal('500.100')
    },
    {
        'name': 'test_remember_me',
        'description': '验证记住我功能',
        'parent_suite': 'LoginSuite',
        'suite': 'UserAuth',
        'sub_suite': 'LoginTests',
        'test_class': 'TestLogin',
        'test_method': 'test_remember_me',
        'status': 'passed',
        'duration_in_ms': Decimal('1100.400')
    },
    
    # PaymentSuite - 5个用例 (全部通过)
    {
        'name': 'test_payment_credit_card',
        'description': '验证信用卡支付流程',
        'parent_suite': 'PaymentSuite',
        'suite': 'Payment',
        'sub_suite': 'CreditCardTests',
        'test_class': 'TestPayment',
        'test_method': 'test_payment_credit_card',
        'status': 'passed',
        'duration_in_ms': Decimal('2500.800')
    },
    {
        'name': 'test_payment_alipay',
        'description': '验证支付宝支付流程',
        'parent_suite': 'PaymentSuite',
        'suite': 'Payment',
        'sub_suite': 'AlipayTests',
        'test_class': 'TestPayment',
        'test_method': 'test_payment_alipay',
        'status': 'passed',
        'duration_in_ms': Decimal('2800.600')
    },
    {
        'name': 'test_payment_wechat',
        'description': '验证微信支付流程',
        'parent_suite': 'PaymentSuite',
        'suite': 'Payment',
        'sub_suite': 'WechatTests',
        'test_class': 'TestPayment',
        'test_method': 'test_payment_wechat',
        'status': 'passed',
        'duration_in_ms': Decimal('2600.700')
    },
    {
        'name': 'test_refund',
        'description': '验证退款功能',
        'parent_suite': 'PaymentSuite',
        'suite': 'Payment',
        'sub_suite': 'RefundTests',
        'test_class': 'TestPayment',
        'test_method': 'test_refund',
        'status': 'passed',
        'duration_in_ms': Decimal('1900.500')
    },
    {
        'name': 'test_payment_timeout',
        'description': '验证支付超时处理',
        'parent_suite': 'PaymentSuite',
        'suite': 'Payment',
        'sub_suite': 'TimeoutTests',
        'test_class': 'TestPayment',
        'test_method': 'test_payment_timeout',
        'status': 'passed',
        'duration_in_ms': Decimal('2500.700')
    },
    
    # UserManagementSuite - 5个用例 (4通过, 1跳过)
    {
        'name': 'test_user_registration',
        'description': '验证用户注册功能',
        'parent_suite': 'UserManagementSuite',
        'suite': 'UserManagement',
        'sub_suite': 'RegistrationTests',
        'test_class': 'TestUserManagement',
        'test_method': 'test_user_registration',
        'status': 'passed',
        'duration_in_ms': Decimal('1500.300')
    },
    {
        'name': 'test_user_profile_update',
        'description': '验证用户资料更新',
        'parent_suite': 'UserManagementSuite',
        'suite': 'UserManagement',
        'sub_suite': 'ProfileTests',
        'test_class': 'TestUserManagement',
        'test_method': 'test_user_profile_update',
        'status': 'skipped',
        'duration_in_ms': Decimal('0.000')
    },
    {
        'name': 'test_password_change',
        'description': '验证密码修改功能',
        'parent_suite': 'UserManagementSuite',
        'suite': 'UserManagement',
        'sub_suite': 'SecurityTests',
        'test_class': 'TestUserManagement',
        'test_method': 'test_password_change',
        'status': 'passed',
        'duration_in_ms': Decimal('1200.600')
    },
    {
        'name': 'test_user_deletion',
        'description': '验证用户删除功能',
        'parent_suite': 'UserManagementSuite',
        'suite': 'UserManagement',
        'sub_suite': 'DeletionTests',
        'test_class': 'TestUserManagement',
        'test_method': 'test_user_deletion',
        'status': 'passed',
        'duration_in_ms': Decimal('1800.400')
    },
    {
        'name': 'test_user_search',
        'description': '验证用户搜索功能',
        'parent_suite': 'UserManagementSuite',
        'suite': 'UserManagement',
        'sub_suite': 'SearchTests',
        'test_class': 'TestUserManagement',
        'test_method': 'test_user_search',
        'status': 'passed',
        'duration_in_ms': Decimal('2300.500')
    }
]

# 生成时间戳
base_timestamp = int(start_time.timestamp() * 1000)

for idx, case_data in enumerate(cases_data):
    # 添加时间戳
    case_data['start_time'] = str(base_timestamp + idx * 60000)
    case_data['stop_time'] = str(base_timestamp + idx * 60000 + int(case_data['duration_in_ms']))
    
    case, created = TestSuiteDetail.objects.get_or_create(
        execution=execution,
        name=case_data['name'],
        defaults=case_data
    )
    status_icon = '✓' if case.status == 'passed' else '✗' if case.status == 'failed' else '⏸'
    print(f"    {status_icon} {'创建' if created else '已存在'} Case: {case.name} ({case.status})")

# ==================== 6. 创建 Category (缺陷分类) ====================
categories_data = [
    {
        'category_name': '登录失败',
        'count': 2,
        'severity': 'critical',
        'description': '用户登录相关的失败用例'
    },
    {
        'category_name': '功能跳过',
        'count': 1,
        'severity': 'minor',
        'description': '暂时跳过的测试用例'
    }
]

for cat_data in categories_data:
    category, created = Category.objects.get_or_create(
        execution=execution,
        category_name=cat_data['category_name'],
        defaults=cat_data
    )
    print(f"  {'✅ 创建' if created else '✅ 已存在'} Category: {category.category_name}")

# ==================== 7. 创建 FeatureScenario (特性场景) ====================
scenarios_data = [
    {
        'scenario_name': '用户认证场景',
        'total': 5,
        'passed': 3,
        'failed': 2,
        'pass_rate': Decimal('60.00')
    },
    {
        'scenario_name': '支付场景',
        'total': 5,
        'passed': 5,
        'failed': 0,
        'pass_rate': Decimal('100.00')
    }
]

for scenario_data in scenarios_data:
    scenario, created = FeatureScenario.objects.get_or_create(
        execution=execution,
        scenario_name=scenario_data['scenario_name'],
        defaults=scenario_data
    )
    print(f"  {'✅ 创建' if created else '✅ 已存在'} Scenario: {scenario.scenario_name}")

# ==================== 8. 验证数据 ====================
print("\n" + "="*60)
print("📊 数据创建完成! 统计信息:")
print("="*60)
print(f"✅ TestExecution: {TestExecution.objects.count()} 条")
print(f"✅ TestSuite: {TestSuite.objects.count()} 条")
print(f"✅ TestSuiteDetail: {TestSuiteDetail.objects.count()} 条")
print(f"✅ Category: {Category.objects.count()} 条")
print(f"✅ FeatureScenario: {FeatureScenario.objects.count()} 条")
print("="*60)

# 验证关键数据
print("\n🔍 验证 parent_suite 数据一致性:")
for suite in TestSuite.objects.filter(execution=execution):
    case_count = TestSuiteDetail.objects.filter(
        execution=execution,
        parent_suite=suite.suite_name
    ).count()
    print(f"  {suite.suite_name}: {case_count} 条用例 (预期: {suite.total_cases})")
    if case_count != suite.total_cases:
        print(f"    ⚠️ 警告: 用例数量不匹配!")

print("\n✅ 测试数据创建完成!")
print(f"📝 Execution ID: {execution.id}")
print(f"🔗 前端访问: http://localhost:5173/jenkins/report/{execution.id}")
print("\n💡 下一步:")
print("1. 访问前端报告详情页")
print("2. 点击【测试套件】Tab")
print("3. 点击任意套件的【查看用例】按钮")
print("4. 应该能看到 5 条用例记录!")
print("5. 点击用例名称,应该能打开详情抽屉!")
