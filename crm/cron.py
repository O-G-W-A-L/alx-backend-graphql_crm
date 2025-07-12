"""
crm/cron.py
Heartbeat job for django-crontab.
Runs every 5 minutes.
"""

import datetime
import os
import sys
from pathlib import Path

# Ensure Django settings are available when run via cron
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crm.settings")

import django
django.setup()

from django.conf import settings
import requests  # optional GraphQL probe

LOG_FILE = "/tmp/crm_heartbeat_log.txt"


def log_crm_heartbeat():
    """
    Append a heartbeat line to the log file.
    Optionally hit the GraphQL 'hello' field to confirm endpoint health.
    """
    now = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    line = f"{now} CRM is alive"

    # Optional GraphQL probe
    try:
        response = requests.post(
            "http://localhost:8000/graphql",
            json={"query": "{ hello }"},
            timeout=3
        )
        if response.status_code == 200:
            gql_status = "GraphQL OK"
        else:
            gql_status = f"GraphQL DOWN ({response.status_code})"
    except Exception as exc:
        gql_status = f"GraphQL ERROR ({exc})"

    line += f" - {gql_status}\n"

    with open(LOG_FILE, "a") as f:
        f.write(line)


# Allow standalone execution for quick test
if __name__ == "__main__":
    log_crm_heartbeat()