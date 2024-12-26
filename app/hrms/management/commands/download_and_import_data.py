# your_app/management/commands/download_and_import_data.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from hrms.models import Scheduling
from collections import defaultdict
import xmlrpc.client
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Download data from Odoo and import into Django'

    def handle(self, *args, **kwargs):
        # Define your Odoo connection parameters
        url = 'https://hrm.mandalahotel.com.vn'
        db = 'apechrm_product_v3'
        username = 'admin_ho'
        password = '43a824d3a724da2b59d059d909f13ba0c38fcb82'

        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        uid = common.authenticate(db, username, password, {})
        models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

        # Get the first day of the current month
        first_day_of_month = datetime.now().replace(day=1)

        # Calculate the last day of the current month
        if first_day_of_month.month == 12:
            next_month = first_day_of_month.replace(year=first_day_of_month.year + 1, month=1, day=1)
        else:
            next_month = first_day_of_month.replace(month=first_day_of_month.month + 1, day=1)

        last_day_of_month = next_month - timedelta(days=1)

        # Format the dates
        start_str = first_day_of_month.strftime('%Y-%m-%d')
        end_str = last_day_of_month.strftime('%Y-%m-%d')

        print(f"Start date: {start_str}")
        print(f"End date: {end_str}")

        fields = [
            "id",
            "employee_name",
            "date",
            "shift_name",
            "employee_code",
            "company",
            "additional_company",
            "shift_start",
            "shift_end",
            "rest_start",
            "rest_end",
            "rest_shift",
            "probation_completion_wage",
            "total_shift_work_time",
            "total_work_time",
            "time_keeping_code",
            "kid_time",
            "department",
            "attendance_attempt_1",
            "attendance_attempt_2",
            "minutes_working_reduced",
            "attendance_attempt_3",
            "attendance_attempt_4",
            "attendance_attempt_5",
            "attendance_attempt_6",
            "attendance_attempt_7",
            "attendance_attempt_8",
            "attendance_attempt_9",
            "attendance_attempt_10",
            "attendance_attempt_11",
            "attendance_attempt_12",
            "attendance_attempt_13",
            "attendance_attempt_14",
            "attendance_inout_1",
            "attendance_inout_2",
            "attendance_inout_3",
            "attendance_inout_4",
            "attendance_inout_5",
            "attendance_inout_6",
            "attendance_inout_7",
            "attendance_inout_8",
            "attendance_inout_9",
            "amount_al_reserve",
            "amount_cl_reserve",
            "attendance_inout_10",
            "attendance_inout_11",
            "attendance_inout_12",
            "attendance_inout_13",
            "attendance_inout_14",
            "attendance_inout_15",
            "actual_total_work_time",
            "standard_working_day",
            "attendance_attempt_15",
            "last_attendance_attempt",
            "attendance_inout_last",
            "night_hours_normal",
            "night_hours_holiday",
            "probation_wage_rate",
            "split_shift",
            "missing_checkin_break",
            "leave_early",
            "attendance_late",
            "night_shift",
            "minute_worked_day_holiday",
            "total_attendance",
            "ot_holiday",
            "ot_normal",
            "write_date",
            "locked",
        ]
        LIMIT_SIZE = 300
        index = 0
        len_data = 0
        merged_array = []
        while (len_data == LIMIT_SIZE) or (index == 0):
            ids = models.execute_kw(
                db,
                uid,
                password,
                "hr.apec.attendance.report",
                "search",
                [["&", ("date", ">=", start_str), ("date", "<=", end_str)]],
                {"offset": index * LIMIT_SIZE, "limit": LIMIT_SIZE},
            )
            len_data = len(ids)
            print(ids)
            merged_array = list(set(merged_array) | set(ids))
            index = index + 1

        # Split ids into chunks of 200
        ids_chunks = [
            merged_array[i:i + 200] for i in range(0, len(merged_array), 200)
        ]
        print(ids_chunks)
        merged_data = []

        for ids_chunk in ids_chunks:
            # Fetch data from Odoo
            list_attendance_trans = models.execute_kw(
                db,
                uid,
                password,
                "hr.apec.attendance.report",
                "read",
                [ids_chunk],
                {"fields": fields},
            )
            merged_data.extend(list_attendance_trans)

        # Group data by employee_code
        grouped_data = defaultdict(list)
        for record in merged_data:
            grouped_data[record["employee_code"]].append(record)
            print(f"{record['employee_code']} -- {len(grouped_data[record['employee_code']])}")

        # Save data to Django
        self.save_to_django(grouped_data, start_str, end_str)

    def save_to_django(self, grouped_data, start_date, end_date):
        for employee_code, records in grouped_data.items():
            scheduling, created = Scheduling.objects.get_or_create(
                employee_code=employee_code,
                start_date=datetime.strptime(start_date, "%Y-%m-%d"),
                end_date=datetime.strptime(end_date, "%Y-%m-%d"),
            )
            scheduling.scheduling_records = records
            scheduling.save()
