#!/bin/bash


cd /home/leone/Coding/ProDevAlx/alx-backend-graphql_crm

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

DELETED_COUNT=$(python manage.py shell -c "
from django.utils import timezone
from datetime import timedelta
from crm.models import Customer

# Calculate date one year ago
one_year_ago = timezone.now() - timedelta(days=365)

# Find customers with no orders since a year ago
inactive_customers = Customer.objects.filter(
    orders__isnull=True
).distinct() | Customer.objects.exclude(
    orders__created_at__gte=one_year_ago
).distinct()

# Count and delete
count = inactive_customers.count()
inactive_customers.delete()
print(count)
" 2>/dev/null)

echo "[$TIMESTAMP] Deleted $DELETED_COUNT inactive customers" >> /tmp/customer_cleanup_log.txt