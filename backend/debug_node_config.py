"""
检查Jenkins节点配置以查找IP地址信息
"""
from jenkins_integration.jenkins_client import get_jenkins_client
import json

client = get_jenkins_client()

# 获取所有节点
nodes = client.get_nodes()
print(f"找到 {len(nodes)} 个节点\n")

for node in nodes[:3]:  # 查看前3个节点
    node_name = node.get('name', '')
    print(f"=" * 60)
    print(f"节点名称: {node_name}")
    print(f"=" * 60)
    
    try:
        # 获取详细信息
        node_info = client.get_node_info(node_name)
        
        print("\n【节点完整信息的关键字段】")
        important_keys = ['displayName', 'description', 'launcher', 'nodeDescription', 
                         'remoteFS', 'labelString', 'mode']
        for key in important_keys:
            if key in node_info:
                value = node_info[key]
                if isinstance(value, dict):
                    print(f"  {key}: (dict)")
                    for k, v in value.items():
                        print(f"    - {k}: {v}")
                else:
                    print(f"  {key}: {value}")
        
        # 检查launcher配置(可能包含主机信息)
        if 'launcher' in node_info and node_info['launcher']:
            print("\n【Launcher详细信息】")
            launcher = node_info['launcher']
            print(f"  Type: {launcher.get('_class', 'Unknown')}")
            if 'host' in launcher:
                print(f"  Host: {launcher.get('host')}")
            if 'port' in launcher:
                print(f"  Port: {launcher.get('port')}")
            # 打印所有launcher字段
            print("  All launcher keys:")
            for k, v in launcher.items():
                if k != '_class':
                    print(f"    {k}: {v}")
        
        # 输出所有一级键
        print("\n【所有一级键】")
        print(f"  {', '.join(node_info.keys())}")
        
    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n")
