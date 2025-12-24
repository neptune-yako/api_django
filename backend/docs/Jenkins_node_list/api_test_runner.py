#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API测试运行器 - 集成版
将API测试用例生成与Jenkins节点执行集成到一起
"""

import jenkins
import json
import argparse
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class IntegratedAPITestRunner:
    """集成的API测试运行器"""
    
    def __init__(self, config_file: str = 'jenkins_nodes_config.json'):
        """初始化"""
        self.config = self.load_config(config_file)
        self.jenkins_config = self.config.get('jenkins', {})
        self.test_case = {
            'name': '',
            'url': '',
            'method': 'GET',
            'headers': {},
            'body': '',
            'description': ''
        }
        self.server = None
    
    def load_config(self, config_file: str) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            config_path = Path(__file__).parent / config_file
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                logger.info(f"✓ 已加载配置文件: {config_path}")
                return config
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            return {}
    
    def connect_jenkins(self):
        """连接到Jenkins"""
        try:
            self.server = jenkins.Jenkins(
                self.jenkins_config['url'],
                username=self.jenkins_config['username'],
                password=self.jenkins_config['password']
            )
            user = self.server.get_whoami()
            version = self.server.get_version()
            logger.info(f"✓ 已连接到 Jenkins {version}")
            logger.info(f"✓ 当前用户: {user.get('fullName', 'Unknown')}")
            return True
        except Exception as e:
            logger.error(f"✗ 连接 Jenkins 失败: {e}")
            return False
    
    # ==================== 交互式输入部分 ====================
    
    def ask_question(self, question: str, default: str = None) -> str:
        """询问用户问题"""
        if default:
            prompt = f"{question} [{default}]: "
        else:
            prompt = f"{question}: "
        answer = input(prompt).strip()
        return answer if answer else default
    
    def ask_yes_no(self, question: str, default: bool = False) -> bool:
        """询问是/否问题"""
        default_str = "Y/n" if default else "y/N"
        answer = input(f"{question} [{default_str}]: ").strip().lower()
        if not answer:
            return default
        return answer in ['y', 'yes', '是']
    
    def collect_api_test_info(self):
        """收集API测试信息"""
        print("\n" + "=" * 60)
        print("🚀 API 测试运行器 - 集成版")
        print("=" * 60)
        print("创建API测试用例并直接在Jenkins节点上运行\n")
        
        # 基本信息
        print("📝 步骤 1/4: 基本信息")
        print("-" * 60)
        self.test_case['name'] = self.ask_question(
            "测试用例名称",
            f"api_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        self.test_case['description'] = self.ask_question(
            "测试描述",
            "API测试"
        )
        
        # URL和方法
        print("\n🌐 步骤 2/4: URL和请求方法")
        print("-" * 60)
        self.test_case['url'] = self.ask_question(
            "请求URL",
            "https://api.example.com/endpoint"
        )
        
        print("\n请选择HTTP方法:")
        methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']
        for i, method in enumerate(methods, 1):
            print(f"  {i}. {method}")
        
        choice = self.ask_question("选择方法 (1-5)", "1")
        try:
            self.test_case['method'] = methods[int(choice) - 1]
        except (ValueError, IndexError):
            self.test_case['method'] = 'GET'
        
        print(f"✓ 已选择: {self.test_case['method']}")
        
        # 请求头
        print("\n📋 步骤 3/4: 请求头")
        print("-" * 60)
        
        if self.test_case['method'] in ['POST', 'PUT', 'PATCH']:
            if self.ask_yes_no("使用默认JSON请求头?", default=True):
                self.test_case['headers'] = {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
                print("✓ 已添加默认请求头")
        
        if self.ask_yes_no("是否添加更多请求头?", default=False):
            print("添加自定义请求头 (格式: Header-Name: value)")
            print("每行一个,输入空行结束")
            
            while True:
                header = input("请求头: ").strip()
                if not header:
                    break
                if ':' in header:
                    key, value = header.split(':', 1)
                    self.test_case['headers'][key.strip()] = value.strip()
                    print(f"  ✓ 已添加: {key.strip()}")
        
        # 请求体
        print("\n📦 步骤 4/4: 请求体")
        print("-" * 60)
        
        if self.test_case['method'] in ['POST', 'PUT', 'PATCH']:
            if self.ask_yes_no("是否包含请求体?", default=True):
                print("输入JSON数据 (可以多行,输入空行结束):")
                print('示例: {"username": "test", "password": "123456"}')
                
                body_lines = []
                while True:
                    line = input()
                    if not line:
                        break
                    body_lines.append(line)
                
                body_text = '\n'.join(body_lines)
                
                # 验证JSON
                try:
                    json.loads(body_text)
                    self.test_case['body'] = body_text
                    print("✓ JSON格式验证通过")
                except json.JSONDecodeError as e:
                    print(f"⚠ JSON格式错误: {e}")
                    if self.ask_yes_no("仍然使用此内容?", default=True):
                        self.test_case['body'] = body_text
        
        # 预览
        print("\n👀 预览测试用例")
        print("-" * 60)
        print(f"名称: {self.test_case['name']}")
        print(f"描述: {self.test_case['description']}")
        print(f"URL: {self.test_case['url']}")
        print(f"方法: {self.test_case['method']}")
        
        if self.test_case['headers']:
            print("请求头:")
            for k, v in self.test_case['headers'].items():
                print(f"  {k}: {v}")
        
        if self.test_case['body']:
            print(f"请求体: {self.test_case['body'][:100]}...")
        print()
    
    # ==================== Pipeline 生成部分 ====================
    
    def generate_api_test_pipeline(self, node_label: str) -> str:
        """
        生成API测试的Jenkins Pipeline脚本
        
        Args:
            node_label: 节点标签
            
        Returns:
            Pipeline脚本
        """
        # 准备请求头参数
        headers_args = []
        for k, v in self.test_case['headers'].items():
            # 转义单引号和双引号
            v_escaped = v.replace("'", "\\'").replace('"', '\\"')
            headers_args.append(f"-H '{k}: {v_escaped}'")
        headers_str = ' \\\n                '.join(headers_args) if headers_args else ''
        
        # 准备请求体参数
        body_arg = ''
        if self.test_case['body']:
            # 转义body中的特殊字符
            body_escaped = self.test_case['body'].replace("'", "'\\''")
            body_arg = f"-d '{body_escaped}'"
        
        # 构建curl命令
        curl_cmd = f"""curl -X '{self.test_case['method']}' \\
                '{self.test_case['url']}'"""
        
        if headers_str:
            curl_cmd += f" \\\n                {headers_str}"
        
        if body_arg:
            curl_cmd += f" \\\n                {body_arg}"
        
        curl_cmd += " \\\n                -w '\\nHTTP Status: %{http_code}\\nTime Total: %{time_total}s\\n' \\\n                -s"
        
        # 生成Pipeline
        pipeline = f"""pipeline {{
    agent {{ label '{node_label}' }}
    
    stages {{
        stage('环境信息') {{
            steps {{
                echo "=========================================="
                echo "🧪 API 测试: {self.test_case['name']}"
                echo "=========================================="
                echo "执行节点: ${{env.NODE_NAME}}"
                echo "测试描述: {self.test_case['description']}"
                echo "请求URL: {self.test_case['url']}"
                echo "请求方法: {self.test_case['method']}"
            }}
        }}
        
        stage('执行API测试') {{
            steps {{
                script {{
                    echo "\\n📤 发送请求..."
                    
                    // 执行curl命令
                    def response = sh(
                        script: '''{curl_cmd}''',
                        returnStdout: true
                    ).trim()
                    
                    echo "\\n📥 响应内容:"
                    echo response
                    
                    // 提取HTTP状态码
                    def statusMatch = (response =~ /HTTP Status: (\\d+)/)
                    if (statusMatch.find()) {{
                        def statusCode = statusMatch[0][1] as Integer
                        echo "\\n状态码: ${{statusCode}}"
                        
                        if (statusCode >= 200 && statusCode < 300) {{
                            echo "\\n✅ 测试通过 - 请求成功"
                        }} else {{
                            error("\\n❌ 测试失败 - 状态码: ${{statusCode}}")
                        }}
                    }} else {{
                        echo "\\n⚠️ 无法提取状态码"
                    }}
                }}
            }}
        }}
    }}
    
    post {{
        always {{
            echo "\\n=========================================="
            echo "测试执行完成"
            echo "=========================================="
        }}
        success {{
            echo "✅ Pipeline 执行成功"
        }}
        failure {{
            echo "❌ Pipeline 执行失败"
        }}
    }}
}}"""
        
        return pipeline
    
    def create_and_run_pipeline(self, node_label: str, wait: bool = True, cleanup: bool = False):
        """
        创建并运行Pipeline
        
        Args:
            node_label: 节点标签
            wait: 是否等待完成
            cleanup: 是否完成后清理
        """
        job_name = f"{self.test_case['name']}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        logger.info("\n" + "=" * 60)
        logger.info(f"创建 Jenkins Pipeline 任务")
        logger.info("=" * 60)
        logger.info(f"任务名称: {job_name}")
        logger.info(f"目标节点: {node_label}")
        logger.info(f"API URL: {self.test_case['url']}")
        logger.info("=" * 60)
        
        # 生成Pipeline脚本
        pipeline_script = self.generate_api_test_pipeline(node_label)
        
        logger.info("\n生成的 Pipeline 脚本:")
        logger.info("-" * 60)
        print(pipeline_script)
        logger.info("-" * 60)
        
        # XML转义Pipeline脚本中的特殊字符
        import html
        pipeline_script_escaped = html.escape(pipeline_script)
        
        # 构建任务配置
        job_config = f"""<?xml version='1.1' encoding='UTF-8'?>
