from projects.models import Project
from bot_manager.models import Chatuser
from collections import defaultdict
import xmlrpc.client
from dashboard.models import Fleet
from datetime import datetime, timedelta
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from hrms.models import Employee
from django.core.management.base import BaseCommand
import copy
from django.conf import settings  # Import settings to access the defined constants

# Define constants for Odoo connection
ODOO_URL = settings.ODOO_BASE_URL
ODOO_DB = settings.ODOO_DB
ODOO_USERNAME = settings.ODOO_USERNAME
ODOO_PASSWORD = settings.ODOO_PASSWORD


class ChatService():
    def __init__(self, first_day_of_month=None, company_merged_data=None):
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
        super(ChatService, self).__init__()

    def get_user_list(self):
        user_fields = [
            "id",
            "name",
            "login",
            "company_ids",
            "company_id",
        ]
        user_merged_data = self.download_data(
            "res.users",
            user_fields,
        )
        # Download employee data
        employee_fields = [
            "id",
            "name",
            "user_id",
            "employee_ho",
            "part_time_company_id",
            "part_time_department_id",
            "company_id",
            "code",
            "department_id",
            "time_keeping_code",
            "job_title",
            "probationary_contract_termination_date",
            "severance_day",
            "work_phone",
            "mobile_phone",
            "work_email",
            "personal_email",
            "coach_id",
            "parent_id",
            "birthday",
            "employee_type",
            "workingday",
            "probationary_salary_rate",
            "resource_calendar_id",
            "date_sign",
            "level",
            "working_status",
            "write_date",
            "active",
        ]
        employees = self.download_data('hr.employee', employee_fields)
        # Initialize empty employees list for each user and populate it
        for user in user_merged_data:
            user_id = user['id']
            user['employees'] = [employee for employee in employees if employee['user_id'] == user_id]
        self.save_user_to_django(user_merged_data=user_merged_data)

    def save_user_to_django(self, user_merged_data):
        # print('grouped_data: ', grouped_data)
        for user_record in user_merged_data:
            user, created = Chatuser.objects.get_or_create(
                identity=user_record['login'],
                defaults={"login_type": 2, "device_type": 0}
            )
            user.username = user_record['login']
            user.full_name = user_record['name']
            user.info = user_record
            user.save()

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
        return employee_grouped_data

    def download(self, max_write_date_project):
        self.max_write_date_project = max_write_date_project
        start_str = self.first_day_of_month.strftime('%Y-%m-%d')
        end_str = self.last_day_of_month.strftime('%Y-%m-%d')
        print(f"Start date: {start_str}")
        print(f"End date: {end_str}")

        employee_grouped_data = self.get_grouped_employee_data()
        # print("employee_grouped_data: ", employee_grouped_data)
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
        # print('project_merged_data', project_merged_data)
        for item in project_merged_data:
            # print('item', item)
            for employee_id in item['employee_ids']:
                if f"{employee_id}" in employee_grouped_data:
                    item_copy = copy.deepcopy(item)
                    item_copy['employee_code'] = employee_grouped_data[f"{employee_id}"]['code']
                    project_splited_data.append(item_copy)
        # Group data by employee_code
        project_grouped_data = defaultdict(list)
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
        elif model_name == "res.users":
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
        # print('grouped_data: ', grouped_data)
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


class Command(BaseCommand):
    help = "Insert initial settings into the database"

    def handle(self, *args, **kwargs):
        pass
