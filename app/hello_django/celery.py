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
        'task': 'dashboard.tasks.check_apec_hrms_update',
        'schedule': 180.0,  # 60 giây một lần
    },
    'hrm-scheduled-task': {  # Task mới
        'task': 'dashboard.tasks.update_apec_hrm',
        'schedule': 960.0,  # 16 phút một lần
    },
    'project-scheduled-task': {
        'task': 'dashboard.tasks.update_bhl_project',
        'schedule': 885.0,  # 885s một lần
    }
}
