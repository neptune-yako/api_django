#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Jenkins 节点 IP 地址更新工具
基于 python-jenkins 框架远程修改 Jenkins 节点的主机 IP
"""

import jenkins
import xml.etree.ElementTree as ET
import argparse
import logging
from typing import Optional, Dict, Any

# Jenkins 配置
JENKINS_URL = 'http://mg.morry.online'
USERNAME = 'admin'
PASSWORD = 'admin123'

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class JenkinsNodeIPUpdater:
    """Jenkins 节点 IP 地址更新器"""
    
    def __init__(self, jenkins_url: str = JENKINS_URL, 
                 username: str = USERNAME, 
                 password: str = PASSWORD):
        """
        初始化 Jenkins 连接
        
        Args:
            jenkins_url: Jenkins 服务器地址
            username: Jenkins 用户名
            password: Jenkins 密码或 API Token
        """
        self.server = jenkins.Jenkins(
            jenkins_url,
            username=username,
            password=password
        )
        
        # 测试连接
        try:
            user = self.server.get_whoami()
            logger.info(f"✓ 已连接到 Jenkins,当前用户: {user['fullName']}")
        except Exception as e:
            logger.error(f"✗ 连接 Jenkins 失败: {e}")
            raise
    
    def list_all_nodes(self) -> list:
        """
        获取所有节点列表
        
        Returns:
            节点列表
        """
        try:
            nodes = self.server.get_nodes()
            logger.info(f"找到 {len(nodes)} 个节点")
            return nodes
        except Exception as e:
            logger.error(f"获取节点列表失败: {e}")
            return []
    
    def get_node_info(self, node_name: str) -> Dict[str, Any]:
        """
        获取节点详细信息
        
        Args:
            node_name: 节点名称
            
        Returns:
            节点信息字典
        """
        try:
            node_info = self.server.get_node_info(node_name)
            logger.info(f"节点 '{node_name}' 信息:")
            logger.info(f"  - 离线状态: {node_info.get('offline', 'Unknown')}")
            logger.info(f"  - 临时离线: {node_info.get('temporarilyOffline', 'Unknown')}")
            return node_info
        except jenkins.JenkinsException as e:
            logger.error(f"获取节点 '{node_name}' 信息失败: {e}")
            raise
    
    def get_node_current_ip(self, node_name: str) -> Optional[str]:
        """
        获取节点当前的 IP 地址
        
        Args:
            node_name: 节点名称
            
        Returns:
            当前 IP 地址,如果未找到则返回 None
        """
        try:
            config_xml = self.server.get_node_config(node_name)
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
    
    def update_node_ip(self, node_name: str, new_ip: str, 
                      ssh_port: Optional[int] = None) -> bool:
        """
        更新节点的主机 IP 地址
        
        Args:
            node_name: 节点名称
            new_ip: 新的 IP 地址
            ssh_port: SSH 端口(可选,默认保持不变)
            
        Returns:
            更新是否成功
        """
        try:
            logger.info(f"\n{'='*60}")
            logger.info(f"开始更新节点 '{node_name}' 的 IP 地址")
            logger.info(f"{'='*60}")
            
            # 获取当前节点配置
            config_xml = self.server.get_node_config(node_name)
            
            # 解析 XML
            root = ET.fromstring(config_xml)
            
            # 标记是否有更新
            updated = False
            
            # 1. 更新 SSH 主机 IP(对于 SSH 连接节点)
            host_elements = root.findall(".//host")
            for host_elem in host_elements:
                old_ip = host_elem.text
                if old_ip != new_ip:
                    host_elem.text = new_ip
                    updated = True
                    logger.info(f"✓ 更新 SSH 主机 IP: {old_ip} → {new_ip}")
                else:
                    logger.info(f"IP 地址已经是 {new_ip},无需更新")
            
            # 2. 更新端口(如果指定)
            if ssh_port:
                port_elements = root.findall(".//port")
                for port_elem in port_elements:
                    old_port = port_elem.text
                    if old_port != str(ssh_port):
                        port_elem.text = str(ssh_port)
                        updated = True
                        logger.info(f"✓ 更新 SSH 端口: {old_port} → {ssh_port}")
            
            # 3. 更新 JNLP tunnel(对于 JNLP 连接节点)
            tunnel_elements = root.findall(".//tunnel")
            for tunnel_elem in tunnel_elements:
                if tunnel_elem.text and ":" in tunnel_elem.text:
                    parts = tunnel_elem.text.split(":")
                    if len(parts) == 2:
                        old_tunnel = tunnel_elem.text
                        port = parts[1]
                        tunnel_elem.text = f"{new_ip}:{port}"
                        updated = True
                        logger.info(f"✓ 更新 JNLP tunnel: {old_tunnel} → {new_ip}:{port}")
            
            # 如果没有找到任何需要更新的元素
            if not updated:
                logger.warning(f"未找到需要更新的 IP 配置元素")
                logger.warning(f"请检查节点是否使用 SSH 或 JNLP 启动器")
                return False
            
            # 将更新后的配置转换回字符串
            updated_config = ET.tostring(root, encoding='unicode')
            
            # 应用更新
            self.server.reconfig_node(node_name, updated_config)
            logger.info(f"✓ 成功应用节点配置更新")
            
            # 验证更新
            self._verify_update(node_name, new_ip)
            
            logger.info(f"{'='*60}")
            logger.info(f"✓ 节点 '{node_name}' IP 地址更新完成!")
            logger.info(f"{'='*60}\n")
            
            return True
            
        except ET.ParseError as e:
            logger.error(f"✗ 解析 XML 配置失败: {e}")
            return False
        except jenkins.JenkinsException as e:
            logger.error(f"✗ Jenkins API 错误: {e}")
            return False
        except Exception as e:
            logger.error(f"✗ 未预期的错误: {e}")
            return False
    
    def _verify_update(self, node_name: str, expected_ip: str) -> None:
        """
        验证更新是否成功
        
        Args:
            node_name: 节点名称
            expected_ip: 期望的 IP 地址
        """
        try:
            # 重新获取配置并验证
            config_xml = self.server.get_node_config(node_name)
            root = ET.fromstring(config_xml)
            
            verified = False
            
            # 检查 SSH 主机
            host_elements = root.findall(".//host")
            for host_elem in host_elements:
                if host_elem.text == expected_ip:
                    logger.info(f"✓ 验证通过: SSH 主机 IP 是 {expected_ip}")
                    verified = True
                else:
                    logger.warning(f"⚠ 验证失败: SSH 主机 IP 是 {host_elem.text}")
            
            # 检查 JNLP tunnel
            tunnel_elements = root.findall(".//tunnel")
            for tunnel_elem in tunnel_elements:
                if tunnel_elem.text and expected_ip in tunnel_elem.text:
                    logger.info(f"✓ 验证通过: JNLP tunnel 包含 {expected_ip}")
                    verified = True
                elif tunnel_elem.text:
                    logger.warning(f"⚠ 验证失败: JNLP tunnel 是 {tunnel_elem.text}")
            
            if not verified:
                logger.warning("⚠ 未找到可验证的配置项")
                
        except Exception as e:
            logger.error(f"验证失败: {e}")
    
    def reconnect_node(self, node_name: str) -> bool:
        """
        重新连接节点(更新 IP 后可能需要)
        
        Args:
            node_name: 节点名称
            
        Returns:
            重新连接是否成功
        """
        try:
            import time
            
            logger.info(f"\n开始重新连接节点 '{node_name}'...")
            
            # 先断开连接
            self.server.disable_node(node_name)
            logger.info(f"✓ 已断开节点连接")
            
            # 等待片刻
            time.sleep(2)
            
            # 重新连接
            self.server.enable_node(node_name)
            logger.info(f"✓ 已启用节点")
            
            # 检查状态
            time.sleep(5)  # 等待连接建立
            node_info = self.get_node_info(node_name)
            
            if node_info.get('offline', True):
                logger.warning(f"⚠ 节点 '{node_name}' 仍然离线")
                return False
            else:
                logger.info(f"✓ 节点 '{node_name}' 已在线\n")
                return True
                
        except Exception as e:
            logger.error(f"重新连接节点失败: {e}")
            return False
    
    def batch_update_nodes(self, updates: Dict[str, str], 
                          auto_reconnect: bool = False) -> Dict[str, bool]:
        """
        批量更新多个节点
        
        Args:
            updates: 字典,键为节点名,值为新的 IP 地址
            auto_reconnect: 是否自动重新连接节点
            
        Returns:
            每个节点的更新结果
        """
        results = {}
        
        logger.info(f"\n{'='*60}")
        logger.info(f"开始批量更新 {len(updates)} 个节点")
        logger.info(f"{'='*60}\n")
        
        for node_name, new_ip in updates.items():
            try:
                # 更新 IP
                success = self.update_node_ip(node_name, new_ip)
                
                if success and auto_reconnect:
                    self.reconnect_node(node_name)
                
                results[node_name] = success
                
            except Exception as e:
                logger.error(f"更新节点 '{node_name}' 失败: {e}")
                results[node_name] = False
        
        # 打印汇总结果
        print("\n" + "="*60)
        print("批量更新结果汇总:")
        print("="*60)
        for node, success in results.items():
            status = "✓ 成功" if success else "✗ 失败"
            print(f"  {node:30} {status}")
        
        success_count = sum(1 for s in results.values() if s)
        print(f"\n总计: {len(results)} 个节点, {success_count} 个成功, {len(results)-success_count} 个失败")
        print("="*60 + "\n")
        
        return results


def main():
    """主函数 - 命令行接口"""
    parser = argparse.ArgumentParser(
        description='Jenkins 节点 IP 地址更新工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 列出所有节点
  python update_node_ip.py --list
  
  # 查看节点当前 IP
  python update_node_ip.py --node my-node --show-ip
  
  # 更新单个节点 IP
  python update_node_ip.py --node my-node --ip 192.168.1.100
  
  # 更新节点 IP 和端口
  python update_node_ip.py --node my-node --ip 192.168.1.100 --port 2222
  
  # 更新 IP 并自动重新连接
  python update_node_ip.py --node my-node --ip 192.168.1.100 --reconnect
        """
    )
    
    parser.add_argument('--url', default=JENKINS_URL, 
                       help=f'Jenkins 服务器地址 (默认: {JENKINS_URL})')
    parser.add_argument('--user', default=USERNAME, 
                       help=f'Jenkins 用户名 (默认: {USERNAME})')
    parser.add_argument('--password', default=PASSWORD, 
                       help='Jenkins 密码或 API Token')
    
    parser.add_argument('--list', action='store_true', 
                       help='列出所有节点')
    parser.add_argument('--node', help='节点名称')
    parser.add_argument('--show-ip', action='store_true', 
                       help='显示节点当前 IP')
    parser.add_argument('--ip', help='新的 IP 地址')
    parser.add_argument('--port', type=int, help='SSH 端口 (可选)')
    parser.add_argument('--reconnect', action='store_true', 
                       help='更新后重新连接节点')
    
    args = parser.parse_args()
    
    # 创建更新器实例
    try:
        updater = JenkinsNodeIPUpdater(args.url, args.user, args.password)
    except Exception as e:
        logger.error(f"初始化失败: {e}")
        return 1
    
    # 列出所有节点
    if args.list:
        nodes = updater.list_all_nodes()
        print("\nJenkins 节点列表:")
        print("="*60)
        for node in nodes:
            print(f"  - {node['name']}")
        print("="*60 + "\n")
        return 0
    
    # 需要指定节点名称
    if not args.node:
        parser.error("请使用 --node 指定节点名称,或使用 --list 列出所有节点")
        return 1
    
    # 显示节点当前 IP
    if args.show_ip:
        current_ip = updater.get_node_current_ip(args.node)
        if current_ip:
            print(f"\n节点 '{args.node}' 当前 IP: {current_ip}\n")
        return 0
    
    # 更新节点 IP
    if args.ip:
        success = updater.update_node_ip(args.node, args.ip, args.port)
        
        if success and args.reconnect:
            updater.reconnect_node(args.node)
        
        return 0 if success else 1
    
    # 如果没有指定操作,显示节点信息
    updater.get_node_info(args.node)
    updater.get_node_current_ip(args.node)
    return 0


if __name__ == "__main__":
    exit(main())
