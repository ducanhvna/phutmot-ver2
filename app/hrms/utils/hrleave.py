from hrms.models import Leave
from collections import defaultdict
import xmlrpc.client
from dashboard.models import Fleet
from datetime import datetime, timedelta
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


class LeaveService():
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
            next_month = self.first_day_of_month.replace(year=self.first_day_of_month.year + 1, month=1, day=1)
        else:
            next_month = self.first_day_of_month.replace(month=self.first_day_of_month.month + 1, day=1)

        self.last_day_of_month = next_month - timedelta(days=1)
        super(LeaveService, self).__init__()

    def download_data(self, model_name, fields, start_str, end_str):
        LIMIT_SIZE = 300
        index = 0
        len_data = 0
        merged_array = []
        if model_name == 'hr.leave':
            domain = [[
                ("request_date_to", ">=", start_str),
                ("request_date_from", "<=", end_str),
                ("active", "=", True),
                ("state", "=", "validate"),
            ]]
            if self.max_write_date_leave:
                domain[0].append((("write_date", ">", self.max_write_date_leave)))
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
        print("chunks: ", lend(ids_chunks))
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

    def download(self, max_write_date_leave):
        self.max_write_date_leave = max_write_date_leave
        # Format the dates
        start_str = self.first_day_of_month.strftime('%Y-%m-%d')
        end_str = self.last_day_of_month.strftime('%Y-%m-%d')

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

        merged_data = self.download_data('hr.leave', fields, start_str, end_str)
        # Group data by employee_code
        grouped_data = defaultdict(list)
        for record in merged_data:
            grouped_data[record["employee_code"]].append(record)
            print(f"{record['employee_code']} -- {len(grouped_data[record['employee_code']])} -- {record['holiday_status_id']}")

        # Save data to Django
        self.save_to_django(grouped_data, start_str, end_str)
        write_dates = [
            datetime.strptime(record["write_date"], "%Y-%m-%d %H:%M:%S")
            for record in merged_data
            if record.get("write_date")
        ]

        # Get the maximum write_date or None if the list is empty
        max_write_date = max(write_dates, default=None)

        # Now max_write_date contains the maximum write_date or None if there are no dates
        print(f"Maximum write_date: {max_write_date}")

        return max_write_date

    def save_to_django(self, grouped_data, start_date, end_date):
        for employee_code, records in grouped_data.items():
            hrleave, created = Leave.objects.get_or_create(
                employee_code=employee_code,
                start_date=datetime.strptime(start_date, "%Y-%m-%d"),
                end_date=datetime.strptime(end_date, "%Y-%m-%d"),
                defaults={"leave_records": []},
            )
            existing_leaves = hrleave.leave_records if hrleave.leave_records else []
            # updated_leaves = []
            # Update existing leaves or add new ones
            for _, leave in enumerate(existing_leaves):
                found = False
                for record in records:
                    if leave['id'] == record['id']:
                        found = True
                        break
                if not found:
                    records.append(leave)  # Add new leave if not found
            # records = records.extend(updated_leaves)
            hrleave.leave_records = records
            hrleave.save()
