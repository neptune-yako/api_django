#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Jenkins 凭证查询工具 (改进版)
支持多种Jenkins凭证API格式
"""

import requests
import json
import sys
from jenkins_node_crud import load_config


def get_credentials_detailed(jenkins_url, username, password):
    """
    获取凭证详细信息，尝试多种API格式
    """
    base_url = jenkins_url.rstrip('/')
    auth = (username, password)
    
    # API端点列表
    endpoints = [
        ("/credentials/store/system/domain/_/api/json?depth=2", "深度查询"),
        ("/credentials/store/system/domain/_/api/json", "标准查询"),
        ("/credentials/api/json", "简化查询"),
    ]
    
    for endpoint, desc in endpoints:
        url = base_url + endpoint
        
        try:
            response = requests.get(url, auth=auth, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # 检查是否包含凭证信息
                if 'credentials' in data:
                    print(f"✅ 使用 {desc} 成功获取凭证")
                    return data
                    
        except Exception:
            continue
    
    return None


def parse_credentials(data):
    """
    解析凭证数据，适配不同的数据格式
    """
    if not data or 'credentials' not in data:
        return []
    
    credentials = data['credentials']
    parsed_list = []
    
    for cred in credentials:
        # 尝试提取各种可能的字段
        cred_info = {
            'id': cred.get('id') or cred.get('credentialId') or 'Unknown',
            'description': cred.get('description', ''),
            'displayName': cred.get('displayName', ''),
            'typeName': cred.get('typeName', ''),
            'className': cred.get('_class', ''),
            'scope': cred.get('scope', ''),
        }
        
        # 如果没有 typeName，尝试从 className 提取
        if not cred_info['typeName'] and cred_info['className']:
            class_name = cred_info['className']
            if 'SSH' in class_name or 'ssh' in class_name:
                cred_info['typeName'] = 'SSH Username with private key'
            elif 'UsernamePassword' in class_name:
                cred_info['typeName'] = 'Username with password'
            elif 'Secret' in class_name:
                cred_info['typeName'] = 'Secret text'
            elif 'Certificate' in class_name:
                cred_info['typeName'] = 'Certificate'
            else:
                # 提取类名的最后一部分
                parts = class_name.split('.')
                cred_info['typeName'] = parts[-1] if parts else 'Unknown'
        
        parsed_list.append(cred_info)
    
    return parsed_list


def print_credentials_table(credentials):
    """
    打印凭证表格
    """
    if not credentials:
        print("\n⚠️  未找到任何凭证")
        print("\n可能的原因:")
        print("1. Jenkins 中没有配置任何凭证")
        print("2. 当前用户没有查看凭证的权限")
        print("3. 凭证存储在其他域(domain)中")
        print("\n建议:")
        print("- 在 Jenkins Web 界面手动查看: Manage Jenkins → Manage Credentials")
        print("- 检查用户权限: Credentials → View 权限")
        return
    
    print("\n" + "=" * 100)
    print(f"Jenkins 凭证列表 (找到 {len(credentials)} 个)")
    print("=" * 100)
    
    # 表格头
    header = f"{'序号':<6} {'Credential ID':<35} {'类型':<30} {'描述':<25}"
    print(f"\n{header}")
    print("-" * 100)
    
    # 打印每个凭证
    for i, cred in enumerate(credentials, 1):
        cred_id = cred['id']
        cred_type = cred['typeName']
        description = cred['description'] or cred['displayName'] or ''
        
        # 简化类型名称显示
        if 'SSH' in cred_type:
            type_short = '🔑 SSH Key'
        elif 'Username' in cred_type and 'password' in cred_type.lower():
            type_short = '👤 Username/Password'
        elif 'Secret' in cred_type:
            type_short = '🔐 Secret Text'
        elif 'Certificate' in cred_type:
            type_short = '📜 Certificate'
        else:
            type_short = cred_type[:28]
        
        # 截断过长内容
        cred_id_display = cred_id[:33] + '..' if len(cred_id) > 35 else cred_id
        desc_display = description[:23] + '..' if len(description) > 25 else description
        
        print(f"{i:<6} {cred_id_display:<35} {type_short:<30} {desc_display:<25}")
    
    print("-" * 100)
    
    # 使用提示
    print(f"\n💡 使用方法:")
    print("   创建节点时使用上面的 'Credential ID'，例如:")
    if credentials:
        example_id = credentials[0]['id']
        print(f'   python jenkins_node_cli.py create --name my-node --host 192.168.1.100 --credential-id "{example_id}"')
    print()


def main():
    """主函数"""
    print("=" * 100)
    print("Jenkins 凭证查询工具")
    print("=" * 100)
    
    try:
        # 加载配置
        config = load_config()
        jenkins_config = config.get('jenkins', {})
        
        url = jenkins_config.get('url')
        username = jenkins_config.get('username')
        password = jenkins_config.get('password')
        
        if not all([url, username, password]):
            print("\n❌ 配置文件中缺少 Jenkins 连接信息")
            print("请检查 jenkins_nodes_config.json 文件")
            return 1
        
        print(f"\nJenkins URL: {url}")
        print(f"用户: {username}")
        print("\n正在查询凭证...\n")
        
        # 获取凭证数据
        data = get_credentials_detailed(url, username, password)
        
        if not data:
            print("❌ 无法获取凭证信息")
            print("\n请尝试运行调试脚本查看详细信息:")
            print("   python debug_credentials.py")
            return 1
        
        # 解析凭证
        credentials = parse_credentials(data)
        
        # 打印结果
        print_credentials_table(credentials)
        
        return 0
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
