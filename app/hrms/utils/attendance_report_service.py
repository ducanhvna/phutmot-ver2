from hrms.models import Scheduling
from collections import defaultdict
import xmlrpc.client
from dashboard.models import Fleet
from datetime import datetime, timedelta
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


class AttendanceReportService():
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
        super(AttendanceReportService, self).__init__()

    def download_data(self, model_name, fields, start_str, end_str):
        LIMIT_SIZE = 300
        index = 0
        len_data = 0
        merged_array = []
        if model_name == 'hr.apec.attendance.report':
            domain = [["&", ("date", ">=", start_str), ("date", "<=", end_str)]]
            if self.max_write_date_reports:
                domain[0].append((("write_date", ">", self.max_write_date_reports)))
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
            print(ids)
            merged_array = list(set(merged_array) | set(ids))
            index += 1

        # Split ids into chunks of 200
        ids_chunks = [merged_array[i:i + 200] for i in range(0, len(merged_array), 200)]
        print(ids_chunks)
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

    def download(self, max_write_date_reports):
        self.max_write_date_reports = max_write_date_reports
        # Format the dates
        start_str = self.first_day_of_month.strftime('%Y-%m-%d')
        end_str = self.last_day_of_month.strftime('%Y-%m-%d')

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

        merged_data = self.download_data("hr.apec.attendance.report", fields, start_str, end_str)
        # Group data by employee_code
        grouped_data = defaultdict(list)
        for record in merged_data:
            grouped_data[record["employee_code"]].append(record)
            print(f"{record['employee_code']} -- {len(grouped_data[record['employee_code']])}")

        # Save data to Django
        self.grouped_total_worktime_by_company = {}
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

    def group_by_company(self, merged_data):
        # companies = defaultdict(lambda: [0] * (self.last_day_of_month.day))
        for record in merged_data:
            company = record["company"]
            date = datetime.strptime(record["date"], "%Y-%m-%d").day - 1
            total_work_time = record.get("actual_total_work_time", 0)
            if company not in self.grouped_total_worktime_by_company:
                self.grouped_total_worktime_by_company[company] = [0] * (self.last_day_of_month.day)
            self.grouped_total_worktime_by_company[company][date] += total_work_time // 60

    def save_to_django(self, grouped_data, start_date, end_date):
        for employee_code, records in grouped_data.items():
            scheduling, created = Scheduling.objects.get_or_create(
                employee_code=employee_code,
                start_date=datetime.strptime(start_date, "%Y-%m-%d"),
                end_date=datetime.strptime(end_date, "%Y-%m-%d"),
                defaults={"scheduling_records": []},
            )
            existing_reports = scheduling.scheduling_records if scheduling.scheduling_records else []
            for _, report in enumerate(existing_reports):
                found = False
                for record in records:
                    if report['id'] == record['id']:
                        found = True
                        break
                if not found:
                    records.append(report)  # Add new leave if not found
            self.group_by_company(records)
            scheduling.scheduling_records = records
            scheduling.save()
