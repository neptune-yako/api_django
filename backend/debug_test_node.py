"""
专门检查非master节点的配置
"""
from jenkins_integration.jenkins_client import get_jenkins_client
import json

client = get_jenkins_client()

# 获取所有节点
nodes = client.get_nodes()

for node in nodes:
    node_name = node.get('name', '')
    
    # 跳过Built-In Node,只看其他节点
    if node_name in ['Built-In Node', 'master', '(master)']:
        continue
    
    print(f"=" * 70)
    print(f"节点名称: {node_name}")
    print(f"=" * 70)
    
    try:
        node_info = client.get_node_info(node_name)
        
        print("\n完整节点信息:")
        print(json.dumps(node_info, indent=2, ensure_ascii=False, default=str))
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n")
