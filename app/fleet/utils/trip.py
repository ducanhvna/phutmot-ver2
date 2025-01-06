from fleet.models import Vehicle
from collections import defaultdict
import xmlrpc.client
from datetime import datetime, timedelta


class Trip():
    def __init__(self, first_day_of_month=None):
        # Define your Odoo connection parameters
        if not first_day_of_month:
            first_day_of_month = datetime.now().replace(day=1)
        self.first_day_of_month = first_day_of_month

        # Lấy ngày đầu tiên của tháng trước
        self.first_day_of_last_month = self.first_day_of_month - timedelta(days=1)
        self.first_day_of_last_month = datetime(self.first_day_of_last_month.year, self.first_day_of_last_month.month, 1)

        self.url = 'https://vantaihahai.com'
        self.db = 'fleet'
        self.username = 'admin'
        self.password = 'admin'
        common = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/common')
        self.uid = common.authenticate(self.db, self.username, self.password, {})
        self.models = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object')
        super(Trip, self).__init__()

    def download(self):
        # Calculate the last day of the current month
        if self.first_day_of_month.month == 12:
            next_month = self.first_day_of_month.replace(year=self.first_day_of_month.year + 1, month=1, day=1)
        else:
            next_month = self.first_day_of_month.replace(month=self.first_day_of_month.month + 1, day=1)

        last_day_of_month = next_month - timedelta(days=1)

        # Format the dates
        start_str = (self.first_day_of_month - timedelta(days=1)).strftime('%Y-%m-%d')
        end_str = (last_day_of_month + timedelta(days=1)).strftime('%Y-%m-%d')

        print(f"Start date: {start_str}")
        print(f"End date: {end_str}")

        fields = ['id', 'name', 'day', 'time', 'in_out', 'write_date']
        LIMIT_SIZE = 300
        index = 0
        len_data = 0
        merged_array = []
        while (len_data == LIMIT_SIZE) or (index == 0):
            ids = self.models.execute_kw(
                self.db,
                self.uid,
                self.password,
                "fleet.trip",
                "search",
                [
                    [
                        ("day", ">=", start_str),
                        ("day", "<=", end_str)
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
            list_attendance_trans = self.models.execute_kw(
                self.db,
                self.uid,
                self.password,
                "hr.attendance.trans",
                "read",
                [ids_chunk],
                {"fields": fields},
            )
            merged_data.extend(list_attendance_trans)

        # Group data by employee_code
        grouped_data = defaultdict(list)
        for record in merged_data:
            grouped_data[record["name"]].append(record)
            print(f"{record['name']} -- {len(grouped_data[record['name']])}")

        # Save data to Django
        self.save_to_django(grouped_data, start_str, end_str)

    def save_to_django(self, grouped_data, start_date, end_date):
        for code, records in grouped_data.items():
            attendance, created = Vehicle.objects.get_or_create(
                code=code,
                start_date=datetime.strptime(start_date, "%Y-%m-%d"),
                end_date=datetime.strptime(end_date, "%Y-%m-%d"),
            )
            attendance.attendance_records = records
            attendance.save()
