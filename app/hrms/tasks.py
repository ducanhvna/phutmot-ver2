# hrms/tasks.py

import logging
import json
from celery import shared_task
from datetime import timedelta, datetime
from hrms.models import Timesheet

logger = logging.getLogger(__name__)


def serialize_scheduling(obj):
    """Helper function to convert datetime objects to string."""
    result = []
    for scheduling in obj.scheduling_records:
        timesheet = {
            "date": scheduling.get("date", None),
            'listitemTrans': scheduling.get('listitemTrans', []),
            'attempt_with_inout_array': scheduling.get('attempt_with_inout_array', []),
            'attendanceAttemptArray': scheduling.get('attendanceAttemptArray', []),
            "shift_start_datetime": scheduling.get("shift_start_datetime", None),
            "shift_end_datetime": scheduling.get("shift_end_datetime", None),
            "rest_start_datetime": scheduling.get("rest_start_datetime", None),
            "rest_end_datetime": scheduling.get("rest_end_datetime", None),
            'shift_name': scheduling.get('shift_name', '-'),
            "out_in_after_explanation_private": scheduling.get(
                "list_couple_out_in_after_explanation_private", []
            ),
            "couple_after_explanation_private": scheduling.get(
                "list_couple_after_explanation_private", []
            ),
        }
        result.append(timesheet)
    return result


def save_to_django_timesheet(schedule, start_date, end_date, serialize_datetime):
    # Convert scheduling_records datetime objects to strings
    serialized_records = json.loads(json.dumps(serialize_scheduling(schedule), default=serialize_datetime))

    timesheet, created = Timesheet.objects.get_or_create(
        employee_code=schedule.employee_code,
        start_date=start_date,
        end_date=end_date,
        defaults={"timesheet_records": []},
    )
    timesheet.timesheet_records = serialized_records
    timesheet.save()


@shared_task
def calculate_scheduling(attendance_id):
    # Import cục bộ để tránh import vòng lặp
    from .models import Attendance, Scheduling, Employee, Shifts, Leave, Explaination
    from .utils.attendance_report import add_attempt_more_than_limit, mergedTimeToScheduling, serialize_datetime, calculate_worktime_with_inout_standard
    from home.models import UserProfile

    try:
        # Lấy đối tượng Attendance
        attendance = Attendance.objects.get(id=attendance_id)
        start_date = attendance.start_date + timedelta(days=1)
        first_day_of_month = start_date.replace(day=1)
        if first_day_of_month.month == 12:
            next_month = first_day_of_month.replace(year=first_day_of_month.year + 1, month=1, day=1)
        else:
            next_month = first_day_of_month.replace(month=first_day_of_month.month + 1, day=1)

        last_day_of_month = next_month - timedelta(days=1)
        employee = Employee.objects.get(time_keeping_code=attendance.code, start_date=start_date)
        profile = UserProfile.objects.get(employee_code=employee.employee_code)
        shifts = Shifts.objects.filter(company_code='IDJ')
        scheduling = Scheduling.objects.get(employee_code=employee.employee_code, start_date=start_date)

        leave, _ = Leave.objects.get_or_create(
            employee_code=employee.employee_code,
            start_date=first_day_of_month,
            end_date=last_day_of_month,
            defaults={"leave_records": []},
        )
        explanation, _ = Explaination.objects.get_or_create(
            employee_code=employee.employee_code,
            start_date=first_day_of_month,
            end_date=last_day_of_month,
            defaults={"explaination_records": []},
        )
        # Log đối tượng Attendance
        logger.info(f"Create attendance: {attendance}")
        logger.info(f"Get employee: {employee}")
        logger.info(f"GET scheduling: {scheduling}")
        logger.info(f"GET leave: {leave}")
        mergedTimeToScheduling(scheduling.scheduling_records, shifts, employee, leave.leave_records, explanation, profile)
        for sched in scheduling.scheduling_records:
            add_attempt_more_than_limit(attendance.attendance_records, sched, 6, 6)
            # process_missing_attendance(sched)
            # find_attendance_hue4_time_mode(sched)
            calculate_worktime_with_inout_standard(sched)
        save_to_django_timesheet(scheduling, first_day_of_month, last_day_of_month, serialize_datetime)
        # Tính toán và cập nhật Scheduling tương ứng
        # scheduling, created = Scheduling.objects.get_or_create(attendance=attendance)

        # Ví dụ: Cập nhật một số thuộc tính của Scheduling
        # scheduling.some_field = attendance.some_related_field
        # scheduling.save()

    except Attendance.DoesNotExist:
        logger.error(f"Attendance with id {attendance_id} does not exist.")


@shared_task
def check_apec_hrms_update():
    print("Tác vụ chạy định kỳ mỗi 30 giây check_apec_hrms_update")
    # Thực hiện công việc của bạn tại đây
