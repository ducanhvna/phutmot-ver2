# your_app/management/commands/download_and_import_data.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from hrms.models import Shifts
from home.models import Company
from collections import defaultdict
import xmlrpc.client
from datetime import datetime, timedelta, time


def float_to_time(hour_float):
    """Chuyển đổi từ giờ dạng float sang thời gian dạng datetime.time"""
    hours = int(hour_float)
    minutes = int((hour_float - hours) * 60)
    return time(hour=hours, minute=minutes)


class ApecShiftService():
    def __init__(self):
        # Define your Odoo connection parameters
        # Define your Odoo connection parameters
        self.url = 'https://hrm.mandalahotel.com.vn'
        self.db = 'apechrm_product_v3'
        self.username = 'admin_ho'
        self.password = '43a824d3a724da2b59d059d909f13ba0c38fcb82'
        common = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/common')
        self.uid = common.authenticate(self.db, self.username, self.password, {})
        self.models = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object')

        # if not first_day_of_month:
        #     first_day_of_month = datetime.now().replace(day=1)
        # self.first_day_of_month = first_day_of_month

        # # Lấy ngày đầu tiên của tháng trước
        # self.first_day_of_last_month = self.first_day_of_month - timedelta(days=1)
        # self.first_day_of_last_month = datetime(self.first_day_of_last_month.year, self.first_day_of_last_month.month, 1)
        # # Calculate the last day of the current month
        # if self.first_day_of_month.month == 12:
        #     next_month = self.first_day_of_month.replace(year=self.first_day_of_month.year + 1, month=1, day=1)
        # else:
        #     next_month = self.first_day_of_month.replace(month=self.first_day_of_month.month + 1, day=1)

        # self.last_day_of_month = next_month - timedelta(days=1)
        super(ApecShiftService, self).__init__()

    def download_copanies(self, max_write_date_companies=None):
        self.max_write_date_companies = max_write_date_companies
        company_fields = [
            'id',
            'name',
            'is_ho',
            'mis_id',
            'write_date'
        ]
        self.company_merged_data = self.download_data("res.company", company_fields)

        # Group data by company
        self.company_grouped_data = {}
        for record in self.company_merged_data:
            self.company_grouped_data[f'{record["id"]}'] = record
            print(f"{record['id']} -- {record['name']}")

    def download_shift(self, max_write_date_shifts=None):
        self.max_write_date_shifts = max_write_date_shifts
        shift_fields = [
            'id',
            'name',
            'start_work_time',
            'end_work_time',
            'total_work_time',
            'start_rest_time',
            'end_rest_time',
            'company_id',
            'rest_shifts',
            'fix_rest_time',
            'night',
            'night_eat',
            'dinner',
            'lunch',
            'breakfast',
            'efficiency_factor',
            'is_ho_shift',
            'night_ph_efficiency_factor',
            'minutes_working_not_reduced',
            'write_date'
        ]
        shift_merged_data = self.download_data("shifts", shift_fields)
        # Group data by employee_code
        shift_grouped_data = {}
        for record in shift_merged_data:
            shift_grouped_data[f'{record["name"]}_{record["company_id"][0]}_{record["company_id"][1]}'] = record
            print(f"{record['id']} -- {record['name']} -- {float_to_time(record['start_work_time'])}")
        # Save data to Django
        self.save_to_django(shift_grouped_data)
        write_dates = [
            datetime.strptime(record["write_date"], "%Y-%m-%d %H:%M:%S")
            for record in shift_merged_data
            if record.get("write_date")
        ]
        # Get the maximum write_date or None if the list is empty
        max_write_date = max(write_dates, default=None)

        # Now max_write_date contains the maximum write_date or None if there are no dates
        print(f"Maximum write_date: {max_write_date}")

        return max_write_date

    def download_data(self, model_name, fields, limit=300):
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
            if self.max_write_date_shifts:
                domain[0].append((("write_date", ">", self.max_write_date_shifts)))
        elif model_name == "res.company":
            domain = [[]]
            if self.max_write_date_companies:
                domain[0].append((("write_date", ">", self.max_write_date_companies)))
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

    def save_to_django(self, grouped_data):
        company, _ = Company.objects.get_or_create(
            company_code='APEC',
            company_name='APEC GROUP',
            defaults={'info': {"max_write_date": None}}
        )
        company.info['companies'] = self.company_merged_data
        company.save()

        for company_info, record in grouped_data.items():
            try:
                shifts, created = Shifts.objects.get_or_create(
                    name=record['name'],
                    company_code=self.company_grouped_data[f"{record['company_id'][0]}"]['mis_id'],
                )
                shifts.start_work_time = float_to_time(record['start_work_time'])
                shifts.end_work_time = float_to_time(record['end_work_time'])
                shifts.start_rest_time = float_to_time(record['start_rest_time'])
                shifts.end_rest_time = float_to_time(record['end_rest_time'])
                shifts.info = record
                shifts.save()
            except Exception as ex:
                print(ex)
                print("Time to process: ", float_to_time(record['start_work_time']))
