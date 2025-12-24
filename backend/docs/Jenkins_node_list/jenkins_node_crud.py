#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Jenkins 节点 CRUD 管理模块
提供完整的节点增删改查功能
"""

import jenkins
import json
import xml.etree.ElementTree as ET
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class JenkinsNodeCRUD:
    """Jenkins 节点 CRUD 管理器"""
    
    def __init__(self, jenkins_url: str, username: str, password: str):
        """
        初始化 Jenkins 连接
        
        Args:
            jenkins_url: Jenkins 服务器地址
            username: Jenkins 用户名
            password: Jenkins 密码或 API Token
        """
        self.url = jenkins_url
        self.username = username
        self.password = password
        
        # 初始化 Jenkins 连接
        self.server = jenkins.Jenkins(
            jenkins_url,
            username=username,
            password=password
        )
        
        # 测试连接
        try:
            user = self.server.get_whoami()
            version = self.server.get_version()
            logger.info(f"✓ 已连接到 Jenkins {version}")
            logger.info(f"✓ 当前用户: {user['fullName']}")
        except Exception as e:
            logger.error(f"✗ 连接 Jenkins 失败: {e}")
            raise
    
    # ==================== 查询功能 (Read) ====================
    
    def list_nodes(self, include_master: bool = True) -> List[Dict[str, Any]]:
        """
        获取所有节点列表
        
        Args:
            include_master: 是否包含主节点
            
        Returns:
            节点列表
        """
        try:
            nodes = self.server.get_nodes()
            
            if not include_master:
                nodes = [n for n in nodes if n.get('name') != 'master']
            
            logger.info(f"找到 {len(nodes)} 个节点")
            return nodes
        except Exception as e:
            logger.error(f"获取节点列表失败: {e}")
            return []
    
    def get_node_info(self, node_name: str, depth: int = 1) -> Optional[Dict[str, Any]]:
        """
        获取节点详细信息
        
        Args:
            node_name: 节点名称
            depth: 查询深度
            
        Returns:
            节点信息字典
        """
        try:
            node_info = self.server.get_node_info(node_name, depth=depth)
            logger.info(f"成功获取节点 '{node_name}' 信息")
            return node_info
        except jenkins.JenkinsException as e:
            logger.error(f"获取节点 '{node_name}' 信息失败: {e}")
            return None
    
    def get_node_config(self, node_name: str) -> Optional[str]:
        """
        获取节点 XML 配置
        
        Args:
            node_name: 节点名称
            
        Returns:
            节点配置 XML 字符串
        """
        try:
            config_xml = self.server.get_node_config(node_name)
            logger.info(f"成功获取节点 '{node_name}' 配置")
            return config_xml
        except Exception as e:
            logger.error(f"获取节点配置失败: {e}")
            return None
    
    def get_node_ip(self, node_name: str) -> Optional[str]:
        """
        获取节点当前的 IP 地址
        
        Args:
            node_name: 节点名称
            
        Returns:
            当前 IP 地址
        """
        try:
            config_xml = self.get_node_config(node_name)
            if not config_xml:
                return None
            
            root = ET.fromstring(config_xml)
            
            # 查找 SSH 主机 IP
            host_elem = root.find(".//host")
            if host_elem is not None and host_elem.text:
                logger.info(f"节点 '{node_name}' 当前 IP: {host_elem.text}")
                return host_elem.text
            
            logger.warning(f"未找到节点 '{node_name}' 的 IP 配置")
            return None
            
        except Exception as e:
            logger.error(f"获取节点 IP 失败: {e}")
            return None
    
    def node_exists(self, node_name: str) -> bool:
        """
        检查节点是否存在
        
        Args:
            node_name: 节点名称
            
        Returns:
            节点是否存在
        """
        try:
            return self.server.node_exists(node_name)
        except Exception as e:
            logger.error(f"检查节点存在失败: {e}")
            return False
    
    # ==================== 创建功能 (Create) ====================
    
    def create_ssh_node(
        self,
        name: str,
        host: str,
        credential_id: str = '',
        port: int = 22,
        remote_fs: str = '/home/jenkins',
        labels: str = '',
        num_executors: int = 2,
        description: str = ''
    ) -> bool:
        """
        创建 SSH 连接节点
        
        Args:
            name: 节点名称
            host: 主机 IP 或域名
            credential_id: SSH 凭证 ID
            port: SSH 端口
            remote_fs: 远程工作目录
            labels: 节点标签(空格分隔)
            num_executors: 执行器数量
            description: 节点描述
            
        Returns:
            创建是否成功
        """
        # 检查节点是否已存在
        if self.node_exists(name):
            logger.error(f"节点 '{name}' 已存在")
            return False
        
        # 构建 SSH 节点配置 XML
        config_xml = self._build_ssh_node_config(
            host=host,
            credential_id=credential_id,
            port=port,
            remote_fs=remote_fs,
            labels=labels,
            num_executors=num_executors,
            description=description
        )
        
        try:
            # 创建节点
            self.server.create_node(
                name=name,
                numExecutors=num_executors,
                nodeDescription=description,
                remoteFS=remote_fs,
                labels=labels,
                exclusive=False
            )
            
            # 更新为自定义的 SSH 配置
            self.server.reconfig_node(name, config_xml)
            
            logger.info(f"✓ 成功创建节点 '{name}'")
            logger.info(f"  - 主机: {host}:{port}")
            logger.info(f"  - 标签: {labels}")
            logger.info(f"  - 执行器: {num_executors}")
            
            return True
            
        except Exception as e:
            logger.error(f"创建节点 '{name}' 失败: {e}")
            # 尝试清理已创建的节点
            try:
                if self.node_exists(name):
                    self.delete_node(name)
            except:
                pass
            return False
    
    def create_node_from_config(self, name: str, config_xml: str) -> bool:
        """
        从 XML 配置创建节点
        
        Args:
            name: 节点名称
            config_xml: 节点配置 XML
            
        Returns:
            创建是否成功
        """
        if self.node_exists(name):
            logger.error(f"节点 '{name}' 已存在")
            return False
        
        try:
            # 解析 XML 获取基本参数
            root = ET.fromstring(config_xml)
            num_executors = int(root.find('.//numExecutors').text or 2)
            remote_fs = root.find('.//remoteFS').text or '/home/jenkins'
            
            # 先创建基本节点
            self.server.create_node(
                name=name,
                numExecutors=num_executors,
                remoteFS=remote_fs
            )
            
            # 应用完整配置
            self.server.reconfig_node(name, config_xml)
            
            logger.info(f"✓ 成功从配置创建节点 '{name}'")
            return True
            
        except Exception as e:
            logger.error(f"从配置创建节点失败: {e}")
            return False
    
    # ==================== 更新功能 (Update) ====================
    
    def update_node_ip(self, node_name: str, new_ip: str, port: Optional[int] = None) -> bool:
        """
        更新节点的主机 IP 地址
        
        Args:
            node_name: 节点名称
            new_ip: 新的 IP 地址
            port: SSH 端口(可选)
            
        Returns:
            更新是否成功
        """
        try:
            logger.info(f"开始更新节点 '{node_name}' 的 IP 地址")
            
            # 获取当前节点配置
            config_xml = self.get_node_config(node_name)
            if not config_xml:
                return False
            
            # 解析 XML
            root = ET.fromstring(config_xml)
            
            updated = False
            
            # 更新 SSH 主机 IP
            host_elements = root.findall(".//host")
            for host_elem in host_elements:
                old_ip = host_elem.text
                if old_ip != new_ip:
                    host_elem.text = new_ip
                    updated = True
                    logger.info(f"✓ 更新 SSH 主机 IP: {old_ip} → {new_ip}")
            
            # 更新端口
            if port:
                port_elements = root.findall(".//port")
                for port_elem in port_elements:
                    old_port = port_elem.text
                    if old_port != str(port):
                        port_elem.text = str(port)
                        updated = True
                        logger.info(f"✓ 更新 SSH 端口: {old_port} → {port}")
            
            if not updated:
                logger.warning("未找到需要更新的配置")
                return False
            
            # 应用更新
            updated_config = ET.tostring(root, encoding='unicode')
            self.server.reconfig_node(node_name, updated_config)
            
            logger.info(f"✓ 节点 '{node_name}' IP 地址更新完成")
            return True
            
        except Exception as e:
            logger.error(f"更新节点 IP 失败: {e}")
            return False
    
    def update_node_config(self, node_name: str, config_xml: str) -> bool:
        """
        更新节点完整配置
        
        Args:
            node_name: 节点名称
            config_xml: 新的配置 XML
            
        Returns:
            更新是否成功
        """
        try:
            self.server.reconfig_node(node_name, config_xml)
            logger.info(f"✓ 成功更新节点 '{node_name}' 配置")
            return True
        except Exception as e:
            logger.error(f"更新节点配置失败: {e}")
            return False
    
    def update_node_labels(self, node_name: str, labels: str) -> bool:
        """
        更新节点标签
        
        Args:
            node_name: 节点名称
            labels: 新的标签(空格分隔)
            
        Returns:
            更新是否成功
        """
        try:
            config_xml = self.get_node_config(node_name)
            if not config_xml:
                return False
            
            root = ET.fromstring(config_xml)
            
            # 更新标签
            label_elem = root.find('.//label')
            if label_elem is not None:
                label_elem.text = labels
            else:
                # 如果不存在标签元素,创建一个
                label_elem = ET.SubElement(root, 'label')
                label_elem.text = labels
            
            updated_config = ET.tostring(root, encoding='unicode')
            self.server.reconfig_node(node_name, updated_config)
            
            logger.info(f"✓ 成功更新节点 '{node_name}' 标签: {labels}")
            return True
            
        except Exception as e:
            logger.error(f"更新节点标签失败: {e}")
            return False
    
    # ==================== 删除功能 (Delete) ====================
    
    def delete_node(self, node_name: str, force: bool = False) -> bool:
        """
        删除指定节点
        
        Args:
            node_name: 节点名称
            force: 是否强制删除(跳过确认)
            
        Returns:
            删除是否成功
        """
        if not self.node_exists(node_name):
            logger.error(f"节点 '{node_name}' 不存在")
            return False
        
        try:
            self.server.delete_node(node_name)
            logger.info(f"✓ 成功删除节点 '{node_name}'")
            return True
        except Exception as e:
            logger.error(f"删除节点 '{node_name}' 失败: {e}")
            return False
    
    def batch_delete_nodes(self, node_names: List[str]) -> Dict[str, bool]:
        """
        批量删除节点
        
        Args:
            node_names: 节点名称列表
            
        Returns:
            每个节点的删除结果
        """
        results = {}
        
        logger.info(f"开始批量删除 {len(node_names)} 个节点")
        
        for node_name in node_names:
            results[node_name] = self.delete_node(node_name, force=True)
        
        success_count = sum(1 for s in results.values() if s)
        logger.info(f"批量删除完成: {success_count}/{len(node_names)} 成功")
        
        return results
    
    # ==================== 辅助功能 ====================
    
    def enable_node(self, node_name: str) -> bool:
        """启用节点"""
        try:
            self.server.enable_node(node_name)
            logger.info(f"✓ 成功启用节点 '{node_name}'")
            return True
        except Exception as e:
            logger.error(f"启用节点失败: {e}")
            return False
    
    def disable_node(self, node_name: str, message: str = '') -> bool:
        """禁用节点"""
        try:
            self.server.disable_node(node_name, message)
            logger.info(f"✓ 成功禁用节点 '{node_name}'")
            return True
        except Exception as e:
            logger.error(f"禁用节点失败: {e}")
            return False
    
    def reconnect_node(self, node_name: str) -> bool:
        """重新连接节点"""
        import time
        
        try:
            logger.info(f"开始重新连接节点 '{node_name}'")
            
            # 先禁用
            self.disable_node(node_name)
            time.sleep(2)
            
            # 再启用
            self.enable_node(node_name)
            time.sleep(3)
            
            # 检查状态
            node_info = self.get_node_info(node_name)
            if node_info and not node_info.get('offline', True):
                logger.info(f"✓ 节点 '{node_name}' 已在线")
                return True
            else:
                logger.warning(f"⚠ 节点 '{node_name}' 仍然离线")
                return False
                
        except Exception as e:
            logger.error(f"重新连接节点失败: {e}")
            return False
    
    # ==================== 私有辅助方法 ====================
    
    def _build_ssh_node_config(
        self,
        host: str,
        credential_id: str,
        port: int,
        remote_fs: str,
        labels: str,
        num_executors: int,
        description: str
    ) -> str:
        """构建 SSH 节点配置 XML"""
        
        config_template = f'''<?xml version="1.1" encoding="UTF-8"?>
<slave>
  <name>{{name}}</name>
  <description>{description}</description>
  <remoteFS>{remote_fs}</remoteFS>
  <numExecutors>{num_executors}</numExecutors>
  <mode>NORMAL</mode>
  <retentionStrategy class="hudson.slaves.RetentionStrategy$Always"/>
  <launcher class="hudson.plugins.sshslaves.SSHLauncher" plugin="ssh-slaves@2.854.v7fd446b_337c9">
    <host>{host}</host>
    <port>{port}</port>
    <credentialsId>{credential_id}</credentialsId>
    <launchTimeoutSeconds>60</launchTimeoutSeconds>
    <maxNumRetries>10</maxNumRetries>
    <retryWaitTime>15</retryWaitTime>
    <sshHostKeyVerificationStrategy class="hudson.plugins.sshslaves.verifiers.NonVerifyingKeyVerificationStrategy"/>
    <tcpNoDelay>true</tcpNoDelay>
  </launcher>
  <label>{labels}</label>
  <nodeProperties/>
</slave>'''
        
        return config_template


def load_config(config_file: str = 'jenkins_nodes_config.json') -> Dict[str, Any]:
    """
    从配置文件加载配置
    
    Args:
        config_file: 配置文件路径
        
    Returns:
        配置字典
    """
    try:
        config_path = Path(__file__).parent / config_file
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"加载配置文件失败: {e}")
        return {}


if __name__ == "__main__":
    # 简单测试
    print("Jenkins 节点 CRUD 管理模块")
    print("使用示例请参考 jenkins_node_cli.py")