<flow-definition plugin="workflow-job">
  <description>{html.escape(self.test_case['description'])}</description>
  <keepDependencies>false</keepDependencies>
  <properties/>
  <definition class="org.jenkinsci.plugins.workflow.cps.CpsFlowDefinition" plugin="workflow-cps">
    <script>{pipeline_script_escaped}</script>
    <sandbox>true</sandbox>
  </definition>
  <triggers/>
  <disabled>false</disabled>
</flow-definition>"""
        
        try:
            # 创建任务
            if self.server.job_exists(job_name):
                logger.info(f"任务 '{job_name}' 已存在,正在更新...")
                self.server.reconfig_job(job_name, job_config)
            else:
                logger.info(f"创建新任务 '{job_name}'...")
                self.server.create_job(job_name, job_config)
            
            logger.info(f"✓ 任务已准备就绪")
            
            # 触发构建
            logger.info(f"\n触发构建...")
            queue_number = self.server.build_job(job_name)
            logger.info(f"✓ 任务已加入构建队列: #{queue_number}")
            
            # 等待构建
            if wait:
                import time
                logger.info(f"\n等待构建完成...")
                
                start_time = time.time()
                timeout = 300
                last_build_number = None
                
                # 等待构建开始
                while time.time() - start_time < timeout:
                    job_info = self.server.get_job_info(job_name)
                    last_build = job_info.get('lastBuild')
                    
                    if last_build:
                        last_build_number = last_build['number']
                        break
                    
                    time.sleep(2)
                
                if last_build_number:
                    logger.info(f"构建已开始: #{last_build_number}")
                    
                    # 等待构建完成
                    while time.time() - start_time < timeout:
                        build_info = self.server.get_build_info(job_name, last_build_number)
                        
                        if not build_info.get('building', True):
                            result = build_info.get('result', 'UNKNOWN')
                            duration = build_info.get('duration', 0) / 1000
                            
                            logger.info(f"\n构建完成: #{last_build_number}")
                            logger.info(f"结果: {result}")
                            logger.info(f"耗时: {duration:.1f}秒")
                            
                            # 显示控制台输出
                            console_output = self.server.get_build_console_output(job_name, last_build_number)
                            logger.info("\n控制台输出:")
                            logger.info("=" * 60)
                            print(console_output)
                            logger.info("=" * 60)
                            
                            # 清理
                            if cleanup:
                                logger.info(f"\n清理任务...")
                                self.server.delete_job(job_name)
                                logger.info(f"✓ 已删除任务 '{job_name}'")
                            else:
                                logger.info(f"\n任务URL: {self.jenkins_config['url']}/job/{job_name}")
                            
                            if result == 'SUCCESS':
                                logger.info("\n✅ 测试执行成功")
                                return True
                            else:
                                logger.error(f"\n❌ 测试执行失败: {result}")
                                return False
                        
                        time.sleep(5)
            else:
                logger.info(f"\n任务已创建: {self.jenkins_config['url']}/job/{job_name}")
                return True
                
        except Exception as e:
            logger.error(f"\n执行失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def run_on_multiple_nodes(self, node_labels: list, wait: bool = True, cleanup: bool = False):
        """
        在多个节点上运行相同的测试
        
        Args:
            node_labels: 节点标签列表
            wait: 是否等待完成
            cleanup: 是否完成后清理
        """
        logger.info(f"\n🚀 多节点并行测试")
        logger.info(f"目标节点: {', '.join(node_labels)}")
        logger.info(f"共 {len(node_labels)} 个节点\n")
        
        results = {}
        job_names = {}
        
        # 为每个节点创建并触发任务
        for node_label in node_labels:
            job_name = f"{self.test_case['name']}-{node_label}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            job_names[node_label] = job_name
            
            logger.info(f"\n{'='*60}")
            logger.info(f"节点: {node_label}")
            logger.info(f"任务: {job_name}")
            logger.info(f"{'='*60}")
            
            # 生成Pipeline
            pipeline_script = self.generate_api_test_pipeline(node_label)
            
            # XML转义
            import html
            pipeline_script_escaped = html.escape(pipeline_script)
            
            # 创建任务配置
            job_config = f"""<?xml version='1.1' encoding='UTF-8'?>
