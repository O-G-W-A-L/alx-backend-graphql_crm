#!/bin/bash
# Deletes customers with NO orders in the last 365 days.
# Logs count + timestamp to /tmp/customer_cleanup_log.txt

LOG_FILE="/tmp/customer_cleanup_log.txt"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Use Django's shell to run a one-liner that:
#   - filters customers whose latest order < 1 year ago (or no orders)
#   - deletes them in bulk
COUNT=$(python manage.py shell -c "
from django.utils import timezone
from datetime import timedelta
from customers.models import Customer
from django.db.models import Max, Q

cutoff = timezone.now() - timedelta(days=365)
stale = Customer.objects.annotate(
            last_order=Max('orders__created_at')
        ).filter(
            Q(last_order__lt=cutoff) | Q(orders__isnull=True)
        )
print(stale.count())   # prints to stdout → captured in COUNT
stale.delete()
")

echo "[$TIMESTAMP] Deleted ${COUNT:-0} inactive customers" >> "$LOG_FILE"
