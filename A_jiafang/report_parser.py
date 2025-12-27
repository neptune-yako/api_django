# test_utils/report_parser.py
# encoding=UTF-8
from typing import Dict, List, Optional
from pydantic import BaseModel
import json
import os
import csv
from datetime import datetime
import pymysql
import sys

# 添加项目路径
TEST_PROJ_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
if TEST_PROJ_DIR not in sys.path:
    sys.path.append(TEST_PROJ_DIR)

# 从cfg_data导入数据库配置
from test_data.cfg_data import DB_CONFIG

class ReportOverview(BaseModel):
    timestamp: str
    report_name: str
    test_runs: List[dict]
    total_cases: int
    passed_cases: int
    failed_cases: int
    skipped_cases: int
    broken_cases: int
    unknown_cases: int
    pass_rate: float
    min_duration: int
    max_duration: int
    sum_duration: int
    execution_time: str
    start_time: Optional[str]
    end_time: Optional[str]
    status: str

class TestSuite(BaseModel):
    suite_name: str
    total_cases: int
    passed_cases: int
    failed_cases: int
    skipped_cases: int
    broken_cases: int
    unknown_cases: int
    pass_rate: float
    min_duration: int
    max_duration: int
    sum_duration: int
    duration_seconds: float

# 新增：测试套详细数据模型，完全对应CSV字段
class TestSuiteDetail(BaseModel):
    description: str          # DESCRIPTION
    duration_in_ms: float     # DURATION IN MS
    name: str                # NAME
    parent_suite: str        # PARENT SUITE
    start_time: str          # START TIME
    status: str              # STATUS
    stop_time: str           # STOP TIME
    sub_suite: str           # SUB SUITE
    suite: str               # SUITE
    test_class: str          # TEST CLASS
    test_method: str         # TEST METHOD

class Category(BaseModel):
    category_name: str
    count: int
    severity: str
    description: str

class Behavior(BaseModel):
    feature_name: str
    count: int
    passed: int
    failed: int
    total: int
    pass_rate: float

# 修改：增加suite_details字段
class AllureReportData(BaseModel):
    overview: ReportOverview
    suites: List[TestSuite]  # 汇总数据
    suite_details: List[TestSuiteDetail]  # 详细数据
    categories: List[Category]
    behaviors: List[Behavior]

def extract_overview_data_from_allure_report(timestamp: str, base_path: str) -> ReportOverview:
    """从allure-report/widgets/summary.json中提取总览数据"""
    data = {
        "timestamp": timestamp,
        "report_name": "自动化测试报告",
        "test_runs": [],
        "total_cases": 0,
        "passed_cases": 0,
        "failed_cases": 0,
        "skipped_cases": 0,
        "broken_cases": 0,
        "unknown_cases": 0,
        "pass_rate": 0.0,
        "min_duration": 0,
        "max_duration": 0,
        "sum_duration": 0,
        "execution_time": "",
        "start_time": None,
        "end_time": None,
        "status": "success"
    }
    
    try:
        # 构建summary.json路径
        summary_json_path = os.path.join(base_path, timestamp, "allure-report", "widgets", "summary.json")
        
        if not os.path.exists(summary_json_path):
            raise FileNotFoundError(f"Summary file not found: {summary_json_path}")
        
        # 读取并解析summary.json文件
        with open(summary_json_path, 'r', encoding='utf-8') as f:
            summary_data = json.load(f)
        
        # 提取报告名称
        data["report_name"] = summary_data.get("reportName", "自动化测试报告")
        
        # 提取测试运行信息
        data["test_runs"] = summary_data.get("testRuns", [])
        
        # 提取统计数据
        statistic = summary_data.get("statistic", {})
        data["total_cases"] = statistic.get("total", 0)
        data["passed_cases"] = statistic.get("passed", 0)
        data["failed_cases"] = statistic.get("failed", 0)
        data["skipped_cases"] = statistic.get("skipped", 0)
        data["broken_cases"] = statistic.get("broken", 0)
        data["unknown_cases"] = statistic.get("unknown", 0)
        
        # 计算通过率
        if data["total_cases"] > 0:
            data["pass_rate"] = round((data["passed_cases"] / data["total_cases"]) * 100, 2)
        
        # 提取时间信息
        time_info = summary_data.get("time", {})
        start_time_ms = time_info.get("start", 0)
        stop_time_ms = time_info.get("stop", 0)
        duration_ms = time_info.get("duration", 0)
        data["min_duration"] = time_info.get("minDuration", 0)
        data["max_duration"] = time_info.get("maxDuration", 0)
        data["sum_duration"] = time_info.get("sumDuration", 0)
        
        if start_time_ms:
            data["start_time"] = datetime.fromtimestamp(start_time_ms/1000).strftime('%Y-%m-%d %H:%M:%S')
        if stop_time_ms:
            data["end_time"] = datetime.fromtimestamp(stop_time_ms/1000).strftime('%Y-%m-%d %H:%M:%S')
        
        # 格式化执行时长
        hours = duration_ms // 3600000
        minutes = (duration_ms % 3600000) // 60000
        seconds = (duration_ms % 60000) // 1000
        
        time_parts = []
        if hours > 0:
            time_parts.append(f"{int(hours)}h")
        if minutes > 0:
            time_parts.append(f"{int(minutes)}m")
        if seconds > 0 or not time_parts:
            time_parts.append(f"{int(seconds)}s")
        
        data["execution_time"] = " ".join(time_parts)
        
        return ReportOverview(**data)
    
    except Exception as e:
        print(f"Error parsing overview data: {str(e)}")
        return ReportOverview(**data)

