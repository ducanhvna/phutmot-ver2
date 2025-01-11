from hrms.models import Attendance
from collections import defaultdict
import xmlrpc.client
from dashboard.models import Fleet
from datetime import datetime, timedelta
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


class AttendanceTransService():
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
        super(AttendanceTransService, self).__init__()

    def download_data(self, model_name, fields, start_str, end_str):
        LIMIT_SIZE = 300
        index = 0
        len_data = 0
        merged_array = []
        if model_name == 'hr.attendance.trans':
            domain = [[
                ("day", ">=", start_str),
                ("day", "<=", end_str)
            ]]
            if self.max_write_date_trans:
                domain[0].append((("write_date", ">", self.max_write_date_trans)))
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

    def download(self, max_write_date_trans):
        self.max_write_date_trans = max_write_date_trans
        # Format the dates
        start_str = (self.first_day_of_month - timedelta(days=1)).strftime('%Y-%m-%d')
        end_str = (self.last_day_of_month + timedelta(days=1)).strftime('%Y-%m-%d')

        print(f"Start date: {start_str}")
        print(f"End date: {end_str}")

        fields = ['id', 'name', 'day', 'time', 'in_out', 'write_date']

        merged_data = self.download_data("hr.attendance.trans", fields, start_str, end_str)
        # Group data by employee_code
        grouped_data = defaultdict(list)
        for record in merged_data:
            grouped_data[record["name"]].append(record)
            print(f"{record['name']} -- {len(grouped_data[record['name']])}")

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
        for code, records in grouped_data.items():
            attendance, created = Attendance.objects.get_or_create(
                code=code,
                start_date=datetime.strptime(start_date, "%Y-%m-%d"),
                end_date=datetime.strptime(end_date, "%Y-%m-%d"),
                defaults={"attendance_records": []},
            )
            existing_trans = attendance.attendance_records if attendance.attendance_records else []
            for _, tran in enumerate(existing_trans):
                found = False
                for record in records:
                    if tran['id'] == record['id']:
                        found = True
                        break
                if not found:
                    records.append(tran)  # Add new leave if not found
            attendance.attendance_records = records
            attendance.save()
