#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Jenkins 节点添加脚本
用于通过 python-jenkins 库向 Jenkins 服务器添加新的节点
"""

import jenkins
import argparse
import json
import sys


class JenkinsNodeAdder:
    """Jenkins 节点添加器"""
    
    def __init__(self, url, username, password):
        """
        初始化 Jenkins 连接
        
        Args:
            url: Jenkins 服务器 URL
            username: Jenkins 用户名
            password: Jenkins 密码或 API Token
        """
        self.server = jenkins.Jenkins(url, username=username, password=password)
        
    def add_node(self, node_config):
        """
        添加新的 Jenkins 节点
        
        Args:
            node_config: 节点配置字典，包含以下字段：
                - name: 节点名称 (必需)
                - host: 节点主机地址 (必需)
                - description: 节点描述 (可选)
                - remote_fs: 远程工作目录 (可选，默认: /home/jenkins)
                - labels: 节点标签 (可选)
                - num_executors: 执行器数量 (可选，默认: 2)
                - exclusive: 是否独占 (可选，默认: False)
                - port: SSH 端口 (可选，默认: 22)
                - credentials_id: Jenkins 凭证 ID (可选)
                - username: SSH 用户名 (可选)
        
        Returns:
            bool: 添加成功返回 True，失败返回 False
        """
        # 提取配置参数
        name = node_config.get('name')
        host = node_config.get('host')
        
        if not name or not host:
            print("错误: 节点名称和主机地址是必需的")
            return False
        
        # 检查节点是否已存在
        try:
            existing_node = self.server.get_node_info(name)
            print(f"警告: 节点 '{name}' 已存在")
            return False
        except jenkins.JenkinsException:
            # 节点不存在，继续创建
            pass
        
        # 配置参数
        node_description = node_config.get('description', f'Jenkins Node: {name}')
        remote_fs = node_config.get('remote_fs', '/home/jenkins')
        labels = node_config.get('labels', '')
        num_executors = node_config.get('num_executors', 2)
        exclusive = node_config.get('exclusive', False)
        
        # SSH 启动器参数
        launcher_params = {
            'host': host,
            'port': str(node_config.get('port', 22)),
        }
        
        # 添加凭证 ID（如果提供）
        if 'credentials_id' in node_config:
            launcher_params['credentialsId'] = node_config['credentials_id']
        
        # 添加用户名（如果提供）
        if 'username' in node_config:
            launcher_params['username'] = node_config['username']
        
        try:
            # 创建节点
            self.server.create_node(
                name=name,
                numExecutors=num_executors,
                nodeDescription=node_description,
                remoteFS=remote_fs,
                labels=labels,
                exclusive=exclusive,
                launcher=jenkins.LAUNCHER_SSH,
                launcher_params=launcher_params
            )
            
            print(f"✓ 成功添加节点: {name}")
            print(f"  主机: {host}")
            print(f"  标签: {labels}")
            print(f"  远程目录: {remote_fs}")
            print(f"  执行器数量: {num_executors}")
            return True
            
        except Exception as e:
            print(f"✗ 添加节点失败: {str(e)}")
            return False
    
    def get_node_info(self, name):
        """
        获取节点信息
        
        Args:
            name: 节点名称
        
        Returns:
            dict: 节点信息
        """
        try:
            return self.server.get_node_info(name)
        except jenkins.JenkinsException as e:
            print(f"错误: 无法获取节点信息 - {str(e)}")
            return None
    
    def list_nodes(self):
        """
        列出所有节点
        
        Returns:
            list: 节点列表
        """
        try:
            nodes = self.server.get_nodes()
            print(f"\n当前 Jenkins 节点列表 (共 {len(nodes)} 个):")
            print("-" * 60)
            for node in nodes:
                status = "离线" if node.get('offline') else "在线"
                print(f"  • {node['name']} - {status}")
            return nodes
        except Exception as e:
            print(f"错误: 无法获取节点列表 - {str(e)}")
            return []


def load_jenkins_config(config_file='jenkins_nodes_config.json'):
    """
    从配置文件加载 Jenkins 连接信息
    
    Args:
        config_file: 配置文件路径
        
    Returns:
        Jenkins 连接配置字典
    """
    try:
        from pathlib import Path
        config_path = Path(__file__).parent / config_file
        
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('jenkins', {})
    except Exception as e:
        print(f"警告: 无法加载配置文件 {config_file}: {e}")
    
    return {}


def main():
    """主函数"""
    # 尝试加载默认配置
    default_jenkins_config = load_jenkins_config()
    
    parser = argparse.ArgumentParser(
        description='Jenkins 节点添加工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例：
  # 使用默认配置添加节点（从 jenkins_nodes_config.json 读取 Jenkins 连接信息）
  python add_jenkins_node.py --name build-node-01 --host 192.168.1.100 --labels "linux docker" --credentials-id aliyun

  # 指定 Jenkins 连接信息
  python add_jenkins_node.py --url http://jenkins.example.com --username admin --password token --name node-01 --host 192.168.1.100

  # 从配置文件添加节点
  python add_jenkins_node.py --config node_config.json

  # 列出所有节点
  python add_jenkins_node.py --list

Jenkins 连接配置文件 (jenkins_nodes_config.json):
{
    "jenkins": {
        "url": "http://jenkins.example.com",
        "username": "admin",
        "password": "admin123"
    }
}

节点配置文件示例 (node_config.json):
{
    "name": "build-node-01",
    "host": "192.168.1.100",
    "description": "Build server for production",
    "remote_fs": "/home/jenkins",
    "labels": "linux docker",
    "num_executors": 4,
    "exclusive": true,
    "port": 22,
    "credentials_id": "ssh-credentials-id",
    "username": "jenkins"
}
        """
    )
    
    # Jenkins 连接参数（可选，会从配置文件读取默认值）
    parser.add_argument('--url', help=f'Jenkins 服务器 URL (默认: {default_jenkins_config.get("url", "从配置文件读取")})')
    parser.add_argument('--username', help=f'Jenkins 用户名 (默认: {default_jenkins_config.get("username", "从配置文件读取")})')
    parser.add_argument('--password', help=f'Jenkins 密码或 API Token (默认: 从配置文件读取)')
    parser.add_argument('--config', help='节点配置 JSON 文件路径')
    parser.add_argument('--list', action='store_true', help='列出所有节点')
    
    # 交互式参数
    parser.add_argument('--name', help='节点名称')
    parser.add_argument('--host', help='节点主机地址')
    parser.add_argument('--description', help='节点描述')
    parser.add_argument('--remote-fs', help='远程工作目录')
    parser.add_argument('--labels', help='节点标签（空格分隔）')
    parser.add_argument('--executors', type=int, help='执行器数量')
    parser.add_argument('--exclusive', action='store_true', help='是否独占节点')
    parser.add_argument('--port', type=int, help='SSH 端口')
    parser.add_argument('--credentials-id', help='Jenkins 凭证 ID')
    parser.add_argument('--ssh-username', help='SSH 用户名')
    
    args = parser.parse_args()
    
    try:
        # 获取 Jenkins 连接参数（命令行参数优先，否则使用配置文件）
        jenkins_url = args.url or default_jenkins_config.get('url')
        jenkins_username = args.username or default_jenkins_config.get('username')
        jenkins_password = args.password or default_jenkins_config.get('password')
        
        # 检查必需参数
        if not jenkins_url or not jenkins_username or not jenkins_password:
            print("错误: 缺少 Jenkins 连接信息")
            print("请提供 --url, --username, --password 参数，")
            print("或在 jenkins_nodes_config.json 文件中配置默认值。")
            return 1
        
        # 创建 Jenkins 节点添加器
        adder = JenkinsNodeAdder(jenkins_url, jenkins_username, jenkins_password)
        
        # 如果只是列出节点
        if args.list:
            adder.list_nodes()
            return 0
        
        # 从配置文件加载
        if args.config:
            with open(args.config, 'r', encoding='utf-8') as f:
                node_config = json.load(f)
            
            if adder.add_node(node_config):
                return 0
            else:
                return 1
        
        # 交互式添加
        if args.name and args.host:
            node_config = {
                'name': args.name,
                'host': args.host,
            }
            
            if args.description:
                node_config['description'] = args.description
            if args.remote_fs:
                node_config['remote_fs'] = args.remote_fs
            if args.labels:
                node_config['labels'] = args.labels
            if args.executors:
                node_config['num_executors'] = args.executors
            if args.exclusive:
                node_config['exclusive'] = True
            if args.port:
                node_config['port'] = args.port
            if args.credentials_id:
                node_config['credentials_id'] = args.credentials_id
            if args.ssh_username:
                node_config['username'] = args.ssh_username
            
            if adder.add_node(node_config):
                return 0
            else:
                return 1
        
        # 如果没有提供足够的参数
        print("错误: 请提供 --config 配置文件，或使用 --name 和 --host 参数")
        print("使用 --help 查看详细用法")
        return 1
        
    except Exception as e:
        print(f"错误: {str(e)}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
