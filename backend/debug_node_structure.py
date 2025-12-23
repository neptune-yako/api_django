"""
直接测试Jenkins API,查看节点信息的完整结构
"""
from jenkins_integration.jenkins_client import get_jenkins_client

client = get_jenkins_client()

# 获取所有节点
nodes = client.get_nodes()
print(f"找到 {len(nodes)} 个节点\n")

for node in nodes[:2]:  # 只查看前2个节点
    node_name = node.get('name', '')
    print(f"=" * 60)
    print(f"节点名称: {node_name}")
    print(f"=" * 60)
    
    try:
        # 获取详细信息
        node_info = client.get_node_info(node_name)
        
        print("\n【基本信息】")
        print(f"  displayName: {node_info.get('displayName')}")
        print(f"  description: {node_info.get('description')}")
        print(f"  offline: {node_info.get('offline')}")
        
        print("\n【monitorData 键列表】")
        monitor_data = node_info.get('monitorData', {})
        for key in monitor_data.keys():
            print(f"  - {key}")
        
        print("\n【检查特定监控器】")
        # 检查架构监控器
        if 'hudson.node_monitors.ArchitectureMonitor' in monitor_data:
            arch = monitor_data['hudson.node_monitors.ArchitectureMonitor']
            print(f"  ArchitectureMonitor: {arch}")
        
        # 检查响应时间监控器
        if 'hudson.node_monitors.ResponseTimeMonitor' in monitor_data:
            resp = monitor_data['hudson.node_monitors.ResponseTimeMonitor']
            print(f"  ResponseTimeMonitor: {resp}")
        
        # 检查磁盘空间监控器
        if 'hudson.node_monitors.DiskSpaceMonitor' in monitor_data:
            disk = monitor_data['hudson.node_monitors.DiskSpaceMonitor']
            print(f"  DiskSpaceMonitor keys: {disk.keys() if isinstance(disk, dict) else type(disk)}")
        
        print("\n【完整monitorData】")
        import json
        print(json.dumps(monitor_data, indent=2, ensure_ascii=False, default=str))
        
    except Exception as e:
        print(f"  ERROR: {e}")
    
    print("\n")
