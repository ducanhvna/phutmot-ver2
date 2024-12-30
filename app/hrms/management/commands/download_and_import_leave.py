# your_app/management/commands/download_and_import_data.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from hrms.models import Leave
from collections import defaultdict
import xmlrpc.client
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Download Leave data from Odoo and import into Django'

    def handle(self, *args, **kwargs):
        # Get the first day of the current month
        first_day_of_month = datetime.now().replace(day=1)
        self.download(first_day_of_month)
        # Lấy ngày đầu tiên của tháng trước
        first_day_of_last_month = first_day_of_month - timedelta(days=1)
        first_day_of_last_month = datetime(first_day_of_last_month.year, first_day_of_last_month.month, 1)
        self.download(first_day_of_last_month)

    def download(self, first_day_of_month):
        # Define your Odoo connection parameters
        url = 'https://hrm.mandalahotel.com.vn'
        db = 'apechrm_product_v3'
        username = 'admin_ho'
        password = '43a824d3a724da2b59d059d909f13ba0c38fcb82'

        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        uid = common.authenticate(db, username, password, {})
        models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

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
            "employee_id",
            "employee_code",
            "employee_company_id",
            "active",
            "holiday_status_id",
            "minutes",
            "time",
            "state",
            "request_date_from",
            "request_date_to",
            "attendance_missing_from",
            "attendance_missing_to",
            "reasons",
            "for_reasons",
            "convert_overtime",
            "employee_company_id",
            "multiplier_work_time",
            "overtime_from",
            "overtime_to",
            "write_date",
            "multiplier_wage",
            "multiplied_wage_amount",
            "multiplied_work_time_amount",
            "absent_morning",
            "absent_afternoon",
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
                "hr.leave",
                "search",
                [
                    [
                        ("request_date_to", ">=", start_str),
                        ("request_date_from", "<=", end_str),
                        ("active", "=", True),
                        ("state", "=", "validate"),
                    ]
                ],
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
                "hr.leave",
                "read",
                [ids_chunk],
                {"fields": fields},
            )
            merged_data.extend(list_attendance_trans)

        # Group data by employee_code
        grouped_data = defaultdict(list)
        for record in merged_data:
            grouped_data[record["employee_code"]].append(record)
            print(f"{record['employee_code']} -- {len(grouped_data[record['employee_code']])} -- {record['holiday_status_id']}")

        # Save data to Django
        self.save_to_django(grouped_data, start_str, end_str)

    def save_to_django(self, grouped_data, start_date, end_date):
        for employee_code, records in grouped_data.items():
            leave, created = Leave.objects.get_or_create(
                employee_code=employee_code,
                start_date=datetime.strptime(start_date, "%Y-%m-%d"),
                end_date=datetime.strptime(end_date, "%Y-%m-%d"),
            )
            leave.leave_records = records
            leave.save()
