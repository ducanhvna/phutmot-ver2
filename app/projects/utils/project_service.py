from projects.models import Project
from collections import defaultdict
import xmlrpc.client
from dashboard.models import Fleet
from datetime import datetime, timedelta
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from hrms.models import Employee
import copy

ODOO_URL = "http://odoo17:8069"
ODOO_DB = "odoo"
ODOO_USERNAME = "admin"
ODOO_PASSWORD = "admin"


class ProjectService():
    def __init__(self, first_day_of_month=None, company_merged_data=None):
        # Define your Odoo connection parameters
        # Define your Odoo connection parameters
        self.url = ODOO_URL
        self.db = ODOO_DB
        self.username = ODOO_USERNAME
        self.password = ODOO_PASSWORD
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
        super(ProjectService, self).__init__()

    def get_grouped_employee_data(self):
        employee_fields = [
            "id",
            "active",
            "code",
        ]
        employee_merged_data = self.download_data(
            "hr.employee",
            employee_fields,
        )
        employee_grouped_data = {}
        for record in employee_merged_data:
            employee_grouped_data[f'{record["id"]}'] = record
        return employee_merged_data

    def download(self, max_write_date_project):
        self.max_write_date_project = max_write_date_project
        start_str = self.first_day_of_month.strftime('%Y-%m-%d')
        end_str = self.last_day_of_month.strftime('%Y-%m-%d')
        print(f"Start date: {start_str}")
        print(f"End date: {end_str}")

        employee_grouped_data = self.get_grouped_employee_data()
        print("employee_grouped_data: ", employee_grouped_data)
        project_fields = [
            'id',
            'name',
            'display_name',
            'label_tasks',
            'code',
            'department_id',
            'company_id',
            'date_start',
            'date',
            'is_daily',
            'employee_ids',
            'write_date'
        ]
        project_merged_data = self.download_data("project.project", project_fields, 200, start_str, end_str)
        project_splited_data = []
        print('project_merged_data', project_merged_data)
        for item in project_merged_data:
            print('item', item)
            for employee_id in item['employee_ids']:
                if f"{employee_id}" in employee_grouped_data:
                    item_copy = copy.deepcopy(item)
                    item_copy['employee_code'] = employee_grouped_data[f"{employee_id}"]['code']
                    project_splited_data.append(item_copy)
        # Group data by employee_code
        project_grouped_data = {}
        for record in project_splited_data:
            project_grouped_data[f'{record["employee_code"]}'].append(record)

        # Save data to Django
        self.save_to_django(project_grouped_data, start_str, end_str)
        write_dates = [
            datetime.strptime(record["write_date"], "%Y-%m-%d %H:%M:%S")
            for record in project_merged_data
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
        elif model_name == "project.project":
            domain = [
                [
                    '&',
                    # ['company_id', '!=', False],
                    ["date_start", "<=", end_str],
                    '|',
                    ["date", ">=", start_str],
                    ["date", "=", False]
                ]
            ]
            if self.max_write_date_project:
                domain[0].append((("write_date", ">", self.max_write_date_project)))
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
        print('grouped_data: ', grouped_data)
        for employee_code, records in grouped_data.items():
            project, created = Project.objects.get_or_create(
                employee_code=employee_code,
                start_date=datetime.strptime(start_date, "%Y-%m-%d"),
                end_date=datetime.strptime(end_date, "%Y-%m-%d"),
                defaults={"info": {}},
            )
            project_records = project.info.get('records', [])
            existing_projects = project_records if project_records else []
            for _, item in enumerate(existing_projects):
                found = False
                for record in records:
                    if item['id'] == record['id']:
                        found = True
                        break
                if not found:
                    records.append(item)  # Add new leave if not found
            project.info["records"] = records
            project.save()
