# your_app/management/commands/download_and_import_data.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from hrms.models import Shifts
from collections import defaultdict
import xmlrpc.client
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Download data from Odoo and import into Django'

    def handle(self, *args, **kwargs):
        # Define your Odoo connection parameters
        url = 'https://hrm.mandalahotel.com.vn'
        db = 'apechrm_product_v3'
        username = 'admin_ho'
        password = '43a824d3a724da2b59d059d909f13ba0c38fcb82'

        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        uid = common.authenticate(db, username, password, {})
        models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

        company_fields = [
            'id',
            'name',
            'is_ho',
            'mis_id'
        ]
        company_merged_data = self.download_data(model, db, uid, password, "res.company", company_fields)

        # Group data by company
        company_grouped_data = defaultdict(list)
        for record in company_merged_data:
            company_grouped_data[f'{record["id"]}'].append(record)
            print(f"{record['id']} -- {len(grouped_data[record['name']])}")
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
        shift_merged_data = self.download_data(model, db, uid, password, "shifts", shift_fields)
        # Group data by employee_code
        shift_grouped_data = defaultdict(list)
        for record in shift_merged_data:
            shift_grouped_data[f'{record["company_id"][0]}_{record["company_id"][1]}'].append(record)
            print(f"{record['id']} -- {len(grouped_data[record['name']])}")
        # Save data to Django
        self.save_to_django(grouped_data, shift_grouped_data, company_grouped_data)

    def download_data(self, models, db, uid, password, model_name, fields, limit=300):
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
            domain = [[['company_id', "!=", False]]]
        elif model_name == "res.company":
            domain = [[]]
        else:
            raise ValueError("Invalid model name")

        while (len_data == LIMIT_SIZE) or (index == 0):
            ids = models.execute_kw(
                db,
                uid,
                password,
                model_name,
                "search",
                domain,
                {"offset": index * LIMIT_SIZE, "limit": LIMIT_SIZE},
            )
            len_data = len(ids)
            print(ids)
            merged_array = list(set(merged_array) | set(ids))
            index += 1

        # Split ids into chunks of 200
        ids_chunks = [
            merged_array[i:i + 200] for i in range(0, len(merged_array), 200)
        ]
        print(ids_chunks)
        merged_data = []

        for ids_chunk in ids_chunks:
            # Fetch data from Odoo
            data_chunk = models.execute_kw(
                db,
                uid,
                password,
                model_name,
                "read",
                [ids_chunk],
                {"fields": fields},
            )
            merged_data.extend(data_chunk)

        return merged_data

    def save_to_django(self, grouped_data, grouped_data, company_grouped_data):
        for company_info, records in grouped_data.items():
            for record in records:
                shifts, created = Shifts.objects.get_or_create(
                    name=record['name'],
                    company_code=company_grouped_data[f"{record['company_id'][0]}"]['mis_id'],
                )
                shifts.info = record
                shifts.save()
