
import logging
import sys
import jenkins

# Setup logging
logging.basicConfig(level=logging.ERROR) # Only show errors to keep output clean

def test_jenkins_auth_nodes(username, token):
    url = "http://mg.morry.online"
    print(f"Testing User: {username} ...")
    try:
        client = jenkins.Jenkins(url, username=username, password=token)
        version = client.get_version()
        print(f"  [OK] Auth success (Version: {version})")
        
        try:
            nodes = client.get_nodes()
            print(f"  [OK] Get nodes success (Count: {len(nodes)})")
            return True
        except Exception as e:
            print(f"  [FAIL] Get nodes failed: {e}")
            return False
            
    except Exception as e:
        print(f"  [FAIL] Auth failed: {e}")
        return False

if __name__ == "__main__":
    current_token = "112f35231e8ffe20994a406815179d8a68"
    
    print("--- Testing Credentials ---")
    test_jenkins_auth_nodes("akko", current_token)
    test_jenkins_auth_nodes("admin", current_token)
