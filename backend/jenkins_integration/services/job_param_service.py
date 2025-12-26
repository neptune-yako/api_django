"""
Job 参数服务 - 动态插槽业务逻辑

负责处理 Jenkins Job 的参数提取、替换和带参构建等核心业务逻辑
"""
from typing import List, Dict, Tuple
from django.db import transaction
import logging

logger = logging.getLogger(__name__)


class JobParamService:
    """Job 参数管理服务"""
    
    @staticmethod
    def get_job_params(job_id: int) -> List[str]:
        """
        获取指定 Job 的动态参数列表
        
        Args:
            job_id: Job 的数据库 ID
            
        Returns:
            list: 参数名列表（已排序）
            
        Raises:
            JenkinsJob.DoesNotExist: Job 不存在时抛出
            
        Example:
            >>> JobParamService.get_job_params(1)
            ['env', 'score']
        """
        from ..models import JenkinsJob
        from ..utils.param_parser import extract_params
        
        try:
            # 查询 Job
            job = JenkinsJob.objects.get(id=job_id)
            
            # 提取参数
            params = extract_params(job.config_xml)
            
            logger.info(f"Job [{job.name}] 包含 {len(params)} 个动态参数: {params}")
            return params
            
        except JenkinsJob.DoesNotExist:
            logger.error(f"Job ID {job_id} 不存在")
            raise
        except Exception as e:
            logger.error(f"获取 Job 参数失败: {str(e)}")
            raise
    
    @staticmethod
    def get_job_params_by_name(job_name: str, server_id: int = None) -> List[str]:
        """
        根据 Job 名称获取动态参数列表
        
        Args:
            job_name: Job 名称
            server_id: 服务器 ID（可选，用于多服务器场景）
            
        Returns:
            list: 参数名列表
            
        Raises:
            JenkinsJob.DoesNotExist: Job 不存在时抛出
        """
        from ..models import JenkinsJob
        from ..utils.param_parser import extract_params
        
        try:
            # 构建查询条件
            query_kwargs = {'name': job_name}
            if server_id:
                query_kwargs['server_id'] = server_id
            
            job = JenkinsJob.objects.get(**query_kwargs)
            return extract_params(job.config_xml)
            
        except JenkinsJob.DoesNotExist:
            logger.error(f"Job '{job_name}' 不存在")
            raise
    
    @staticmethod
    def has_dynamic_params(job_id: int) -> bool:
        """
        快速检查 Job 是否包含动态参数
        
        Args:
            job_id: Job ID
            
        Returns:
            bool: True 表示包含动态参数
        """
        from ..models import JenkinsJob
        from ..utils.param_parser import has_dynamic_params
        
        try:
            job = JenkinsJob.objects.get(id=job_id)
            return has_dynamic_params(job.config_xml)
        except JenkinsJob.DoesNotExist:
            return False
    
    @staticmethod
    @transaction.atomic
    def build_with_params(
        job_id: int, 
        build_params: Dict[str, str],
        validate_missing: bool = True
    ) -> Tuple[bool, str, dict]:
        """
        使用参数构建 Job（核心业务方法）
        
        支持两种参数化方式:
        1. Jenkins 原生参数: parameters { string(name: 'xxx', ...) } → 直接参数化构建
        2. 动态插槽 {{}}: {{score}} → 替换 XML + 更新配置 + 构建
        
        Args:
            job_id: Job ID
            build_params: 参数字典 {"score": "95", "env": "prod"}
            validate_missing: 是否验证参数完整性（默认 True）
            
        Returns:
            tuple: (success, message, data)
                - success: 是否成功
                - message: 提示信息
                - data: 构建信息（构建编号等）
                
        Raises:
            ValueError: 参数验证失败时抛出
            Exception: Jenkins API 调用失败时抛出
        """
        from ..models import JenkinsJob
        from ..utils.param_parser import (
            replace_params, 
            get_missing_params,
            has_dynamic_params,
            has_jenkins_native_params
        )
        from ..jenkins_client import update_job, build_job
        
        try:
            # 1. 获取 Job
            job = JenkinsJob.objects.get(id=job_id)
            logger.info(f"开始为 Job [{job.name}] 进行参数化构建")
            
            # 2. 检查是否包含动态参数
            if not has_dynamic_params(job.config_xml):
                logger.warning(f"Job [{job.name}] 不包含动态参数，直接构建")
                # 直接构建（无需替换）
                return build_job(job.name)
            
            # 3. 验证参数完整性
            if validate_missing:
                missing_params = get_missing_params(job.config_xml, build_params)
                if missing_params:
                    error_msg = f"缺少必需参数: {', '.join(missing_params)}"
                    logger.error(error_msg)
                    raise ValueError(error_msg)
            
            # 🔥 4. 判断参数类型，选择构建方式
            if has_jenkins_native_params(job.config_xml):
                # 方式 A: Jenkins 原生参数化构建（推荐）
                logger.info(f"检测到 Jenkins 原生参数，使用参数化构建 API")
                logger.info(f"构建参数: {build_params}")
                
                # 直接调用 Jenkins 参数化构建 API
                build_success, build_msg, build_data = build_job(job.name, parameters=build_params)
                
                if build_success:
                    logger.info(f"Job [{job.name}] 参数化构建触发成功")
                    return True, "参数化构建已触发", build_data
                else:
                    logger.error(f"触发构建失败: {build_msg}")
                    return False, f"触发构建失败: {build_msg}", None
            else:
                # 方式 B: 动态插槽（{{}} 占位符）
                logger.info(f"检测到动态插槽 {{}}, 更新配置后构建")
                logger.debug(f"开始替换参数: {build_params}")
                
                # 替换 XML 中的占位符
                new_xml = replace_params(job.config_xml, build_params)
                
                # 更新 Jenkins Job 配置
                logger.info(f"更新 Job [{job.name}] 的配置...")
                update_success, update_msg, _ = update_job(job.name, new_xml)
                
                if not update_success:
                    error_msg = f"更新 Job 配置失败: {update_msg}"
                    logger.error(error_msg)
                    raise Exception(error_msg)
                
                logger.info(f"Job 配置更新成功，开始触发构建")
                
                # 触发构建（不带参数）
                build_success, build_msg, build_data = build_job(job.name)
                
                if build_success:
                    logger.info(f"Job [{job.name}] 构建触发成功")
                    return True, "参数化构建已触发", build_data
                else:
                    logger.error(f"触发构建失败: {build_msg}")
                    return False, f"触发构建失败: {build_msg}", None
                
        except JenkinsJob.DoesNotExist:
            error_msg = f"Job ID {job_id} 不存在"
            logger.error(error_msg)
            return False, error_msg, None
            
        except ValueError as e:
            # 参数验证失败
            logger.error(f"参数验证失败: {str(e)}")
            return False, str(e), None
            
        except Exception as e:
            # 其他异常
            logger.error(f"参数化构建失败: {str(e)}", exc_info=True)
            return False, f"构建失败: {str(e)}", None
    
    @staticmethod
    def preview_replaced_xml(job_id: int, build_params: Dict[str, str]) -> str:
        """
        预览参数替换后的 XML（用于调试）
        
        Args:
            job_id: Job ID
            build_params: 参数字典
            
        Returns:
            str: 替换后的 XML
        """
        from ..models import JenkinsJob
        from ..utils.param_parser import replace_params
        
        job = JenkinsJob.objects.get(id=job_id)
        return replace_params(job.config_xml, build_params)
    
    @staticmethod
    def validate_build_params(
        job_id: int, 
        build_params: Dict[str, str]
    ) -> Tuple[bool, List[str]]:
        """
        验证构建参数是否完整
        
        Args:
            job_id: Job ID
            build_params: 参数字典
            
        Returns:
            tuple: (is_valid, missing_params)
                - is_valid: True 表示参数完整
                - missing_params: 缺失的参数列表
        """
        from ..models import JenkinsJob
        from ..utils.param_parser import get_missing_params
        
        try:
            job = JenkinsJob.objects.get(id=job_id)
            missing = get_missing_params(job.config_xml, build_params)
            return len(missing) == 0, missing
        except JenkinsJob.DoesNotExist:
            return False, []
