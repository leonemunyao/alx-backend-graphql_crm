import os
import sys
import django
from datetime import datetime
import requests
import json


sys.path.append('/home/leone/Coding/ProDevAlx/alx-backend-graphql_crm')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql_crm.settings')
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


def update_low_stock():
    """
    Executes the UpdateLowStockProducts mutation via GraphQL endpoint
    and logs updated product names and new stock levels.
    """
    # Get current timestamp
    timestamp = datetime.now().strftime('%d/%m/%Y-%H:%M:%S')
    
    try:
        # GraphQL mutation to update low stock products
        mutation = {
            "query": """
                mutation {
                    updateLowStockProducts {
                        updatedProducts {
                            id
                            name
                            stock
                        }
                        message
                    }
                }
            """
        }
        
        response = requests.post(
            'http://localhost:8000/graphql',
            json=mutation,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if 'data' in data and 'updateLowStockProducts' in data['data']:
                result = data['data']['updateLowStockProducts']
                updated_products = result.get('updatedProducts', [])
                message = result.get('message', 'No message')
                
                # Log the results
                with open('/tmp/low_stock_updates_log.txt', 'a') as log_file:
                    log_file.write(f"[{timestamp}] {message}\n")
                    
                    for product in updated_products:
                        product_name = product['name']
                        new_stock = product['stock']
                        log_file.write(f"[{timestamp}] Updated product: {product_name}, New stock: {new_stock}\n")
                
            else:
                # Handle GraphQL errors
                error_message = data.get('errors', [{'message': 'Unknown GraphQL error'}])[0]['message']
                with open('/tmp/low_stock_updates_log.txt', 'a') as log_file:
                    log_file.write(f"[{timestamp}] GraphQL error: {error_message}\n")
        
        else:
            # Handle HTTP errors
            with open('/tmp/low_stock_updates_log.txt', 'a') as log_file:
                log_file.write(f"[{timestamp}] HTTP error: Status {response.status_code}\n")
    
    except requests.exceptions.RequestException as e:
        # Handle connection errors
        with open('/tmp/low_stock_updates_log.txt', 'a') as log_file:
            log_file.write(f"[{timestamp}] Connection error: {str(e)}\n")
    except Exception as e:
        # Handle other errors
        with open('/tmp/low_stock_updates_log.txt', 'a') as log_file:
            log_file.write(f"[{timestamp}] Error: {str(e)}\n")