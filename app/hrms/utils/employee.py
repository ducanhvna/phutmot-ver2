from hrms.models import Employee
from collections import defaultdict
import xmlrpc.client
from datetime import datetime, timedelta


class EmployeeService():
    def __init__(self, first_day_of_month=None):
        # Define your Odoo connection parameters
        # Define your Odoo connection parameters
        self.url = 'https://hrm.mandalahotel.com.vn'
        self.db = 'apechrm_product_v3'
        self.username = 'admin_ho'
        self.password = '43a824d3a724da2b59d059d909f13ba0c38fcb82'
        common = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/common')
        self.uid = common.authenticate(self.db, self.username, self.password, {})
        self.models = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object')

        if not first_day_of_month:
            first_day_of_month = datetime.now().replace(day=1)
        self.first_day_of_month = first_day_of_month

        # Lấy ngày đầu tiên của tháng trước
        self.first_day_of_last_month = self.first_day_of_month - timedelta(days=1)
        self.first_day_of_last_month = datetime(self.first_day_of_last_month.year, self.first_day_of_last_month.month, 1)
        # Calculate the last day of the current month
        if self.first_day_of_month.month == 12:
            self.next_month_first_day = self.first_day_of_month.replace(year=self.first_day_of_month.year + 1, month=1, day=1)
        else:
            self.next_month_first_day = self.first_day_of_month.replace(month=self.first_day_of_month.month + 1, day=1)

        self.last_day_of_month = self.next_month_first_day - timedelta(days=1)
        super(EmployeeService, self).__init__()

    def download(self, max_write_date_employees):
        self.max_write_date_employees = max_write_date_employees
        # Format the dates
        start_str = self.first_day_of_month.strftime('%Y-%m-%d')
        end_str = self.last_day_of_month.strftime('%Y-%m-%d')
        nextmonthFistdayStr = self.next_month_first_day.strftime('%Y-%m-%d')

        print(f" Employee Start date: {start_str}")
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
            'work_phone',
            'mobile_phone',
            'work_email',
            'personal_email',
            'coach_id',
            'parent_id',
            'birthday',
            'employee_type',
            'workingday',
            'probationary_salary_rate',
            'resource_calendar_id',
            'date_sign',
            'level',
            'working_status',
            'write_date',
            'active'
        ]
        employees = self.download_data('hr.employee', employee_fields, start_str, nextmonthFistdayStr)

        # Group employee data
        grouped_employee_data = self.group_data(employees, 'code')

        # Download contract data
        contract_fields = [
            'id',
            'name',
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
        contracts = self.download_data('hr.contract', contract_fields, start_str, nextmonthFistdayStr)

        # Process data and save to Django
        self.save_to_django(grouped_employee_data, contracts, start_str, end_str)
        write_dates = [
            datetime.strptime(record["write_date"], "%Y-%m-%d %H:%M:%S")
            for record in employees
            if record.get("write_date")
        ]

        # Get the maximum write_date or None if the list is empty
        max_write_date = max(write_dates, default=None)

        # Now max_write_date contains the maximum write_date or None if there are no dates
        print(f"Maximum write_date: {max_write_date}")

        return max_write_date

    def download_data(self, model_name, fields, start_str, nextmonthFistdayStr):
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
            ids = self.models.execute_kw(
                self.db,
                self.uid,
                self.password,
                model_name,
                'search',
                domain,
                {'offset': index * LIMIT_SIZE, 'limit': LIMIT_SIZE},
            )
            len_data = len(ids)
            print(f"{model_name} length: {len_data}")
            merged_array = list(set(merged_array) | set(ids))
            index += 1

        # Split ids into chunks of 200
        ids_chunks = [merged_array[i:i + 200] for i in range(0, len(merged_array), 200)]
        print("chunks: ", len(ids_chunks))
        merged_data = []

        for ids_chunk in ids_chunks:
            # Fetch data from Odoo
            data_chunk = self.models.execute_kw(
                self.db,
                self.uid,
                self.password,
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
            employee, created = Employee.objects.get_or_create(
                employee_code=employee_code,
                start_date=datetime.strptime(start_date, "%Y-%m-%d"),
                end_date=datetime.strptime(end_date, "%Y-%m-%d"),
                defaults={
                    'info': [],
                    'other_profile': []  # Lưu các record khác
                }
            )
            # employee_info = employee.info if employee.info else []
            employee_other_profile = employee.other_profile if employee.other_profile else []
            if employee.info:
                existing_employees = employee_other_profile.append(employee.info)
            else:
                existing_employees = []
            existing_employees = existing_employees if existing_employees else []
            for _, epl in enumerate(existing_employees):
                found = False
                for record in records:
                    if epl['id'] == record['id']:
                        found = True
                        break
                if not found:
                    records.append(epl)  # Add new leave if not found

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

                    # Tìm hợp đồng thử việc trong các hợp đồng khác
                    probation_contracts = [contract for contract in other_contracts if not ('chính thức' in str(contract['contract_type_id']).lower())]
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
                else:
                    employee.main_probation_contract = main_contract
                    employee.main_offical_contract = {}

            # Lưu thông tin hợp đồng vào employee
            employee.main_contract = main_contract
            employee.other_contracts = other_contracts
            employee.time_keeping_code = selected_record['time_keeping_code']

            employee.save()
