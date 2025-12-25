"""
Pipeline 生成器 - 基础类
参考 api_test_runner.py 的 generate_api_test_pipeline 方法（第202-304行）
"""

import html
import logging
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class BasePipelineGenerator(ABC):
    """Pipeline 生成器基类"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化生成器

        Args:
            config: Job 配置字典，包含:
                - name: Job 名称
                - description: Job 描述
                - node_label: 节点标签（单个或逗号分隔的多个）
                - stages: Stage 列表（可选）
                - pre_script: 前置脚本（可选）
                - test_command: 测试命令（可选）
                - post_script: 后置脚本（可选）
        """
        self.config = config
        self.node_labels = self._parse_node_labels(config.get('node_label', 'any'))

    def _parse_node_labels(self, node_label: Any) -> List[str]:
        """解析节点标签，支持单个标签或逗号分隔的多个标签"""
        if isinstance(node_label, str):
            return [label.strip() for label in node_label.split(',') if label.strip()]
        elif isinstance(node_label, list):
            return node_label
        return ['any']

    @abstractmethod
    def generate_pipeline_script(self) -> str:
        """生成 Pipeline 脚本（子类实现）"""
        pass

    def generate_job_config_xml(self) -> str:
        """
        生成完整的 Jenkins Job 配置 XML
        参考 api_test_runner.py 第338-349行
        """
        pipeline_script = self.generate_pipeline_script()
        pipeline_script_escaped = html.escape(pipeline_script)

        job_config = f"""<?xml version='1.1' encoding='UTF-8'?>
<flow-definition plugin="workflow-job">
  <description>{html.escape(self.config.get('description', ''))}</description>
  <keepDependencies>false</keepDependencies>
  <properties/>
  <definition class="org.jenkinsci.plugins.workflow.cps.CpsFlowDefinition" plugin="workflow-cps">
    <script>{pipeline_script_escaped}</script>
    <sandbox>true</sandbox>
  </definition>
  <triggers/>
  <disabled>false</disabled>
</flow-definition>"""

        return job_config

    def is_multi_node(self) -> bool:
        """判断是否为多节点 Job"""
        return len(self.node_labels) > 1


class SimplePipelineGenerator(BasePipelineGenerator):
    """
    简单 Pipeline 生成器
    适用于基础的单节点 Pipeline Job
    参考 api_test_runner.py 的 generate_api_test_pipeline 方法
    """

    def generate_pipeline_script(self) -> str:
        """生成简单 Pipeline 脚本"""
        # Agent 指令：支持多节点（空格分隔）
        if self.node_labels and self.node_labels[0] != 'any':
            # 将多个节点用空格连接：label 'node-1 node-2 node-3'
            agent_directive = f"label '{' '.join(self.node_labels)}'"
        else:
            agent_directive = 'any'

        # 获取配置
        job_name = self.config.get('name', 'unknown')
        environment_names = self.config.get('environment_names', [])
        pre_script = self.config.get('pre_script', '')
        test_command = self.config.get('test_command', '')
        post_script = self.config.get('post_script', '')

        # 环境信息字符串
        env_info = f"环境: {', '.join(environment_names)}" if environment_names else "环境: 默认"

        # 构建前置脚本步骤
        pre_script_step = ''
        if pre_script:
            pre_script_step = f"""
        stage('准备环境') {{
            steps {{
                echo '=========================================='
                echo '准备测试环境: {env_info}'
                echo '=========================================='
                sh '''{pre_script}'''
            }}
        }}"""

        # 构建测试命令步骤
        test_step = f"""        stage('执行测试') {{
            steps {{
                echo '=========================================='
                echo '开始执行测试用例 - {env_info}'
                echo '=========================================='
                sh '''{test_command if test_command else 'echo "测试执行完成"'}'''
            }}
        }}"""

        # 构建后置脚本步骤
        post_script_step = ''
        if post_script:
            post_script_step = f"""
        stage('生成报告') {{
            steps {{
                echo '=========================================='
                echo '生成测试报告 - {env_info}'
                echo '=========================================='
                sh '''{post_script}'''
            }}
        }}"""

        pipeline = f"""pipeline {{
    agent {agent_directive}

    stages {{
        stage('环境信息') {{
            steps {{
                echo '=========================================='
                echo 'Job: {job_name}'
                echo '{env_info}'
                echo '执行节点: ${{env.NODE_NAME}}'
                echo '=========================================='
            }}
        }}{pre_script_step}
{test_step}{post_script_step}
    }}

    post {{
        always {{
            echo '=========================================='
            echo 'Pipeline 执行完成 - {env_info}'
            echo '=========================================='
        }}
        success {{
            echo '✅ Pipeline 执行成功'
        }}
        failure {{
            echo '❌ Pipeline 执行失败'
        }}
    }}
}}"""

        return pipeline


class CustomPipelineGenerator(BasePipelineGenerator):
    """
    自定义 Pipeline 生成器
    支持用户自定义多个 Stage
    """

    def generate_pipeline_script(self) -> str:
        """生成自定义 Pipeline 脚本"""
        # Agent 指令：支持多节点（空格分隔）
        if self.node_labels and self.node_labels[0] != 'any':
            # 将多个节点用空格连接：label 'node-1 node-2 node-3'
            agent_directive = f"label '{' '.join(self.node_labels)}'"
        else:
            agent_directive = 'any'

        # 获取自定义 stages
        custom_stages = self.config.get('stages', [])
        job_name = self.config.get('name', 'unknown')

        # 如果没有自定义 stages，使用默认
        if not custom_stages:
            return SimplePipelineGenerator(self.config).generate_pipeline_script()

        # 构建自定义 stages
        stage_definitions = []
        for stage in custom_stages:
            stage_name = stage.get('name', 'Unnamed Stage')
            stage_script = stage.get('script', '')

            stage_def = f"""        stage('{stage_name}') {{
            steps {{
                sh '''{stage_script}'''
            }}
        }}"""
            stage_definitions.append(stage_def)

        stages_block = '\n\n'.join(stage_definitions)

        pipeline = f"""pipeline {{
    agent {agent_directive}

    stages {{
        stage('环境信息') {{
            steps {{
                echo '=========================================='
                echo 'Job: {job_name}'
                echo '执行节点: ${{env.NODE_NAME}}'
                echo '=========================================='
            }}
        }}

{stages_block}
    }}

    post {{
        always {{
            echo 'Pipeline 执行完成'
        }}
        success {{
            echo '✅ Pipeline 执行成功'
        }}
        failure {{
            echo '❌ Pipeline 执行失败'
        }}
    }}
}}"""

        return pipeline
