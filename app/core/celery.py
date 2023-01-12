# --------------------------------------------------------------
# Python imports
# --------------------------------------------------------------
import os
from datetime import timedelta

# --------------------------------------------------------------
# 3rd party imports
# --------------------------------------------------------------
from celery import Celery

 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
app = Celery('core')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.timezone = 'Europe/London'

app.conf.beat_schedule = {
    "bulk_send": {
        "task": "app.patient.tasks.bulk_send",
        "schedule": timedelta(days=1),
    },
}
 

app.autodiscover_tasks()
