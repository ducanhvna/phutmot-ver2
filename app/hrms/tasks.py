# hrms/tasks.py

import logging
from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def calculate_scheduling(attendance_id):
    # Import cục bộ để tránh import vòng lặp
    from .models import Attendance, Scheduling

    try:
        # Lấy đối tượng Attendance
        attendance = Attendance.objects.get(id=attendance_id)

        # Log đối tượng Attendance
        logger.info(f"Create attendance: {attendance}")

        # Tính toán và cập nhật Scheduling tương ứng
        # scheduling, created = Scheduling.objects.get_or_create(attendance=attendance)

        # Ví dụ: Cập nhật một số thuộc tính của Scheduling
        # scheduling.some_field = attendance.some_related_field
        # scheduling.save()

    except Attendance.DoesNotExist:
        logger.error(f"Attendance with id {attendance_id} does not exist.")