def extract_suites_data_from_allure_report(timestamp: str, base_path: str) -> List[TestSuite]:
    """从allure-report/data/suites.csv中提取测试套汇总数据"""
    suites = []
    
    try:
        # 构建allure-report/data/suites.csv路径
        suites_csv_path = os.path.join(base_path, timestamp, "allure-report", "data", "suites.csv")
        
        if not os.path.exists(suites_csv_path):
            print(f"Suites CSV file not found: {suites_csv_path}")
            return suites
        
        # 读取并解析suites.csv文件 - 尝试不同编码
        try:
            with open(suites_csv_path, 'r', encoding='utf-8') as f:
                # 使用csv模块解析数据
                reader = csv.DictReader(f)
                rows = list(reader)
        except UnicodeDecodeError:
            # 如果UTF-8失败，尝试GBK编码
            print("UTF-8 decoding failed, trying gbk encoding...")
            with open(suites_csv_path, 'r', encoding='gbk') as f:
                # 使用csv模块解析数据
                reader = csv.DictReader(f)
                rows = list(reader)
        
        # 统计每个测试套的信息
        suite_stats = {}
        
        for row in rows:
            # 获取测试套名称（从PARENT SUITE字段获取）
            suite_name = row.get("PARENT SUITE", "Unknown Suite").strip()
            if not suite_name or suite_name == "":
                suite_name = "Unknown Suite"
            
            # 初始化套件统计信息
            if suite_name not in suite_stats:
                suite_stats[suite_name] = {
                    "total_cases": 0,
                    "passed_cases": 0,
                    "failed_cases": 0,
                    "skipped_cases": 0,
                    "broken_cases": 0,
                    "unknown_cases": 0,
                    "duration_seconds": 0.0,
                    "min_duration": float('inf'),
                    "max_duration": 0,
                    "sum_duration": 0
                }
            
            # 增加测试用例计数
            suite_stats[suite_name]["total_cases"] += 1
            
            # 根据状态更新计数
            status = row.get("STATUS", "").lower()
            if status == "passed":
                suite_stats[suite_name]["passed_cases"] += 1
            elif status == "failed":
                suite_stats[suite_name]["failed_cases"] += 1
            elif status == "skipped":
                suite_stats[suite_name]["skipped_cases"] += 1
            else:
                # 其他状态如broken或unknown
                if "broken" in status:
                    suite_stats[suite_name]["broken_cases"] += 1
                else:
                    suite_stats[suite_name]["unknown_cases"] += 1
            
            # 处理持续时间
            try:
                duration_ms = float(row.get("DURATION IN MS", 0))
                duration_seconds = duration_ms / 1000.0
                suite_stats[suite_name]["duration_seconds"] += duration_seconds
                suite_stats[suite_name]["sum_duration"] += duration_ms
                
                # 更新最小和最大持续时间
                if duration_ms < suite_stats[suite_name]["min_duration"]:
                    suite_stats[suite_name]["min_duration"] = duration_ms
                if duration_ms > suite_stats[suite_name]["max_duration"]:
                    suite_stats[suite_name]["max_duration"] = duration_ms
            except ValueError:
                # 如果持续时间不是有效数字，则跳过
                pass
        
        # 将统计信息转换为TestSuite对象
        for suite_name, stats in suite_stats.items():
            # 计算通过率
            pass_rate = 0.0
            if stats["total_cases"] > 0:
                pass_rate = round((stats["passed_cases"] / stats["total_cases"]) * 100, 2)
            
            # 如果没有有效的持续时间数据，设置默认值
            if stats["min_duration"] == float('inf'):
                stats["min_duration"] = 0
            
            suite_info = TestSuite(
                suite_name=suite_name,
                total_cases=stats["total_cases"],
                passed_cases=stats["passed_cases"],
                failed_cases=stats["failed_cases"],
                skipped_cases=stats["skipped_cases"],
                broken_cases=stats["broken_cases"],
                unknown_cases=stats["unknown_cases"],
                pass_rate=pass_rate,
                min_duration=int(stats["min_duration"]),
                max_duration=int(stats["max_duration"]),
                sum_duration=int(stats["sum_duration"]),
                duration_seconds=stats["duration_seconds"]
            )
            
            suites.append(suite_info)
        
        return suites
    
    except Exception as e:
        print(f"Error parsing suites data: {str(e)}")
        return suites

