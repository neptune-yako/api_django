
import os
import sys
import django
import logging

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from jenkins_integration.services.node_sync import sync_jenkins_nodes

# Configure logging
logging.basicConfig(level=logging.INFO)

def run_sync_test():
    print("Running Jenkins Node Sync Test...")
    try:
        success, msg, data = sync_jenkins_nodes(project_id=1, user=None)
        if success:
            print("Sync Successful!")
            print(msg)
            print(f"Synced Data: {data['synced_count']} nodes.")
            print(f"Deleted Data: {data.get('deleted_count', 0)} nodes.")
        else:
            print(f"Sync Failed: {msg}")
    except Exception as e:
        print(f"Error during sync: {e}")

if __name__ == "__main__":
    run_sync_test()
