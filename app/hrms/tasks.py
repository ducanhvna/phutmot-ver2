# hrms/tasks.py

from celery import shared_task
from .models import Attendance, Scheduling


@shared_task
def calculate_scheduling(attendance_id):
    # Lấy đối tượng Attendance
    attendance = Attendance.objects.get(id=attendance_id)
    
    # Tính toán và cập nhật Scheduling tương ứng
    # scheduling, created = Scheduling.objects.get_or_create(attendance=attendance)
    
    # Ví dụ: Cập nhật một số thuộc tính của Scheduling
    # scheduling.some_field = attendance.some_related_field
    # scheduling.save()
    print("Create attendance", attendance)