# 新增：提取测试套详细数据的函数
def extract_suite_details_data_from_allure_report(timestamp: str, base_path: str) -> List[TestSuiteDetail]:
    """从allure-report/data/suites.csv中提取测试套详细数据，完全对应CSV字段"""
    details = []
    
    try:
        suites_csv_path = os.path.join(base_path, timestamp, "allure-report", "data", "suites.csv")
        
        if not os.path.exists(suites_csv_path):
            print(f"Suites CSV file not found: {suites_csv_path}")
            return details
        
        # 读取并解析suites.csv文件 - 尝试不同编码
        try:
            with open(suites_csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    detail_info = TestSuiteDetail(
                        description=row.get("DESCRIPTION", "").strip(),
                        duration_in_ms=float(row.get("DURATION IN MS", 0)) if row.get("DURATION IN MS", "").strip() else 0,
                        name=row.get("NAME", "").strip(),
                        parent_suite=row.get("PARENT SUITE", "Unknown Suite").strip() or "Unknown Suite",
                        start_time=row.get("START TIME", "").strip(),
                        status=row.get("STATUS", "unknown").strip().lower(),
                        stop_time=row.get("STOP TIME", "").strip(),
                        sub_suite=row.get("SUB SUITE", "").strip(),
                        suite=row.get("SUITE", "").strip(),
                        test_class=row.get("TEST CLASS", "").strip(),
                        test_method=row.get("TEST METHOD", "").strip()
                    )
                    details.append(detail_info)
        except UnicodeDecodeError:
            # 如果UTF-8失败，尝试GBK编码
            print("UTF-8 decoding failed for suite details, trying gbk encoding...")
            with open(suites_csv_path, 'r', encoding='gbk') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    detail_info = TestSuiteDetail(
                        description=row.get("DESCRIPTION", "").strip(),
                        duration_in_ms=float(row.get("DURATION IN MS", 0)) if row.get("DURATION IN MS", "").strip() else 0,
                        name=row.get("NAME", "").strip(),
                        parent_suite=row.get("PARENT SUITE", "Unknown Suite").strip() or "Unknown Suite",
                        start_time=row.get("START TIME", "").strip(),
                        status=row.get("STATUS", "unknown").strip().lower(),
                        stop_time=row.get("STOP TIME", "").strip(),
                        sub_suite=row.get("SUB SUITE", "").strip(),
                        suite=row.get("SUITE", "").strip(),
                        test_class=row.get("TEST CLASS", "").strip(),
                        test_method=row.get("TEST METHOD", "").strip()
                    )
                    details.append(detail_info)
        
        return details
    
    except Exception as e:
        print(f"Error parsing suites details data: {str(e)}")
        return details
def extract_categories_data_from_allure_report(timestamp: str, base_path: str) -> List[Category]:
    """从allure-report/data/categories.json中提取类别数据"""
    categories = []
    
    try:
        # 构建categories.json路径 (优先查找widgets目录)
        categories_json_path = os.path.join(base_path, timestamp, "allure-report", "widgets", "categories.json")
        
        # 如果widgets/categories.json不存在，尝试data/categories.json
        if not os.path.exists(categories_json_path):
            categories_json_path = os.path.join(base_path, timestamp, "allure-report", "data", "categories.json")
            
        if not os.path.exists(categories_json_path):
            print(f"Categories file not found: {categories_json_path}")
            return categories
        
        # 读取并解析categories.json文件 - 使用utf-8-sig处理BOM
        with open(categories_json_path, 'r', encoding='utf-8-sig') as f:
            categories_data = json.load(f)
        
        # 处理每个类别
        if isinstance(categories_data, dict) and "categories" in categories_data:
            # 处理包含categories数组的格式
            for category in categories_data["categories"]:
                category_info = {
                    "category_name": category.get("name", "Unknown Category"),
                    "count": len(category.get("children", [])),
                    "severity": "major",
                    "description": category.get("description", "")
                }
                
                # 根据类别名称判断严重程度
                name = category_info["category_name"].lower()
                if "critical" in name or "严重" in name:
                    category_info["severity"] = "critical"
                elif "major" in name or "主要" in name:
                    category_info["severity"] = "major"
                elif "minor" in name or "次要" in name:
                    category_info["severity"] = "minor"
                else:
                    category_info["severity"] = "major"
                
                categories.append(Category(**category_info))
        elif isinstance(categories_data, list):
            # 处理直接是数组的格式
            for category in categories_data:
                category_info = {
                    "category_name": category.get("name", "Unknown Category"),
                    "count": len(category.get("children", [])),
                    "severity": "major",
                    "description": category.get("description", "")
                }
                
                # 根据类别名称判断严重程度
                name = category_info["category_name"].lower()
                if "critical" in name or "严重" in name:
                    category_info["severity"] = "critical"
                elif "major" in name or "主要" in name:
                    category_info["severity"] = "major"
                elif "minor" in name or "次要" in name:
                    category_info["severity"] = "minor"
                else:
                    category_info["severity"] = "major"
                
                categories.append(Category(**category_info))
        
        return categories
    
    except Exception as e:
        print(f"Error parsing categories data: {str(e)}")
        return categories

def extract_behaviors_data_from_allure_report(timestamp: str, base_path: str) -> List[Behavior]:
    """从allure-report/data/behaviors.json中提取行为/特性数据"""
    behaviors = []
    
    try:
        # 构建behaviors.json路径 (优先查找widgets目录)
        behaviors_json_path = os.path.join(base_path, timestamp, "allure-report", "widgets", "behaviors.json")
        
        # 如果widgets/behaviors.json不存在，尝试data/behaviors.json
        if not os.path.exists(behaviors_json_path):
            behaviors_json_path = os.path.join(base_path, timestamp, "allure-report", "data", "behaviors.json")
            
        if not os.path.exists(behaviors_json_path):
            print(f"Behaviors file not found: {behaviors_json_path}")
            return behaviors
        
        # 读取并解析behaviors.json文件 - 使用utf-8-sig处理BOM
        with open(behaviors_json_path, 'r', encoding='utf-8-sig') as f:
            behaviors_data = json.load(f)
        
        # 处理每个特性
        if isinstance(behaviors_data, dict) and "features" in behaviors_data:
            # 处理包含features数组的格式
            for feature in behaviors_data["features"]:
                feature_info = {
                    "feature_name": feature.get("name", "Unknown Feature"),
                    "count": len(feature.get("children", [])),
                    "passed": feature.get("statistic", {}).get("passed", 0),
                    "failed": feature.get("statistic", {}).get("failed", 0),
                    "total": feature.get("statistic", {}).get("total", 0),
                    "pass_rate": 0.0
                }
                
                # 计算通过率
                if feature_info["total"] > 0:
                    feature_info["pass_rate"] = round(
                        (feature_info["passed"] / feature_info["total"]) * 100, 2
                    )
                
                behaviors.append(Behavior(**feature_info))
        elif isinstance(behaviors_data, list):
            # 处理直接是数组的格式
            for feature in behaviors_data:
                feature_info = {
                    "feature_name": feature.get("name", "Unknown Feature"),
                    "count": len(feature.get("children", [])),
                    "passed": feature.get("statistic", {}).get("passed", 0),
                    "failed": feature.get("statistic", {}).get("failed", 0),
                    "total": feature.get("statistic", {}).get("total", 0),
                    "pass_rate": 0.0
                }
                
                # 计算通过率
                if feature_info["total"] > 0:
                    feature_info["pass_rate"] = round(
                        (feature_info["passed"] / feature_info["total"]) * 100, 2
                    )
                
                behaviors.append(Behavior(**feature_info))
        
        return behaviors
    
    except Exception as e:
        print(f"Error parsing behaviors data: {str(e)}")
        return behaviors
# 修改：增加suite_details数据提取
def parse_allure_report_complete_data(timestamp: str, base_path: str = "./test_result"):
    """解析完整的Allure报告数据"""
    try:
        # 从不同位置提取各类数据
        overview_data = extract_overview_data_from_allure_report(timestamp, base_path)
        suites_data = extract_suites_data_from_allure_report(timestamp, base_path)
        suite_details_data = extract_suite_details_data_from_allure_report(timestamp, base_path)  # 新增
        categories_data = extract_categories_data_from_allure_report(timestamp, base_path)
        behaviors_data = extract_behaviors_data_from_allure_report(timestamp, base_path)
        
        return AllureReportData(
            overview=overview_data,
            suites=suites_data,
            suite_details=suite_details_data,  # 新增
            categories=categories_data,
            behaviors=behaviors_data
        )
    except Exception as e:
        print(f"Failed to parse report: {str(e)}")
        return None

# 修改：增加详细数据保存逻辑
def save_report_data_to_mysql(report_data: AllureReportData):
    """将解析的报告数据保存到MySQL数据库"""
    connection = None
    try:
        # 连接到数据库
        connection = pymysql.connect(**DB_CONFIG)
        
        with connection.cursor() as cursor:
            # 开始事务
            connection.begin()
            
            try:
                # 1. 检查是否已存在相同时间戳的记录
                cursor.execute("SELECT id FROM test_execution WHERE timestamp = %s", (report_data.overview.timestamp,))
                existing_record = cursor.fetchone()
                
                if existing_record:
                    # 如果已存在，删除旧的关联数据
                    execution_id = existing_record[0]
                    
                    # 删除旧的关联数据
                    cursor.execute("DELETE FROM test_suites WHERE execution_id = %s", (execution_id,))
                    cursor.execute("DELETE FROM test_suite_details WHERE execution_id = %s", (execution_id,))
                    cursor.execute("DELETE FROM categories WHERE execution_id = %s", (execution_id,))
                    cursor.execute("DELETE FROM feature_scenarios WHERE execution_id = %s", (execution_id,))
                    
                    # 更新主记录
                    overview_sql = """
                        UPDATE test_execution SET
                            report_title = %s,
                            total_cases = %s,
                            passed_cases = %s,
                            failed_cases = %s,
                            skipped_cases = %s,
                            broken_cases = %s,
                            unknown_cases = %s,
                            pass_rate = %s,
                            min_duration = %s,
                            max_duration = %s,
                            sum_duration = %s,
                            execution_time = %s,
                            start_time = %s,
                            end_time = %s,
                            status = %s,
                            updated_at = NOW()
                        WHERE timestamp = %s
                    """
                    
                    overview = report_data.overview
                    cursor.execute(overview_sql, (
                        overview.report_name,
                        overview.total_cases,
                        overview.passed_cases,
                        overview.failed_cases,
                        overview.skipped_cases,
                        overview.broken_cases,
                        overview.unknown_cases,
                        overview.pass_rate,
                        overview.min_duration,
                        overview.max_duration,
                        overview.sum_duration,
                        overview.execution_time,
                        overview.start_time,
                        overview.end_time,
                        overview.status,
                        overview.timestamp
                    ))
                    print(f"Updated test_execution record for timestamp: {overview.timestamp}")
                else:
                    # 如果不存在，插入新记录
                    overview_sql = """
                        INSERT INTO test_execution (
                            timestamp, report_title, total_cases, passed_cases, 
                            failed_cases, skipped_cases, broken_cases, unknown_cases,
                            pass_rate, min_duration, max_duration, sum_duration,
                            execution_time, start_time, end_time, status
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    
                    overview = report_data.overview
                    cursor.execute(overview_sql, (
                        overview.timestamp,
                        overview.report_name,
                        overview.total_cases,
                        overview.passed_cases,
                        overview.failed_cases,
                        overview.skipped_cases,
                        overview.broken_cases,
                        overview.unknown_cases,
                        overview.pass_rate,
                        overview.min_duration,
                        overview.max_duration,
                        overview.sum_duration,
                        overview.execution_time,
                        overview.start_time,
                        overview.end_time,
                        overview.status
                    ))
                    execution_id = cursor.lastrowid
                    print(f"Inserted new test_execution record with id: {execution_id}")
                
                # 验证 execution_id 是否有效
                if execution_id is None or execution_id == 0:
                    raise Exception(f"Failed to get execution_id after inserting test_execution record. Got: {execution_id}")
                
                print(f"Processing suites data for execution_id: {execution_id}")
                
                # 2. 插入测试套汇总数据
                suite_sql = """
                    INSERT INTO test_suites (
                        execution_id, suite_name, total_cases, passed_cases, 
                        failed_cases, skipped_cases, broken_cases, unknown_cases,
                        pass_rate, min_duration, max_duration, sum_duration, duration_seconds
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                successful_suite_inserts = 0
                for i, suite in enumerate(report_data.suites):
                    try:
                        cursor.execute(suite_sql, (
                            execution_id,
                            suite.suite_name,
                            suite.total_cases,
                            suite.passed_cases,
                            suite.failed_cases,
                            suite.skipped_cases,
                            suite.broken_cases,
                            suite.unknown_cases,
                            suite.pass_rate,
                            suite.min_duration,
                            suite.max_duration,
                            suite.sum_duration,
                            suite.duration_seconds
                        ))
                        successful_suite_inserts += 1
                        print(f"Inserted suite {i+1}/{len(report_data.suites)}: {suite.suite_name[:50]}...")
                    except Exception as e:
                        print(f"Error inserting suite {suite.suite_name[:50]}...: {str(e)}")
                
                print(f"Successfully inserted {successful_suite_inserts}/{len(report_data.suites)} suites")
                
                print(f"Processing suite details data for execution_id: {execution_id}")
                
                # 3. 插入测试套详细数据
                detail_sql = """
                    INSERT INTO test_suite_details (
                        execution_id, description, duration_in_ms, name,
                        parent_suite, start_time, status, stop_time,
                        sub_suite, suite, test_class, test_method
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                successful_detail_inserts = 0
                for i, detail in enumerate(report_data.suite_details):
                    try:
                        # 处理可能的字符编码问题
                        description = detail.description.encode('utf-8', errors='ignore').decode('utf-8')
                        name = detail.name.encode('utf-8', errors='ignore').decode('utf-8')
                        
                        cursor.execute(detail_sql, (
                            execution_id,
                            description,
                            detail.duration_in_ms,
                            name,
                            detail.parent_suite,
                            detail.start_time,
                            detail.status,
                            detail.stop_time,
                            detail.sub_suite,
                            detail.suite,
                            detail.test_class,
                            detail.test_method
                        ))
                        successful_detail_inserts += 1
                        print(f"Inserted detail {i+1}/{len(report_data.suite_details)}: {name[:30]}...")
                    except Exception as e:
                        print(f"Error inserting detail {detail.name[:30]}...: {str(e)}")
                
                print(f"Successfully inserted {successful_detail_inserts}/{len(report_data.suite_details)} details")
                
                # 4. 插入类别数据
                category_sql = """
                    INSERT INTO categories (
                        execution_id, category_name, count, severity, description
                    ) VALUES (%s, %s, %s, %s, %s)
                """
                
                successful_category_inserts = 0
                for i, category in enumerate(report_data.categories):
                    try:
                        cursor.execute(category_sql, (
                            execution_id,
                            category.category_name,
                            category.count,
                            category.severity,
                            category.description
                        ))
                        successful_category_inserts += 1
                        print(f"Inserted category {i+1}/{len(report_data.categories)}: {category.category_name}")
                    except Exception as e:
                        print(f"Error inserting category {category.category_name}: {str(e)}")
                
                print(f"Successfully inserted {successful_category_inserts}/{len(report_data.categories)} categories")
                
                # 5. 插入行为/特性数据
                behavior_sql = """
                    INSERT INTO feature_scenarios (
                        execution_id, scenario_name, count, passed, failed, total, pass_rate
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                
                successful_behavior_inserts = 0
                for i, behavior in enumerate(report_data.behaviors):
                    try:
                        cursor.execute(behavior_sql, (
                            execution_id,
                            behavior.feature_name,
                            behavior.count,
                            behavior.passed,
                            behavior.failed,
                            behavior.total,
                            behavior.pass_rate
                        ))
                        successful_behavior_inserts += 1
                        print(f"Inserted behavior {i+1}/{len(report_data.behaviors)}: {behavior.feature_name}")
                    except Exception as e:
                        print(f"Error inserting behavior {behavior.feature_name}: {str(e)}")
                
                print(f"Successfully inserted {successful_behavior_inserts}/{len(report_data.behaviors)} behaviors")
                
                # 提交事务
                connection.commit()
                print(f"Successfully saved all report data to database for timestamp: {report_data.overview.timestamp}")
                print(f"Summary - Suites: {successful_suite_inserts}, Details: {successful_detail_inserts}, Categories: {successful_category_inserts}, Behaviors: {successful_behavior_inserts}")
                return True
                
            except Exception as e:
                # 回滚事务
                connection.rollback()
                print(f"Error saving report data to database: {str(e)}")
                return False
        
    except Exception as e:
        print(f"Database connection error: {str(e)}")
        return False
    
    finally:
        # 关闭数据库连接
        if connection:
            connection.close()
def get_historical_statistics(days: int = 30):
    """获取历史统计数据"""
    connection = None
    try:
        connection = pymysql.connect(**DB_CONFIG)
        
        with connection.cursor() as cursor:
            # 获取最近N天的测试执行统计
            stats_sql = """
                SELECT 
                    DATE(created_at) as test_date,
                    COUNT(*) as execution_count,
                    AVG(total_cases) as avg_total_cases,
                    AVG(passed_cases) as avg_passed_cases,
                    AVG(failed_cases) as avg_failed_cases,
                    AVG(pass_rate) as avg_pass_rate
                FROM test_execution 
                WHERE created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
                GROUP BY DATE(created_at)
                ORDER BY test_date DESC
            """
            
            cursor.execute(stats_sql, (days,))
            daily_stats = cursor.fetchall()
            
            # 获取测试套级别的统计
            suite_stats_sql = """
                SELECT 
                    s.suite_name,
                    COUNT(*) as execution_count,
                    AVG(s.pass_rate) as avg_pass_rate,
                    MAX(s.pass_rate) as max_pass_rate,
                    MIN(s.pass_rate) as min_pass_rate
                FROM test_suites s
                JOIN test_execution e ON s.execution_id = e.id
                WHERE e.created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
                GROUP BY s.suite_name
                ORDER BY avg_pass_rate DESC
            """
            
            cursor.execute(suite_stats_sql, (days,))
            suite_stats = cursor.fetchall()
            
            # 获取类别统计
            category_stats_sql = """
                SELECT 
                    c.category_name,
                    SUM(c.count) as total_count,
                    COUNT(DISTINCT e.id) as execution_count
                FROM categories c
                JOIN test_execution e ON c.execution_id = e.id
                WHERE e.created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
                GROUP BY c.category_name
                ORDER BY total_count DESC
            """
            
            cursor.execute(category_stats_sql, (days,))
            category_stats = cursor.fetchall()
            
            return {
                "daily_stats": daily_stats,
                "suite_stats": suite_stats,
                "category_stats": category_stats
            }
            
    except Exception as e:
        print(f"Error getting historical statistics: {str(e)}")
        return None
    
    finally:
        if connection:
            connection.close()

def parse_and_save_allure_report(timestamp: str, base_path: str = "./test_result"):
    """解析并保存Allure报告数据到数据库"""
    try:
        # 解析报告数据
        report_data = parse_allure_report_complete_data(timestamp, base_path)
        
        if report_data is None:
            print(f"Failed to parse report data for timestamp: {timestamp}")
            return False
        
        # 保存到数据库
        success = save_report_data_to_mysql(report_data)
        
        if success:
            print(f"Successfully parsed and saved report data for timestamp: {timestamp}")
        else:
            print(f"Failed to save report data for timestamp: {timestamp}")
            
        return success
        
    except Exception as e:
        print(f"Error in parse_and_save_allure_report: {str(e)}")
        return False