"""
多节点并行 Pipeline 生成器
参考 api_test_runner.py 的 run_on_multiple_nodes 方法（第435-596行）
"""

import html
import logging
from typing import Dict, Any, List
from .base import BasePipelineGenerator, SimplePipelineGenerator

logger = logging.getLogger(__name__)


class MatrixPipelineGenerator(BasePipelineGenerator):
    """
    Matrix Pipeline 生成器
    使用 Jenkins 声明式 Pipeline 的 matrix 指令实现多节点并行执行

    参考: https://www.jenkins.io/doc/book/pipeline/syntax/#matrix
    """

    def generate_pipeline_script(self) -> str:
        """生成 matrix Pipeline 脚本"""
        # 单节点情况，回退到简单生成器
        if not self.node_labels or len(self.node_labels) <= 1:
            logger.info("单节点模式，Matrix 不适用，回退到 SimplePipelineGenerator")
            return SimplePipelineGenerator(self.config).generate_pipeline_script()

        logger.info(f"Matrix 多节点并行模式，节点: {self.node_labels}")

        job_name = self.config.get('name', 'unknown')
        environment_names = self.config.get('environment_names', [])
        pre_script = self.config.get('pre_script', '')
        test_command = self.config.get('test_command', '')
        post_script = self.config.get('post_script', '')

        # 环境信息字符串
        env_info = f"环境: {', '.join(environment_names)}" if environment_names else "多节点并行测试"

        # 构建 axis values（逗号分隔的字符串列表）
        axis_values = ", ".join([f"'{label}'" for label in self.node_labels])

        # 构建 matrix 内部的 stages
        matrix_stages = self._build_matrix_stages(job_name, env_info, pre_script, test_command, post_script)

        # 生成高级配置块
        library_import = self._generate_library_import()
        options_block = self._generate_options_block()
        environment_block = self._generate_environment_block()

        pipeline = f"""{library_import}pipeline {{
    agent none
{options_block}{environment_block}
    stages {{
        stage('多节点并行执行') {{
            matrix {{
                axes {{
                    axis {{
                        name 'NODE_LABEL'
                        values {axis_values}
                    }}
                }}
                stages {{
{matrix_stages}
                }}
            }}
        }}
    }}

    post {{
        always {{
            echo '=========================================='
            echo '多节点 Pipeline 执行完成 - {env_info}'
            echo '=========================================='
        }}
        success {{
            echo '多节点 Pipeline 执行成功'
        }}
        failure {{
            echo '多节点 Pipeline 执行失败'
        }}
    }}
}}"""

        return pipeline

    def _build_matrix_stages(self, job_name: str, env_info: str,
                             pre_script: str, test_command: str, post_script: str) -> str:
        """构建 matrix 内部的 stages"""
        stages_list = []

        # 1. 环境信息 stage（必需）
        stages_list.append(self._build_info_stage(job_name, env_info))

        # 2. 准备环境 stage（可选）
        if pre_script:
            stages_list.append(self._build_pre_stage(pre_script))

        # 3. 执行测试 stage（必需）
        stages_list.append(self._build_test_stage(test_command))

        # 4. 生成报告 stage（可选）
        if post_script:
            stages_list.append(self._build_post_stage(post_script))

        return "\n".join(stages_list)

    def _build_info_stage(self, job_name: str, env_info: str) -> str:
        """构建环境信息 stage"""
        return f"""                    stage('环境信息') {{
                        steps {{
                            echo "=========================================="
                            echo "Job: {job_name}"
                            echo "{env_info}"
                            echo "节点: ${{NODE_LABEL}}"
                            echo "=========================================="
                        }}
                    }}"""

    def _build_pre_stage(self, pre_script: str) -> str:
        """构建准备环境 stage"""
        return f"""                    stage('准备环境') {{
                        steps {{
                            sh '''{pre_script}'''
                        }}
                    }}"""

    def _build_test_stage(self, test_command: str) -> str:
        """构建执行测试 stage（关键：使用 node() 分配节点）"""
        cmd = test_command if test_command else 'echo "测试执行完成"'
        return f"""                    stage('执行测试') {{
                        steps {{
                            node("${{NODE_LABEL}}") {{
                                sh '''{cmd}'''
                            }}
                        }}
                    }}"""

    def _build_post_stage(self, post_script: str) -> str:
        """构建生成报告 stage"""
        return f"""                    stage('生成报告') {{
                        steps {{
                            sh '''{post_script}'''
                        }}
                    }}"""
    
    def _generate_library_import(self) -> str:
        """生成 @Library 导入"""
        advanced = self.config.get('advanced', {})
        library = advanced.get('library', '')
        
        if library:
            return f"@Library('{library}') _\n"
        return ''
    
    def _generate_options_block(self) -> str:
        """生成 options 块"""
        advanced = self.config.get('advanced', {})
        options = advanced.get('options', {})
        
        enabled_opts = []
        
        if options.get('disableConcurrentBuilds'):
            enabled_opts.append('        disableConcurrentBuilds abortPrevious: true')
        
        if options.get('enableTimeout'):
            timeout_value = options.get('timeoutValue', 10)
            timeout_unit = options.get('timeoutUnit', 'HOURS')
            enabled_opts.append(f"        timeout(time: {timeout_value}, unit: '{timeout_unit}')")
        
        if options.get('timestamps'):
            enabled_opts.append('        timestamps()')
        
        if not enabled_opts:
            return ''
        
        return "    options {\n" + "\n".join(enabled_opts) + "\n    }\n"
    
    def _generate_environment_block(self) -> str:
        """生成 environment 块"""
        advanced = self.config.get('advanced', {})
        env_vars = advanced.get('environment', [])
        
        # 过滤出有效的环境变量
        valid_env_vars = [e for e in env_vars if isinstance(e, dict) and e.get('key') and e.get('value')]
        
        if not valid_env_vars:
            return ''
        
        env_lines = [f"        {var['key']} = \"{var['value']}\"" for var in valid_env_vars]
        return "    environment {\n" + "\n".join(env_lines) + "\n    }\n"


