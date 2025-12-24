#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Jenkins 节点管理命令行工具
提供友好的 CLI 界面进行节点 CRUD 操作
"""

import argparse
import sys
import json
from pathlib import Path
from jenkins_node_crud import JenkinsNodeCRUD, load_config


def print_header(title: str):
    """打印标题"""
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def print_node_list(nodes: list):
    """打印节点列表"""
    if not nodes:
        print("未找到任何节点")
        return
    
    print(f"\n找到 {len(nodes)} 个节点:\n")
    print(f"{'序号':<6} {'节点名称':<25} {'状态':<10} {'执行器':<8}")
    print("-" * 60)
    
    for i, node in enumerate(nodes, 1):
        name = node.get('name', 'N/A')
        offline = node.get('offline', False)
        status = "❌ 离线" if offline else "✅ 在线"
        executors = node.get('numExecutors', 0)
        
        print(f"{i:<6} {name:<25} {status:<10} {executors:<8}")
    
    print("-" * 60)


def print_node_detail(node_info: dict):
    """打印节点详细信息"""
    if not node_info:
        print("❌ 未获取到节点信息")
        return
    
    print("\n节点详细信息:")
    print("-" * 60)
    print(f"节点名称: {node_info.get('displayName', 'N/A')}")
    print(f"描述: {node_info.get('nodeDescription', 'N/A')}")
    print(f"远程目录: {node_info.get('remoteFS', 'N/A')}")
    print(f"执行器数量: {node_info.get('numExecutors', 0)}")
    print(f"在线状态: {'✅ 在线' if not node_info.get('offline', True) else '❌ 离线'}")
    print(f"空闲状态: {'✅ 空闲' if node_info.get('idle', False) else '⚠ 忙碌'}")
    
    # 标签信息
    labels = node_info.get('assignedLabels', [])
    if labels:
        label_names = [l.get('name', '') for l in labels if l.get('name')]
        print(f"标签: {', '.join(label_names)}")
    
    print("-" * 60)


def cmd_list(manager: JenkinsNodeCRUD, args):
    """列出所有节点"""
    print_header("Jenkins 节点列表")
    nodes = manager.list_nodes(include_master=args.include_master)
    print_node_list(nodes)


def cmd_show(manager: JenkinsNodeCRUD, args):
    """显示节点详细信息"""
    print_header(f"节点详细信息 - {args.name}")
    
    # 获取节点信息
    node_info = manager.get_node_info(args.name, depth=2)
    if node_info:
        print_node_detail(node_info)
        
        # 显示 IP 地址
        if args.show_ip:
            ip = manager.get_node_ip(args.name)
            if ip:
                print(f"\n当前 IP 地址: {ip}")


def cmd_create(manager: JenkinsNodeCRUD, args):
    """创建新节点"""
    print_header(f"创建新节点 - {args.name}")
    
    # 检查节点是否已存在
    if manager.node_exists(args.name):
        print(f"❌ 节点 '{args.name}' 已存在")
        return False
    
    print(f"\n正在创建节点...")
    print(f"  节点名称: {args.name}")
    print(f"  主机地址: {args.host}")
    print(f"  SSH 端口: {args.port}")
    print(f"  远程目录: {args.remote_fs}")
    print(f"  标签: {args.labels}")
    print(f"  执行器: {args.executors}")
    
    success = manager.create_ssh_node(
        name=args.name,
        host=args.host,
        credential_id=args.credential_id,
        port=args.port,
        remote_fs=args.remote_fs,
        labels=args.labels,
        num_executors=args.executors,
        description=args.description
    )
    
    if success:
        print(f"\n✅ 成功创建节点 '{args.name}'")
        return True
    else:
        print(f"\n❌ 创建节点失败")
        return False


def cmd_update_ip(manager: JenkinsNodeCRUD, args):
    """更新节点 IP"""
    print_header(f"更新节点 IP - {args.name}")
    
    # 显示当前 IP
    current_ip = manager.get_node_ip(args.name)
    if current_ip:
        print(f"当前 IP: {current_ip}")
    
    print(f"新 IP: {args.ip}")
    if args.port:
        print(f"新端口: {args.port}")
    
    success = manager.update_node_ip(args.name, args.ip, args.port)
    
    if success:
        print(f"\n✅ 成功更新节点 IP")
        
        # 如果需要重新连接
        if args.reconnect:
            print("\n正在重新连接节点...")
            manager.reconnect_node(args.name)
        
        return True
    else:
        print(f"\n❌ 更新节点 IP 失败")
        return False


def cmd_update_labels(manager: JenkinsNodeCRUD, args):
    """更新节点标签"""
    print_header(f"更新节点标签 - {args.name}")
    
    print(f"新标签: {args.labels}")
    
    success = manager.update_node_labels(args.name, args.labels)
    
    if success:
        print(f"\n✅ 成功更新节点标签")
        return True
    else:
        print(f"\n❌ 更新节点标签失败")
        return False


def cmd_delete(manager: JenkinsNodeCRUD, args):
    """删除节点"""
    print_header(f"删除节点 - {args.name}")
    
    # 检查节点是否存在
    if not manager.node_exists(args.name):
        print(f"❌ 节点 '{args.name}' 不存在")
        return False
    
    # 确认删除
    if not args.force:
        confirm = input(f"\n⚠ 确定要删除节点 '{args.name}' 吗? (yes/no): ")
        if confirm.lower() != 'yes':
            print("已取消删除操作")
            return False
    
    success = manager.delete_node(args.name, force=True)
    
    if success:
        print(f"\n✅ 成功删除节点 '{args.name}'")
        return True
    else:
        print(f"\n❌ 删除节点失败")
        return False


def cmd_enable(manager: JenkinsNodeCRUD, args):
    """启用节点"""
    print_header(f"启用节点 - {args.name}")
    
    success = manager.enable_node(args.name)
    
    if success:
        print(f"\n✅ 成功启用节点")
        return True
    else:
        print(f"\n❌ 启用节点失败")
        return False


def cmd_disable(manager: JenkinsNodeCRUD, args):
    """禁用节点"""
    print_header(f"禁用节点 - {args.name}")
    
    success = manager.disable_node(args.name, args.message)
    
    if success:
        print(f"\n✅ 成功禁用节点")
        return True
    else:
        print(f"\n❌ 禁用节点失败")
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='Jenkins 节点管理 CLI 工具',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # 全局选项
    parser.add_argument('--config', default='jenkins_nodes_config.json',
                       help='配置文件路径')
    parser.add_argument('--url', help='Jenkins URL (覆盖配置文件)')
    parser.add_argument('--user', help='Jenkins 用户名 (覆盖配置文件)')
    parser.add_argument('--password', help='Jenkins 密码 (覆盖配置文件)')
    
    # 子命令
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # list 命令
    parser_list = subparsers.add_parser('list', help='列出所有节点')
    parser_list.add_argument('--include-master', action='store_true',
                            help='包含主节点')
    
    # show 命令
    parser_show = subparsers.add_parser('show', help='显示节点详细信息')
    parser_show.add_argument('name', help='节点名称')
    parser_show.add_argument('--show-ip', action='store_true',
                            help='显示 IP 地址')
    
    # create 命令
    parser_create = subparsers.add_parser('create', help='创建新节点')
    parser_create.add_argument('--name', required=True, help='节点名称')
    parser_create.add_argument('--host', required=True, help='主机 IP 或域名')
    parser_create.add_argument('--port', type=int, default=22, help='SSH 端口')
    parser_create.add_argument('--credential-id', default='', help='SSH 凭证 ID')
    parser_create.add_argument('--remote-fs', default='/home/jenkins',
                              help='远程工作目录')
    parser_create.add_argument('--labels', default='', help='节点标签 (空格分隔)')
    parser_create.add_argument('--executors', type=int, default=2,
                              help='执行器数量')
    parser_create.add_argument('--description', default='', help='节点描述')
    
    # update-ip 命令
    parser_update_ip = subparsers.add_parser('update-ip', help='更新节点 IP')
    parser_update_ip.add_argument('--name', required=True, help='节点名称')
    parser_update_ip.add_argument('--ip', required=True, help='新 IP 地址')
    parser_update_ip.add_argument('--port', type=int, help='新端口')
    parser_update_ip.add_argument('--reconnect', action='store_true',
                                  help='更新后重新连接')
    
    # update-labels 命令
    parser_update_labels = subparsers.add_parser('update-labels',
                                                 help='更新节点标签')
    parser_update_labels.add_argument('--name', required=True, help='节点名称')
    parser_update_labels.add_argument('--labels', required=True,
                                     help='新标签 (空格分隔)')
    
    # delete 命令
    parser_delete = subparsers.add_parser('delete', help='删除节点')
    parser_delete.add_argument('--name', required=True, help='节点名称')
    parser_delete.add_argument('--force', action='store_true',
                              help='强制删除 (跳过确认)')
    
    # enable 命令
    parser_enable = subparsers.add_parser('enable', help='启用节点')
    parser_enable.add_argument('--name', required=True, help='节点名称')
    
    # disable 命令
    parser_disable = subparsers.add_parser('disable', help='禁用节点')
    parser_disable.add_argument('--name', required=True, help='节点名称')
    parser_disable.add_argument('--message', default='', help='禁用原因')
    
    args = parser.parse_args()
    
    # 检查是否指定了命令
    if not args.command:
        parser.print_help()
        return 1
    
    # 加载配置
    config = load_config(args.config)
    
    # 获取 Jenkins 连接信息
    jenkins_config = config.get('jenkins', {})
    url = args.url or jenkins_config.get('url')
    username = args.user or jenkins_config.get('username')
    password = args.password or jenkins_config.get('password')
    
    if not all([url, username, password]):
        print("❌ 缺少 Jenkins 连接信息")
        print("请在配置文件中设置或通过命令行参数提供: --url --user --password")
        return 1
    
    # 创建管理器
    try:
        manager = JenkinsNodeCRUD(url, username, password)
    except Exception as e:
        print(f"❌ 连接 Jenkins 失败: {e}")
        return 1
    
    # 执行命令
    commands = {
        'list': cmd_list,
        'show': cmd_show,
        'create': cmd_create,
        'update-ip': cmd_update_ip,
        'update-labels': cmd_update_labels,
        'delete': cmd_delete,
        'enable': cmd_enable,
        'disable': cmd_disable,
    }
    
    cmd_func = commands.get(args.command)
    if cmd_func:
        try:
            result = cmd_func(manager, args)
            return 0 if result is None or result else 1
        except Exception as e:
            print(f"\n❌ 执行命令时出错: {e}")
            return 1
    else:
        print(f"❌ 未知命令: {args.command}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