<flow-definition plugin="workflow-job">
  <description>{html.escape(self.test_case['description'])} - 节点: {node_label}</description>
  <keepDependencies>false</keepDependencies>
  <properties/>
  <definition class="org.jenkinsci.plugins.workflow.cps.CpsFlowDefinition" plugin="workflow-cps">
    <script>{pipeline_script_escaped}</script>
    <sandbox>true</sandbox>
  </definition>
  <triggers/>
  <disabled>false</disabled>
</flow-definition>"""
            
            try:
                # 创建任务
                if self.server.job_exists(job_name):
                    self.server.reconfig_job(job_name, job_config)
                else:
                    self.server.create_job(job_name, job_config)
                
                logger.info(f"✓ 任务已创建")
                
                # 触发构建
                queue_number = self.server.build_job(job_name)
                logger.info(f"✓ 已触发构建: #{queue_number}")
                
                results[node_label] = {'status': 'triggered', 'job_name': job_name}
                
            except Exception as e:
                logger.error(f"✗ 节点 {node_label} 失败: {e}")
                results[node_label] = {'status': 'failed', 'error': str(e)}
        
        # 等待所有构建完成
        if wait:
            import time
            logger.info(f"\n{'='*60}")
            logger.info("等待所有节点的构建完成...")
            logger.info(f"{'='*60}\n")
            
            time.sleep(5)  # 等待构建开始
            
            for node_label in node_labels:
                if results[node_label]['status'] != 'triggered':
                    continue
                
                job_name = job_names[node_label]
                logger.info(f"\n检查节点 {node_label} 的构建状态...")
                
                try:
                    # 获取最后一次构建
                    job_info = self.server.get_job_info(job_name)
                    last_build = job_info.get('lastBuild')
                    
                    if last_build:
                        build_number = last_build['number']
                        
                        # 等待构建完成
                        timeout = 300
                        start_time = time.time()
                        
                        while time.time() - start_time < timeout:
                            build_info = self.server.get_build_info(job_name, build_number)
                            
                            if not build_info.get('building', True):
                                result = build_info.get('result', 'UNKNOWN')
                                duration = build_info.get('duration', 0) / 1000
                                
                                results[node_label]['build_number'] = build_number
                                results[node_label]['result'] = result
                                results[node_label]['duration'] = duration
                                
                                logger.info(f"  构建 #{build_number} 完成")
                                logger.info(f"  结果: {result}")
                                logger.info(f"  耗时: {duration:.1f}秒")
                                
                                break
                            
                            time.sleep(3)
                        
                except Exception as e:
                    logger.error(f"  获取构建信息失败: {e}")
                    results[node_label]['error'] = str(e)
        
        # 显示汇总结果
        logger.info(f"\n{'='*60}")
        logger.info("📊 测试结果汇总")
        logger.info(f"{'='*60}\n")
        
        success_count = 0
        failed_count = 0
        
        for node_label, result in results.items():
            status_icon = "✅" if result.get('result') == 'SUCCESS' else "❌"
            logger.info(f"{status_icon} 节点: {node_label}")
            logger.info(f"   任务: {result.get('job_name', 'N/A')}")
            
            if 'result' in result:
                logger.info(f"   结果: {result['result']}")
                logger.info(f"   耗时: {result.get('duration', 0):.1f}秒")
                
                if result['result'] == 'SUCCESS':
                    success_count += 1
                else:
                    failed_count += 1
            elif 'error' in result:
                logger.info(f"   错误: {result['error']}")
                failed_count += 1
            
            logger.info(f"   URL: {self.jenkins_config['url']}/job/{result.get('job_name', '')}\n")
        
        logger.info(f"{'='*60}")
        logger.info(f"总计: {len(node_labels)} 个节点")
        logger.info(f"成功: {success_count} 个")
        logger.info(f"失败: {failed_count} 个")
        logger.info(f"{'='*60}")
        
        # 清理
        if cleanup:
            logger.info(f"\n清理所有任务...")
            for node_label, result in results.items():
                if 'job_name' in result:
                    try:
                        self.server.delete_job(result['job_name'])
                        logger.info(f"✓ 已删除: {result['job_name']}")
                    except Exception as e:
                        logger.error(f"✗ 删除失败 {result['job_name']}: {e}")
        
        return success_count == len(node_labels)
    
    def run_interactive(self, node_label: str, wait: bool = True, cleanup: bool = False):
        """运行交互式流程"""
        # 收集测试信息
        self.collect_api_test_info()
        
        # 确认
        if not self.ask_yes_no("\n确认创建并运行测试?", default=True):
            print("\n❌ 已取消")
            return 1
        
        # 连接Jenkins
        if not self.connect_jenkins():
            return 1
        
        # 检查是否为多节点
        if ',' in node_label:
            node_labels = [n.strip() for n in node_label.split(',')]
            success = self.run_on_multiple_nodes(node_labels, wait, cleanup)
        else:
            # 单节点运行
            success = self.create_and_run_pipeline(node_label, wait, cleanup)
        
        return 0 if success else 1


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='API测试运行器 - 集成版',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 单节点: 交互式创建测试并在指定节点运行
  python api_test_runner.py --node a --wait
  
  # 多节点: 在多个节点上并行运行相同的测试
  python api_test_runner.py --node a,test,b --wait
  
  # 运行后自动清理任务
  python api_test_runner.py --node test --wait --cleanup
  
  # 不等待构建完成
  python api_test_runner.py --node a
        """
    )
    
    parser.add_argument(
        '--node',
        required=True,
        help='目标节点名称或标签，多个节点用逗号分隔(例如: a,test,b)'
    )
    
    parser.add_argument(
        '--wait',
        action='store_true',
        help='等待构建完成并显示结果'
    )
    
    parser.add_argument(
        '--cleanup',
        action='store_true',
        help='构建完成后删除任务'
    )
    
    parser.add_argument(
        '--config',
        default='jenkins_nodes_config.json',
        help='配置文件路径(默认: jenkins_nodes_config.json)'
    )
    
    args = parser.parse_args()
    
    try:
        runner = IntegratedAPITestRunner(config_file=args.config)
        return runner.run_interactive(
            node_label=args.node,
            wait=args.wait,
            cleanup=args.cleanup
        )
    except KeyboardInterrupt:
        print("\n\n❌ 用户中断")
        return 130
    except Exception as e:
        logger.error(f"\n执行失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