class MultiNodePipelineGenerator(BasePipelineGenerator):
    """
    多节点并行 Pipeline 生成器
    在单个 Pipeline 中使用 parallel 指令实现多节点并行执行
    """

    def generate_pipeline_script(self) -> str:
        """生成多节点并行 Pipeline 脚本"""
        if not self.node_labels or len(self.node_labels) <= 1:
            # 单节点情况，回退到简单生成器
            logger.info("单节点模式，使用 SimplePipelineGenerator")
            return SimplePipelineGenerator(self.config).generate_pipeline_script()

        logger.info(f"多节点并行模式，节点: {self.node_labels}")

        job_name = self.config.get('name', 'unknown')
        environment_names = self.config.get('environment_names', [])
        pre_script = self.config.get('pre_script', '')
        test_command = self.config.get('test_command', '')
        post_script = self.config.get('post_script', '')

        # 环境信息字符串
        env_info = f"环境: {', '.join(environment_names)}" if environment_names else "多环境并行测试"

        # 构建每个节点的执行脚本
        node_entries = []
        for i, node_label in enumerate(self.node_labels):
            # 获取对应的环境名称
            env_name = environment_names[i] if i < len(environment_names) else node_label

            # 构建该节点的执行步骤
            steps = []
            if pre_script:
                steps.append(f"sh '''{pre_script}'''")
            if test_command:
                steps.append(f"sh '''{test_command}'''")
            else:
                steps.append("sh 'echo \"Executing on ${env.NODE_NAME}\"'")
            if post_script:
                steps.append(f"sh '''{post_script}'''")

            steps_script = '\n                '.join(steps)

            entry = f'"{node_label}": {{\n                node("{node_label}") {{\n                    echo "=========================================="\n                    echo "环境: {env_name}"\n                    echo "节点: {node_label}"\n                    echo "节点名称: ${{env.NODE_NAME}}"\n                    echo "=========================================="\n                    {steps_script}\n                }}\n            }}'

            node_entries.append(entry)

        # 格式化 parallel map
        parallel_map = '{\n            ' + ',\n            '.join(node_entries) + '\n        }'

        pipeline = f"""pipeline {{
    agent none

    stages {{
        stage('多节点并行执行') {{
            steps {{
                script {{
                    echo '=========================================='
                    echo 'Job: {job_name}'
                    echo '{env_info}'
                    echo '并行节点: {', '.join(self.node_labels)}'
                    echo '=========================================='

                    parallel {parallel_map}

                    echo '\\n=========================================='
                    echo '所有节点执行完成'
                    echo '=========================================='
                }}
            }}
        }}
    }}

    post {{
        always {{
            echo '多节点 Pipeline 执行完成 - {env_info}'
        }}
        success {{
            echo '✅ 多节点 Pipeline 执行成功'
        }}
        failure {{
            echo '❌ 多节点 Pipeline 执行失败'
        }}
    }}
}}"""

        return pipeline


