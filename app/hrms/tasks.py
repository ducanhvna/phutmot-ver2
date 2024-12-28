# hrms/tasks.py

import logging
from celery import shared_task

logger = logging.getLogger(__name__)
from hrms.utils.attendance_report import add_attempt_more_than_limit

@shared_task
def calculate_scheduling(attendance_id):
    # Import cục bộ để tránh import vòng lặp
    from .models import Attendance, Scheduling, Employee, Shifts, Leave

    try:
        # Lấy đối tượng Attendance
        attendance = Attendance.objects.get(id=attendance_id)

        employee = Employee.objects.get(time_keeping_code=attendance.code, start_date=attendance.start_date)

        scheduling = Scheduling.objects.get(employee_code=employee.employee_code, start_date=attendance.start_date)

        leave = Leave.objects.get(employee_code=employee.employee_code, start_date=attendance.start_date)

        # Log đối tượng Attendance
        logger.info(f"Create attendance: {attendance}")
        logger.info(f"Get employee: {employee}")
        logger.info(f"GET scheduling: {scheduling}")
        logger.info(f"GET leave: {leave}")
        for sched in scheduling.scheduling_records:
            add_attempt_more_than_limit(attendance, sched, 6, 6)

        # Tính toán và cập nhật Scheduling tương ứng
        # scheduling, created = Scheduling.objects.get_or_create(attendance=attendance)

        # Ví dụ: Cập nhật một số thuộc tính của Scheduling
        # scheduling.some_field = attendance.some_related_field
        # scheduling.save()

    except Attendance.DoesNotExist:
        logger.error(f"Attendance with id {attendance_id} does not exist.")
