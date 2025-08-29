import os
import sys
import django
from datetime import datetime
import requests
import json
from celery import shared_task

sys.path.append('/home/leone/Coding/ProDevAlx/alx-backend-graphql_crm')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql_crm.settings')
django.setup()

from .models import Customer, Order, Product


@shared_task
def generate_crm_report():
    """
    Generates a weekly CRM report by querying GraphQL endpoint for:
    - Total number of customers
    - Total number of orders
    - Total revenue (sum of total_amount from orders)
    
    Logs the report to /tmp/crm_report_log.txt with timestamp.
    """

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        query = {
            "query": """
                query {
                    customers {
                        id
                    }
                    orders {
                        id
                        totalPrice
                    }
                }
            """
        }
        
        response = requests.post(
            'http://localhost:8000/graphql',
            json=query,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if 'data' in data:
                customers = data['data'].get('customers', [])
                orders = data['data'].get('orders', [])
                
                total_customers = len(customers)
                total_orders = len(orders)
                total_revenue = sum(float(order.get('totalPrice', 0)) for order in orders)
                
                report_message = f"{timestamp} - Report: {total_customers} customers, {total_orders} orders, ${total_revenue:.2f} revenue"
                
                with open('/tmp/crm_report_log.txt', 'a') as log_file:
                    log_file.write(report_message + '\n')
                
                print(f"CRM Report generated successfully: {report_message}")
                return report_message
                
            else:
                error_message = data.get('errors', [{'message': 'Unknown GraphQL error'}])[0]['message']
                error_log = f"{timestamp} - GraphQL error: {error_message}"
                
                with open('/tmp/crm_report_log.txt', 'a') as log_file:
                    log_file.write(error_log + '\n')
                
                return error_log
        
        else:
            error_log = f"{timestamp} - HTTP error: Status {response.status_code}"
            
            with open('/tmp/crm_report_log.txt', 'a') as log_file:
                log_file.write(error_log + '\n')
            
            return error_log
    
    except requests.exceptions.RequestException as e:
        try:
            total_customers = Customer.objects.count()
            total_orders = Order.objects.count()
            total_revenue = sum(order.total_price for order in Order.objects.all())
            
            report_message = f"{timestamp} - Report (DB fallback): {total_customers} customers, {total_orders} orders, ${total_revenue:.2f} revenue"
            
            with open('/tmp/crm_report_log.txt', 'a') as log_file:
                log_file.write(report_message + '\n')
            
            return report_message
            
        except Exception as db_error:
            error_log = f"{timestamp} - Connection error and DB fallback failed: {str(e)}, {str(db_error)}"
            
            with open('/tmp/crm_report_log.txt', 'a') as log_file:
                log_file.write(error_log + '\n')
            
            return error_log
    
    except Exception as e:
        error_log = f"{timestamp} - Error generating report: {str(e)}"
        
        with open('/tmp/crm_report_log.txt', 'a') as log_file:
            log_file.write(error_log + '\n')
        
        return error_log