class ParentJobGenerator(BasePipelineGenerator):
    """
    父 Job 生成器
    为多节点 Job 创建一个父 Job，用于统一管理子 Job
    参考 api_test_runner.py 的多节点实现方式
    """

    def generate_pipeline_script(self) -> str:
        """生成父 Job Pipeline 脚本"""
        child_jobs = self.config.get('child_jobs', [])
        job_name = self.config.get('name', 'unknown')

        if not child_jobs:
            # 没有子 Job，返回简单提示
            return """pipeline {
    agent any
    stages {
        stage('提示') {
            steps {
                echo '请先配置子任务'
            }
        }
    }
}"""

        # 构建 Job 名称列表
        job_names_str = ', '.join([f"'{job_name}'" for job_name in child_jobs])

        pipeline = f"""pipeline {{
    agent any

    stages {{
        stage('触发子任务') {{
            steps {{
                script {{
                    echo '=========================================='
                    echo '父任务: {job_name}'
                    echo '子任务数量: {len(child_jobs)}'
                    echo '=========================================='

                    // 子任务列表
                    def jobNames = [{job_names_str}]

                    // 并行触发所有子任务并等待结果
                    def builds = [:]
                    jobNames.each {{ jobName ->
                        builds[jobName] = build job: jobName, wait: true
                    }}

                    // 检查所有构建结果
                    builds.each {{ jobName, build ->
                        def result = build.getResult()
                        echo "子任务: ${{jobName}}, 结果: ${{result}}"
                    }}

                    echo '\\n=========================================='
                    echo '所有子任务已触发完成'
                    echo '=========================================='
                }}
            }}
        }}
    }}

    post {{
        success {{
            echo '✅ 所有子任务执行成功'
        }}
        failure {{
            echo '❌ 部分子任务执行失败'
        }}
    }}
}}"""

        return pipeline


def create_pipeline_generator(
    config: Dict[str, Any],
    multi_node_mode: str = 'matrix',
    use_custom_stages: bool = False
) -> BasePipelineGenerator:
    """
    工厂函数：根据配置创建合适的生成器

    Args:
        config: Job 配置字典
        multi_node_mode: 多节点模式
            - 'matrix': 使用 matrix 指令（默认，推荐，需要 Jenkins 2.300+）
            - 'label': 使用 label 指令  agent { label 'node-1 node-2' }
            - 'parallel': 并行执行（使用 parallel 指令）
            - 'parent': 父子 Job 模式
        use_custom_stages: 是否使用自定义 stages

    Returns:
        Pipeline 生成器实例
    """
    from .base import SimplePipelineGenerator, CustomPipelineGenerator, CustomMatrixPipelineGenerator

    node_label = config.get('node_label', 'any')

    # 解析节点列表（后端传递的是逗号分隔）
    if isinstance(node_label, str):
        node_label_list = [label.strip() for label in node_label.split(',') if label.strip()]
    elif isinstance(node_label, list):
        node_label_list = node_label
    else:
        node_label_list = ['any']

    # 判断是否为多节点
    is_multi_node = len(node_label_list) > 1

    # 自定义 stages 模式
    if use_custom_stages and config.get('stages'):
        if is_multi_node:
            # 多节点 + 自定义 stages = CustomMatrixPipelineGenerator
            logger.info(f"创建自定义Matrix Pipeline生成器，节点: {node_label_list}")
            return CustomMatrixPipelineGenerator(config)
        else:
            # 单节点 + 自定义 stages = CustomPipelineGenerator
            logger.info(f"创建自定义 Pipeline 生成器（单节点），节点: {node_label_list}")
            return CustomPipelineGenerator(config)

    # 使用 label 模式
    if multi_node_mode == 'label':
        logger.info(f"创建简单 Pipeline 生成器（label 模式），节点: {node_label_list}")
        return SimplePipelineGenerator(config)

    # 多节点并行模式
    if is_multi_node:
        if multi_node_mode == 'parent':
            logger.info(f"创建父子 Job 模式生成器，节点: {node_label_list}")
            return ParentJobGenerator(config)
        elif multi_node_mode == 'parallel':
            # parallel 并行模式
            logger.info(f"创建多节点并行 Pipeline 生成器，节点: {node_label_list}")
            return MultiNodePipelineGenerator(config)
        else:
            # 默认使用 matrix 模式
            logger.info(f"创建 Matrix Pipeline 生成器，节点: {node_label_list}")
            return MatrixPipelineGenerator(config)

    # 单节点 fallback
    logger.info(f"创建简单单节点 Pipeline 生成器，节点: {node_label_list}")
    return SimplePipelineGenerator(config)
