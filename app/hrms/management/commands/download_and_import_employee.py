# your_app/management/commands/download_and_import_data.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from hrms.models import Employee
from collections import defaultdict
import xmlrpc.client
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Download Employee data from Odoo and import into Django'

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
        last_day_of_month = next_month - timedelta(days=1)

        # Calculate the last day of the current month
        if first_day_of_month.month == 12:
            next_month_first_day = first_day_of_month.replace(year=first_day_of_month.year + 1, month=1, day=1)
        else:
            next_month_first_day = first_day_of_month.replace(month=first_day_of_month.month + 1, day=1)

        # Format the dates
        start_str = first_day_of_month.strftime('%Y-%m-%d')
        end_str = last_day_of_month.strftime('%Y-%m-%d')
        nextmonthFistdayStr = next_month_first_day.strftime('%Y-%m-%d')

        print(f"Start date: {start_str}")
        print(f"nextmonthFistdayStr: {nextmonthFistdayStr}")

        fields = [
            'id',
            'name',
            'user_id',
            'employee_ho',
            'part_time_company_id',
            'part_time_department_id',
            'company_id',
            'code',
            'department_id',
            'time_keeping_code',
            'job_title',
            'probationary_contract_termination_date',
            'severance_day',
            'workingday',
            'probationary_salary_rate',
            'resource_calendar_id',
            'date_sign',
            'level',
            'working_status',
            'write_date',
            'active'
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
                "hr.employee",
                "search",
                [
                    '&',
                    '&',
                    '|',
                    ['active', '=', False],
                    ['active', '=', True],
                    '|',
                    ['severance_day', '=', False],
                    ['severance_day', '>', start_str],
                    '|',
                    ['workingday', '=', False],
                    ['workingday', '<', nextmonthFistdayStr]
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
            list_employees = models.execute_kw(
                db,
                uid,
                password,
                "hr.employee",
                "read",
                [ids_chunk],
                {"fields": fields},
            )
            merged_data.extend(list_employees)

        # Group data by employee_code
        grouped_data = defaultdict(list)
        for record in merged_data:
            from datetime import datetime

            # Chuyển đổi các giá trị kiểu ngày tháng và kiểm tra xem chúng có bằng False không
            if 'probationary_contract_termination_date' in record:
                probationary_contract_termination_date = datetime.strptime(record['probationary_contract_termination_date'], '%Y-%m-%d').date()
                if not probationary_contract_termination_date:
                    print("Probationary Contract Termination Date is False")

            if 'severance_day' in record:
                severance_day = datetime.strptime(record['severance_day'], '%Y-%m-%d').date()
                if not severance_day:
                    print("Severance Day is False")

            if 'workingday' in record:
                workingday = datetime.strptime(record['workingday'], '%Y-%m-%d').date()
                if not workingday:
                    print("Working Day is False")

                grouped_data[record["code"]].append(record)
                print(f"{record['code']} -- {len(grouped_data[record['time_keeping_code']])}")

        # Save data to Django
        self.save_to_django(grouped_data, start_str, end_str)

    def save_to_django(self, grouped_data, start_date, end_date):
        for code, records in grouped_data.items():
            employee, created = Employee.objects.get_or_create(
                code=code,
                start_date=datetime.strptime(start_date, "%Y-%m-%d"),
                end_date=datetime.strptime(end_date, "%Y-%m-%d"),
            )
            # employee.info là record mà có severance_day = False hoặc lớn nhất, nếu có nhiều 
            # giá trị xét tiếp workingday = False hoặc workingday nhỏ nhất, nếu có nhiều 
            # lấy giá trị có id lớn nhất
            
            employee.save()
