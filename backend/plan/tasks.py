from ApiEngine.basecase import run_test
from scene.serializer import SceneRunSerializer
from .models import Plan, Record, Report
from project.models import Environment
from celery import shared_task
# Jenkins 集成
from jenkins_integration.models import JenkinsServer
from jenkins_integration.jenkins_client import build_job
import logging

logger = logging.getLogger('django')


@shared_task
def run_task(env_id, task_id, tester):
    """
    运行测试计划 (支持本地测试 + Jenkins 构建)
    """
    # 获取测试环境数据
    env = Environment.objects.get(id=env_id)
    
    # 1. 环境注入机制 (Soft Injection)
    # 自动将 Jenkins 配置注入到全局变量，供脚本使用
    jenkins_config = {}
    try:
        jenkins_server = JenkinsServer.objects.filter(is_active=True).first()
        if jenkins_server:
            jenkins_config = {
                "_JENKINS_URL": jenkins_server.url,
                "_JENKINS_TOKEN": jenkins_server.token,
                "_JENKINS_USER": jenkins_server.username
            }
    except Exception as e:
        logger.warning(f"Jenkins 环境注入失败: {str(e)}")

    env_config = {
        "ENV": {
            "host": env.host,
            "headers": env.headers,
            **env.global_variable,
            **jenkins_config  # 注入 Jenkins 变量
        },
        "DB": env.db,
        "global_func": env.global_func
    }
    
    # 获取测试数据
    plan = Plan.objects.get(id=task_id)
    
    # 2. Jenkins 触发机制 (Trigger)
    # 检查计划是否关联了 Jenkins Jobs
    jenkins_jobs = plan.jenkins_jobs.all()
    if jenkins_jobs:
        logger.info(f"计划 [{plan.name}] 包含 {jenkins_jobs.count()} 个流水线任务，开始触发...")
        for job in jenkins_jobs:
            if job.is_active:
                # 触发构建
                # TODO: 这里可以传递参数 parameters
                success, msg, _ = build_job(job.name)
                if success:
                    logger.info(f"流水线 [{job.name}] 触发成功")
                else:
                    logger.error(f"流水线 [{job.name}] 触发失败: {msg}")
            else:
                logger.info(f"流水线 [{job.name}] 已禁用，跳过执行")

    # 3. 本地测试机制 (Local Execution)
    # 获取任务中所有的测试套件
    scene_list = plan.scene.all()
    
    # 如果没有本地套件，直接返回结果（避免报错）
    if not scene_list:
        if jenkins_jobs:
            return {"status": "success", "msg": "Jenkins jobs triggered"}
        return {"status": "skipped", "msg": "No scenes or jobs to run"}

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
