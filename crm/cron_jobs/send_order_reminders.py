#!/usr/bin/env python3
# filepath: /home/leone/Coding/ProDevAlx/alx-backend-graphql_crm/crm/cron_jobs/send_order_reminders.py

import os
import sys
import django
from datetime import datetime, timedelta
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
import json


sys.path.append('/home/leone/Coding/ProDevAlx/alx-backend-graphql_crm')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'graphql_crm.settings')
django.setup()

def main():

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    seven_days_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    transport = RequestsHTTPTransport(url="http://localhost:8000/graphql")
    client = Client(transport=transport, fetch_schema_from_transport=True)
    
 
    query = gql("""
        query GetRecentOrders($dateFilter: String!) {
            orders(orderDate_Gte: $dateFilter) {
                id
                orderDate
                customer {
                    email
                }
            }
        }
    """)
    
    try:
        variables = {"dateFilter": seven_days_ago}
        result = client.execute(query, variable_values=variables)
        
        orders = result.get('orders', [])
        
        with open('/tmp/order_reminders_log.txt', 'a') as log_file:
            for order in orders:
                order_id = order['id']
                customer_email = order['customer']['email']
                log_entry = f"[{timestamp}] Order ID: {order_id}, Customer Email: {customer_email}\n"
                log_file.write(log_entry)
        
        print("Order reminders processed!")
        
    except Exception as e:
        with open('/tmp/order_reminders_log.txt', 'a') as log_file:
            log_file.write(f"[{timestamp}] Error processing reminders: {str(e)}\n")
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()