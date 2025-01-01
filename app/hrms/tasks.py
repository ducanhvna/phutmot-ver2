# hrms/tasks.py

import logging
from celery import shared_task
from datetime import timedelta

logger = logging.getLogger(__name__)


@shared_task
def calculate_scheduling(attendance_id):
    # Import cục bộ để tránh import vòng lặp
    from .models import Attendance, Scheduling, Employee, Shifts, Leave, Explaination
    from .utils.attendance_report import add_attempt_more_than_limit, mergedTimeToScheduling, collect_data_to_schedulings, calculate_worktime_with_inout_standard
    from home.models import UserProfile

    try:
        # Lấy đối tượng Attendance
        attendance = Attendance.objects.get(id=attendance_id)
        start_date = attendance.start_date + timedelta(days=1)
        employee = Employee.objects.get(time_keeping_code=attendance.code, start_date=start_date)
        profile = UserProfile.objects.get(employee_code=employee.employee_code)
        shifts = Shifts.objects.filter(company_code='IDJ')
        scheduling = Scheduling.objects.get(employee_code=employee.employee_code, start_date=start_date)

        leave = Leave.objects.get(employee_code=employee.employee_code, start_date=start_date)
        explanation = Explaination.objects.get(employee_code=employee.employee_code, start_date=start_date)
        # Log đối tượng Attendance
        logger.info(f"Create attendance: {attendance}")
        logger.info(f"Get employee: {employee}")
        logger.info(f"GET scheduling: {scheduling}")
        logger.info(f"GET leave: {leave}")
        mergedTimeToScheduling(scheduling.scheduling_records, shifts, employee, leave, explanation, profile)
        for sched in scheduling.scheduling_records:
            add_attempt_more_than_limit(attendance.attendance_records, sched, 6, 6)
            # process_missing_attendance(sched)
            # find_attendance_hue4_time_mode(sched)
            calculate_worktime_with_inout_standard(sched)
        # Tính toán và cập nhật Scheduling tương ứng
        # scheduling, created = Scheduling.objects.get_or_create(attendance=attendance)

        # Ví dụ: Cập nhật một số thuộc tính của Scheduling
        # scheduling.some_field = attendance.some_related_field
        # scheduling.save()

    except Attendance.DoesNotExist:
        logger.error(f"Attendance with id {attendance_id} does not exist.")
