# encoding=UTF-8
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from typing import List, Optional
import asyncio
import logging
import os
import sys
import time
import subprocess
from pathlib import Path
import pymysql
from test_data.cfg_data import CI_TEST_DIR, PC_PATH_TEST_RESULT, DB_CONFIG

# 添加项目路径
TEST_PROJ_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(TEST_PROJ_DIR)

from test_utils import custom_allure_report, custom_logger
from test_utils.report_parser import parse_and_save_allure_report
from test_data.cfg_data import CI_TEST_DIR, PC_PATH_TEST_RESULT

app = FastAPI(title="创智联恒自动化测试系统agent")

app.mount("/test_result", StaticFiles(directory=PC_PATH_TEST_RESULT), name="test_result")


class TestCaseExecutionRequest(BaseModel):
    test_cases: List[str]  # 要执行的测试用例列表
    title_name: Optional[str] = "自动化测试报告"  # 报告标题


class ExecutionResult(BaseModel):
    status: str
    message: str
    report_url: Optional[str] = None
    timestamp: Optional[str] = None


# 存储执行状态
execution_status = {}


@app.post("/execute-tests", response_model=ExecutionResult)
async def execute_tests(request: TestCaseExecutionRequest, background_tasks: BackgroundTasks):
    """执行指定的测试用例"""
    try:
        # 确保工作目录是项目根目录
        os.chdir(CI_TEST_DIR)
        # 生成时间戳
        now = time.strftime('%Y%m%d%H%M%S')
        timestamp = custom_allure_report.get_time_stamp_and_write_to_file(now)

        # 创建测试报告目录
        test_report_dir = os.path.join(PC_PATH_TEST_RESULT, timestamp)
        os.makedirs(test_report_dir, exist_ok=True)

        # 初始化日志
        custom_logger.log_init(PC_PATH_TEST_RESULT, now)
        
        # 启动后台任务执行测试
        background_tasks.add_task(run_tests, request.test_cases, timestamp, request.title_name)
        
        execution_status[timestamp] = "running"
        
        return ExecutionResult(
            status="started",
            message=f"测试已启动，时间戳: {timestamp}",
            timestamp=timestamp
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/execution-status/{timestamp}")
async def get_execution_status(timestamp: str):
    """获取测试执行状态"""
    status = execution_status.get(timestamp, "not_found")
    return {"timestamp": timestamp, "status": status}


@app.get("/latest-report")
async def get_latest_report():
    """获取最新的测试报告"""
    try:
        test_result_dir = Path(PC_PATH_TEST_RESULT)
        if not test_result_dir.exists():
            raise HTTPException(status_code=404, detail="测试结果目录不存在")

        # 获取最新的报告目录
        subdirs = [d for d in test_result_dir.iterdir() if d.is_dir()]

        if not subdirs:
            raise HTTPException(status_code=404, detail="没有找到测试报告")
            
        latest_dir = max(subdirs, key=os.path.getctime)
        timestamp = latest_dir.name  # 获取最新的时间戳
        print(f"最新报告目录: {timestamp}")
        report_url = f"/test_result/{timestamp}/allure-report/index.html"
        
        return {
            "status": "success",
            "report_url": report_url,
            "timestamp": latest_dir.name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/save-report-data/{timestamp}")
async def save_report_data(timestamp: str, base_path: str = "./test_result"):
    """手动触发保存指定时间戳的测试报告数据到数据库"""
    try:
        # 调用report_parser中的方法保存报告数据
        success = parse_and_save_allure_report(timestamp, base_path)
        
        if success:
            return {
                "status": "success",
                "message": f"测试报告数据已成功保存到数据库: {timestamp}",
                "timestamp": timestamp
            }
        else:
            return {
                "status": "error",
                "message": f"测试报告数据保存到数据库失败: {timestamp}",
                "timestamp": timestamp
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存测试报告数据时出错: {str(e)}")


async def run_tests(test_cases: List[str], timestamp: str, title_name: str):
    """在后台运行测试"""
    try:
        print(f'=====AutoTest Start======')
        print('=====Step1 环境准备：获取当日最新版本，下载版本到基站======')
        # 这里可以添加环境准备逻辑
        
        print('=====Step2 启动测试用例，生成测试报告======')
        # 确保工作目录是项目根目录
        os.chdir(CI_TEST_DIR)

        # 生成allure报告查看脚本
        custom_allure_report.generate_report_bat(timestamp, title_name)
        
        # 构建pytest命令
        pytest_args = ['--alluredir', f'./test_result/{timestamp}/allure-results', '-p', 'no:assertion']
        
        # 添加测试用例
        for test_case in test_cases:
            # 解析测试用例格式 (例如: "test_module::TestClass::test_method")
            class_path, case_class = parse_test_case(test_case)
            test_case_file = "./" + class_path.replace(".", "/") + ".py"
            test_case_format = f"{test_case_file}::{case_class}::{test_case.split('::')[-1]}"
            pytest_args.append(test_case_format)
        
        # 工作目录切换回工程目录
        os.chdir(CI_TEST_DIR)
        current_dir = os.getcwd()
        logging.info('The pytest root dir is {}'.format(current_dir))
        
        # 执行测试
        if len(pytest_args) > 4:  # 除了基础参数外还有测试用例
            # 使用subprocess异步执行
            process = subprocess.Popen([
                sys.executable, "-m", "pytest"
            ] + pytest_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                logging.error(f"测试执行失败: {stderr.decode()}")
                execution_status[timestamp] = "failed"
            else:
                # 生成测试报告
                custom_allure_report.generate_test_report(timestamp, title_name)
                execution_status[timestamp] = "completed"
                
                # 解析并保存Allure报告数据到数据库
                try:
                    success = parse_and_save_allure_report(timestamp, "./test_result")
                    if success:
                        print(f"测试报告数据已成功保存到数据库: {timestamp}")
                    else:
                        print(f"测试报告数据保存到数据库失败: {timestamp}")
                except Exception as e:
                    logging.error(f"保存测试报告数据到数据库时出错: {str(e)}")
                
                print('=====AutoTest Over======')
        else:
            execution_status[timestamp] = "completed"
            print("未选择测试用例")
            
    except Exception as e:
        logging.error(f"执行测试时出错: {str(e)}")
        execution_status[timestamp] = "error"

@app.post("/debug-save-report-data/{timestamp}")
async def debug_save_report_data(timestamp: str):
    """调试：手动触发保存指定时间戳的测试报告数据到数据库并检查结果"""
    try:
        # 调用report_parser中的方法保存报告数据
        success = parse_and_save_allure_report(timestamp, "./test_result")
        
        # 检查数据库中各个表的数据
        connection = pymysql.connect(**DB_CONFIG)
        with connection.cursor() as cursor:
            # 获取 execution_id
            cursor.execute("SELECT id FROM test_execution WHERE timestamp = %s", (timestamp,))
            execution_record = cursor.fetchone()
            
            if execution_record:
                execution_id = execution_record[0]
                
                # 检查各表数据量
                cursor.execute("SELECT COUNT(*) FROM test_suites WHERE execution_id = %s", (execution_id,))
                suites_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM test_suite_details WHERE execution_id = %s", (execution_id,))
                details_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM categories WHERE execution_id = %s", (execution_id,))
                categories_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM feature_scenarios WHERE execution_id = %s", (execution_id,))
                scenarios_count = cursor.fetchone()[0]
                
                connection.close()
                
                return {
                    "status": "success" if success else "error",
                    "message": f"数据保存{'成功' if success else '失败'}",
                    "execution_id": execution_id,
                    "timestamp": timestamp,
                    "tables_data": {
                        "test_suites": suites_count,
                        "test_suite_details": details_count,
                        "categories": categories_count,
                        "feature_scenarios": scenarios_count
                    }
                }
            else:
                connection.close()
                return {
                    "status": "error",
                    "message": "找不到执行记录",
                    "timestamp": timestamp
                }
                
    except Exception as e:
        return {
            "status": "error",
            "message": f"保存测试报告数据时出错: {str(e)}",
            "timestamp": timestamp
        }
def parse_test_case(test_case: str):
    """解析测试用例字符串，提取模块路径和类名"""
    # 这里需要根据实际的test_suite_locator.get_module_and_class_name实现
    # 示例实现：
    parts = test_case.split("::")
    if len(parts) >= 2:
        module_path = ".".join(parts[:-2]) if len(parts) > 2 else "default_module"
        class_name = parts[-2]
        return module_path, class_name
    return "unknown_module", "UnknownClass"


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)