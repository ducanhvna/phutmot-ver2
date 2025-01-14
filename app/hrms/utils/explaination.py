from hrms.models import Shifts, Explaination
from collections import defaultdict
import xmlrpc.client
from dashboard.models import Fleet
from datetime import datetime, timedelta
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


class ExplainationService():
    def __init__(self, first_day_of_month=None, company_merged_data=None):
        # Define your Odoo connection parameters
        # Define your Odoo connection parameters
        self.url = 'https://hrm.mandalahotel.com.vn'
        self.db = 'apechrm_product_v3'
        self.username = 'admin_ho'
        self.password = '43a824d3a724da2b59d059d909f13ba0c38fcb82'
        common = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/common')
        self.uid = common.authenticate(self.db, self.username, self.password, {})
        self.models = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object')
        self.company_merged_data = company_merged_data
        if not first_day_of_month:
            first_day_of_month = datetime.now().replace(day=1)
        self.first_day_of_month = first_day_of_month

        # Lấy ngày đầu tiên của tháng trước
        self.first_day_of_last_month = self.first_day_of_month - timedelta(days=1)
        self.first_day_of_last_month = datetime(self.first_day_of_last_month.year, self.first_day_of_last_month.month, 1)
        # Calculate the last day of the current month
        if self.first_day_of_month.month == 12:
            next_month = self.first_day_of_month.replace(year=self.first_day_of_month.year + 1, month=1, day=1)
        else:
            next_month = self.first_day_of_month.replace(month=self.first_day_of_month.month + 1, day=1)

        self.last_day_of_month = next_month - timedelta(days=1)
        super(ExplainationService, self).__init__()

    def download(self, max_write_date_explaination):
        self.max_write_date_explaination = max_write_date_explaination
        start_str = self.first_day_of_month.strftime('%Y-%m-%d')
        end_str = self.last_day_of_month.strftime('%Y-%m-%d')

        print(f"Start date: {start_str}")
        print(f"End date: {end_str}")
        if not self.company_merged_data:
            company_fields = [
                'id',
                'name',
                'is_ho',
                'mis_id'
            ]
            self.company_merged_data = self.download_data("res.company", company_fields)

        # Group data by company
        company_grouped_data = {}
        for record in self.company_merged_data:
            company_grouped_data[f'{record["id"]}'] = record
            print(f"{record['id']} -- {record['name']}")
        explaination_fields = [
            'id',
            'employee_id',
            'employee_code',
            'department',
            'company_id',
            'position',
            'invalid_date',
            'invalid_type',
            'shift_from',
            'shift_to',
            'shift_break',
            'real_time_attendance_data',
            'attendance_missing_from',
            'attendance_missing_to',
            'validated',
            'reason',
            'remarks',
            'validation_data',
            'write_date'
        ]
        explaination_merged_data = self.download_data("hr.invalid.timesheet", explaination_fields, 200, start_str, end_str)
        # Group data by employee_code
        explaination_grouped_data = defaultdict(list)
        for record in explaination_merged_data:
            explaination_grouped_data[f'{record["employee_code"]}'].append(record)
            record['company_code'] = company_grouped_data[f"{record['company_id'][0]}"]['mis_id'],
            # print(f"{record['id']} -- {record['employee_code']} -- {record['reason']} -- {record['company_code']}")
        # Save data to Django
        self.save_to_django(explaination_grouped_data, start_str, end_str)
        write_dates = [
            datetime.strptime(record["write_date"], "%Y-%m-%d %H:%M:%S")
            for record in explaination_merged_data
            if record.get("write_date")
        ]

        # Get the maximum write_date or None if the list is empty
        max_write_date = max(write_dates, default=None)

        # Now max_write_date contains the maximum write_date or None if there are no dates
        print(f"Maximum write_date: {max_write_date}")

        return max_write_date

    def download_data(self, model_name, fields, limit=300, start_str=None, end_str=None):
        LIMIT_SIZE = limit
        index = 0
        len_data = 0
        merged_array = []
        if model_name == "hr.employee":
            domain = [
                [
                    '|',
                    ["active", "=", False],
                    ["active", "=", True],
                ]
            ]
        elif model_name == "hr.contract":
            domain = [
                [
                    "&",
                    ["employee_id", "!=", False],
                    "|",
                    ["active", "=", False],
                    ["active", "=", True],
                ]
            ]
        elif model_name == "hr.cl.report":
            domain = [
                [["date_calculate", "!=", False]]
            ]
        elif model_name == "hr.al.report":
            domain = [
                [["date_calculate_leave", "!=", False]]
            ]
        elif model_name == "shifts":
            domain = [
                [
                    ['company_id', "!=", False],
                    ['start_work_time', "!=", False],
                    ['end_work_time', "!=", False],
                    ['start_rest_time', "!=", False],
                    ['end_rest_time', "!=", False],
                ]
            ]
        elif model_name == "res.company":
            domain = [[]]
        elif model_name == "hr.invalid.timesheet":
            domain = [
                [
                    ['company_id', '!=', False],
                    ["invalid_date", ">=", start_str],
                    ["invalid_date", "<=", end_str],
                    ["validated", "=", "2"]
                ]
            ]
            if self.max_write_date_explaination:
                domain[0].append((("write_date", ">", self.max_write_date_explaination)))
        else:
            raise ValueError("Invalid model name")

        while (len_data == LIMIT_SIZE) or (index == 0):
            ids = self.models.execute_kw(
                self.db,
                self.uid,
                self.password,
                model_name,
                "search",
                domain,
                {"offset": index * LIMIT_SIZE, "limit": LIMIT_SIZE},
            )
            len_data = len(ids)
            print(f"{model_name} length: {len_data}")
            merged_array = list(set(merged_array) | set(ids))
            index += 1

        # Split ids into chunks of 200
        ids_chunks = [
            merged_array[i:i + 200] for i in range(0, len(merged_array), 200)
        ]
        print("chunks: ", len(ids_chunks))
        merged_data = []

        for ids_chunk in ids_chunks:
            # Fetch data from Odoo
            data_chunk = self.models.execute_kw(
                self.db,
                self.uid,
                self.password,
                model_name,
                "read",
                [ids_chunk],
                {"fields": fields},
            )
            merged_data.extend(data_chunk)

        return merged_data

    def save_to_django(self, grouped_data, start_date, end_date):
        for employee_code, records in grouped_data.items():
            explaination, created = Explaination.objects.get_or_create(
                employee_code=employee_code,
                start_date=datetime.strptime(start_date, "%Y-%m-%d"),
                end_date=datetime.strptime(end_date, "%Y-%m-%d"),
                defaults={"explaination_records": []},
            )
            existing_explainations = explaination.explaination_records if explaination.explaination_records else []
            for _, item in enumerate(existing_explainations):
                found = False
                for record in records:
                    if item['id'] == record['id']:
                        found = True
                        break
                if not found:
                    records.append(item)  # Add new leave if not found
            explaination.explaination_records = records
            explaination.save()
