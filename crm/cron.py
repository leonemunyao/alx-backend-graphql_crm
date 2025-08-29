import os
import sys
import django
from datetime import datetime
import requests
import json


sys.path.append('/home/leone/Coding/ProDevAlx/alx-backend-graphql_crm')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'graphql_crm.settings')
django.setup()

def log_crm_heartbeat():
    """
    Logs a heartbeat message to confirm CRM application health.
    Optionally queries the GraphQL hello field to verify endpoint responsiveness.
    """

    timestamp = datetime.now().strftime('%d/%m/%Y-%H:%M:%S')
    

    heartbeat_message = f"{timestamp} CRM is alive"
    
    try:
        query = {
            "query": "{ hello }"
        }
        
        response = requests.post(
            'http://localhost:8000/graphql',
            json=query,
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and 'hello' in data['data']:
                heartbeat_message += " - GraphQL endpoint responsive"
            else:
                heartbeat_message += " - GraphQL endpoint error"
        else:
            heartbeat_message += f" - GraphQL endpoint returned status {response.status_code}"
            
    except requests.exceptions.RequestException as e:
        heartbeat_message += f" - GraphQL endpoint unreachable: {str(e)}"
    except Exception as e:
        heartbeat_message += f" - Error testing GraphQL: {str(e)}"
    
    try:
        with open('/tmp/crm_heartbeat_log.txt', 'a') as log_file:
            log_file.write(heartbeat_message + '\n')
    except Exception as e:
        print(f"Failed to write heartbeat log: {str(e)}")
        print(heartbeat_message)