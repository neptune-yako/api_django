
import logging
import sys
import os

# Add the current directory to path so we can import jenkins_integration
sys.path.append(os.getcwd())

# Mock logging config
logging.basicConfig(level=logging.INFO)

try:
    from jenkins_integration.jenkins_client import get_all_nodes, get_jenkins_client
    
    def test_jenkins():
        print("Testing Jenkins Connection...")
        try:
            client = get_jenkins_client()
            version = client.get_version()
            print(f"Jenkins Connected! Version: {version}")
            
            success, msg, nodes = get_all_nodes()
            if success:
                print(f"Successfully fetched {len(nodes)} nodes.")
                for node in nodes:
                    print(f" - {node['name']} (Online: {not node['offline']})")
            else:
                print(f"Failed to fetch nodes: {msg}")
                
        except Exception as e:
            print(f"Connection Failed: {e}")

    if __name__ == "__main__":
        test_jenkins()

except ImportError as e:
    print(f"Import Error: {e}")
    print("Ensure you are running this from 'e:\\github\\api_django\\backend'")
