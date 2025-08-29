# CRM Celery Setup Guide

This guide provides step-by-step instructions to set up Celery with Redis for automated CRM report generation.

## Prerequisites

- Python 3.8+
- Django project setup
- Redis server

## Setup Instructions

### 1. Install Redis and Dependencies

#### Install Redis (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

#### Verify Redis is running:
```bash
redis-cli ping
# Should return: PONG
```

#### Install Python dependencies:
```bash
pip install celery django-celery-beat redis
```

### 2. Run Database Migrations

Apply Django migrations including Celery Beat tables:
```bash
python manage.py migrate
```

### 3. Start Celery Services

#### Start Celery Worker (in first terminal):
```bash
celery -A crm worker -l info
```

#### Start Celery Beat Scheduler (in second terminal):
```bash
celery -A crm beat -l info
```

#### Optional: Start both in background with supervisor or systemd

### 4. Verify Setup

#### Check Celery Worker Status:
```bash
celery -A crm inspect active
```

#### Check Scheduled Tasks:
```bash
celery -A crm inspect scheduled
```

#### Monitor Logs:
```bash
tail -f /tmp/crm_report_log.txt
```

## Celery Task Configuration

### Scheduled Tasks

1. **CRM Report Generation**
   - **Schedule**: Every Monday at 6:00 AM
   - **Task**: `crm.tasks.generate_crm_report`
   - **Output**: `/tmp/crm_report_log.txt`
   - **Content**: Total customers, orders, and revenue summary

### Manual Task Execution

To manually trigger the report generation:
```bash
python manage.py shell
```

```python
from crm.tasks import generate_crm_report
result = generate_crm_report.delay()
print(result.get())
```

## Log File Locations

- **CRM Reports**: `/tmp/crm_report_log.txt`
- **Heartbeat Logs**: `/tmp/crm_heartbeat_log.txt`
- **Stock Update Logs**: `/tmp/low_stock_updates_log.txt`

## Troubleshooting

### Redis Connection Issues
```bash
# Check Redis status
sudo systemctl status redis-server

# Restart Redis if needed
sudo systemctl restart redis-server
```

### Celery Worker Issues
```bash
# Clear all tasks
celery -A crm purge

# Restart worker with debug info
celery -A crm worker -l debug
```

### Task Not Running
- Verify Celery Beat is running
- Check timezone settings in Django settings
- Ensure Redis is accessible
- Check task registration with: `celery -A crm inspect registered`

## Production Considerations

1. **Use process managers** (supervisor, systemd) for Celery processes
2. **Configure proper logging** instead of using /tmp files
3. **Set up monitoring** with tools like Flower or Celery Monitor
4. **Use environment variables** for Redis URLs and sensitive settings
5. **Scale workers** based on task load

## Development Testing

For development, you can test the setup by:

1. Starting Redis: `sudo systemctl start redis-server`
2. Running migrations: `python manage.py migrate`
3. Starting worker: `celery -A crm worker -l info`
4. Starting beat: `celery -A crm beat -l info`
5. Manually triggering task or waiting for scheduled execution
6. Checking log files for output

## GraphQL Integration

The CRM report task integrates with the GraphQL endpoint to fetch:
- Customer count via `customers` query
- Order count and revenue via `orders` query with `totalAmount` field

If the GraphQL endpoint is unavailable, the task falls back to direct database queries.
