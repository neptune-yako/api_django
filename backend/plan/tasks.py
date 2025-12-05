from ApiEngine.basecase import run_test
from scene.serializer import SceneRunSerializer
from .models import Plan, Record, Report
from project.models import Environment
from celery import shared_task


@shared_task
def run_task(env_id, task_id, tester):
    """
    运行测试计划
    :param env_id: 测试环境的id
    :param task_id: 测试任务的id
    :param tester: 接口调用者
    """
    # 获取测试环境数据
    env = Environment.objects.get(id=env_id)
    env_config = {
        "ENV": {
            "host": env.host,
            "headers": env.headers,
            **env.global_variable,
        },
        "DB": env.db,
        "global_func": env.global_func
    }
    # 获取测试数据
    plan = Plan.objects.get(id=task_id)
    # 获取任务中所有的测试套件
    scene_list = plan.scene.all()
    # 获取测试套件中的测试数据，组装测试引擎所需要的数据格式
    case_data = []
    for scene in scene_list:
        cases = scene.step_set.all()
        res = SceneRunSerializer(cases, many=True).data
        datas = sorted(res, key=lambda x: x['sort'])
        case_data.append({
            "name": scene.name,
            "Cases": [item['icase'] for item in datas]
        })
    # 创建一条运行记录
    record = Record.objects.create(plan=plan, env=env, tester=tester, status='执行中')
    # 运行测试
    result = run_test(case_data, env_config, debug=False)
    # 保存测试报告和测试运行记录
    report = Report.objects.create(info=result, record=record)
    report.save()
    record.all = result['all']
    record.success = result['success']
    record.fail = result['fail']
    record.error = result['error']
    record.pass_rate = '{:.2f}'.format(result['success'] * 100 / result['all'])
    record.status = '执行完毕'
    record.save()
    # 返回执行结果
    return result
