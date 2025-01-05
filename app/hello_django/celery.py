from celery import Celery
from celery.schedules import crontab
import os


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hello_django.settings')
app = Celery('hello_django')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Cấu hình Beat Schedule
app.conf.beat_schedule = {
    'my-scheduled-task': {
        'task': 'hrms.tasks.check_apec_hrms_update',
        'schedule': 30.0,  # 30 giây một lần
    },
}
