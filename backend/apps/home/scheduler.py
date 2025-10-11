from django_celery_beat.models import PeriodicTask, IntervalSchedule
from django.utils.timezone import now
import json

def setup_periodic_tasks():
    # Tạo lịch chạy mỗi 1 phút
    schedule, created = IntervalSchedule.objects.get_or_create(
        every=1,
        period=IntervalSchedule.MINUTES,
    )

    # Tạo task nếu chưa tồn tại
    PeriodicTask.objects.update_or_create(
        name='Collect data every minute',
        defaults={
            'interval': schedule,
            'task': 'apps.home.tasks.collect_data',
            'start_time': now(),
            'enabled': True,
            'args': json.dumps([]),
        }
    )
