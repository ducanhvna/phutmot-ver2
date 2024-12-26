from django.core.management.base import BaseCommand
from django.utils import timezone
from hrms.models import Employee
from collections import defaultdict
import xmlrpc.client
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Download Employee and Contract data from Odoo and import into Django'

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
            next_month_first_day = first_day_of_month.replace(year=first_day_of_month.year + 1, month=1, day=1)
        else:
            next_month_first_day = first_day_of_month.replace(month=first_day_of_month.month + 1, day=1)

        last_day_of_month = next_month_first_day - timedelta(days=1)

        # Format the dates
        start_str = first_day_of_month.strftime('%Y-%m-%d')
        end_str = last_day_of_month.strftime('%Y-%m-%d')
        nextmonthFistdayStr = next_month_first_day.strftime('%Y-%m-%d')

        print(f"Start date: {start_str}")
        print(f"nextmonthFistdayStr: {nextmonthFistdayStr}")

        # Download employee data
        employee_fields = [
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
        employees = self.download_data(models, db, uid, password, 'hr.employee', employee_fields, start_str, nextmonthFistdayStr)

        # Group employee data
        grouped_employee_data = self.group_data(employees, 'code')

        # Download contract data
        contract_fields = [
            'id',
            'company_id',
            'contract_type_id',
            'minutes_per_day',
            'employee_code',
            'employee_id',
            'date_end',
            'date_start',
            'date_sign',
            'salary_rate',
            'state',
            'active',
            'start_end_attendance',
            'resource_calendar_id',
            'depend_on_shift_time',
            'by_hue_shift',
            'write_date'
        ]
        contracts = self.download_data(models, db, uid, password, 'hr.contract', contract_fields, start_str, nextmonthFistdayStr)

        # Process data and save to Django
        self.save_to_django(grouped_employee_data, contracts, start_str, end_str)

    def download_data(self, models, db, uid, password, model_name, fields, start_str, nextmonthFistdayStr):
        LIMIT_SIZE = 300
        index = 0
        len_data = 0
        merged_array = []
        if model_name == 'hr.employee':
            domain = [[
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
            ]]
        elif model_name == 'hr.contract':
            domain = [[
                '&',
                '&',
                ['employee_id', '!=', False],
                '|',
                ['active', '=', False],
                ['active', '=', True],
                '|',
                ['date_start', '=', False],
                ['date_start', '<', nextmonthFistdayStr]
            ]]
        else:
            raise ValueError("Invalid model name")

        while (len_data == LIMIT_SIZE) or (index == 0):
            ids = models.execute_kw(
                db,
                uid,
                password,
                model_name,
                'search',
                domain,
                {'offset': index * LIMIT_SIZE, 'limit': LIMIT_SIZE},
            )
            len_data = len(ids)
            print(ids)
            merged_array = list(set(merged_array) | set(ids))
            index += 1

        # Split ids into chunks of 200
        ids_chunks = [merged_array[i:i + 200] for i in range(0, len(merged_array), 200)]
        print(ids_chunks)
        merged_data = []

        for ids_chunk in ids_chunks:
            # Fetch data from Odoo
            data_chunk = models.execute_kw(
                db,
                uid,
                password,
                model_name,
                'read',
                [ids_chunk],
                {'fields': fields},
            )
            merged_data.extend(data_chunk)

        return merged_data

    def group_data(self, data, key):
        grouped_data = defaultdict(list)
        for record in data:
            grouped_data[record[key]].append(record)
        return grouped_data

    def save_to_django(self, grouped_employee_data, contracts, start_date, end_date):
        contract_dict = defaultdict(list)
        for contract in contracts:
            contract_dict[contract['employee_code']].append(contract)

        for employee_code, records in grouped_employee_data.items():
            # Sắp xếp các record để tìm record phù hợp
            records = sorted(records, key=lambda x: (
                x['severance_day'] is not False,
                x['severance_day'],
                x['workingday'] is not False,
                x['workingday'],
                x['id']
            ), reverse=True)

            # Lấy record phù hợp nhất
            selected_record = records[0]
            other_records = records[1:] if len(records) > 1 else []  # Các record không phải là employee.info

            employee, created = Employee.objects.get_or_create(
                employee_code=employee_code,
                start_date=datetime.strptime(start_date, "%Y-%m-%d"),
                end_date=datetime.strptime(end_date, "%Y-%m-%d"),
                defaults={
                    'info': selected_record,
                    'other_profile': other_records  # Lưu các record khác
                }
            )

            if not created:
                employee.info = selected_record
                employee.other_profile = other_records

            # Xử lý hợp đồng
            employee_contracts = contract_dict.get(employee_code, [])
            employee_contracts = sorted(employee_contracts, key=lambda x: (
                x['date_end'] is not False,
                x['date_end'],
                x['date_start'] is not False,
                x['date_start'],
                x['id']
            ), reverse=True)
            main_contract = employee_contracts[0] if len(employee_contracts) > 0 else {}
            other_contracts = [contract for contract in employee_contracts if contract != main_contract]

            # Xác định hợp đồng chính thức và hợp đồng thử việc
            if main_contract:
                contract_type = str(main_contract['contract_type_id']).lower()
                if 'chính thức' in contract_type:
                    employee.main_offical_contract = main_contract
                    employee.main_probation_contract = {}
                elif 'thử việc' in contract_type:
                    employee.main_probation_contract = main_contract
                    employee.main_offical_contract = {}

                    # Tìm hợp đồng thử việc trong các hợp đồng khác
                    probation_contracts = [contract for contract in other_contracts if 'thử việc' in str(contract['contract_type_id']).lower()]
                    if probation_contracts:
                        # Sắp xếp các hợp đồng thử việc theo các điều kiện đã cho
                        probation_contracts = sorted(probation_contracts, key=lambda x: (
                            x['date_end'] is not False,
                            x['date_end'],
                            x['date_start'] is not False,
                            x['date_start'],
                            x['id']
                        ), reverse=True)
                        employee.main_probation_contract = probation_contracts[0] if len(probation_contracts) > 0 else {}

            # Lưu thông tin hợp đồng vào employee
            employee.main_contract = main_contract
            employee.other_contracts = other_contracts

            employee.save()
