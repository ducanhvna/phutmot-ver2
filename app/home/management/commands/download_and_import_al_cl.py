from django.core.management.base import BaseCommand
from django.utils import timezone
from home.models import UserProfile
from collections import defaultdict
import xmlrpc.client
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = "Download UserProfile and Contract data from Odoo and import into Django"

    def handle(self, *args, **kwargs):
        # Define your Odoo connection parameters
        url = "https://hrm.mandalahotel.com.vn"
        db = "apechrm_product_v3"
        username = "admin_ho"
        password = "43a824d3a724da2b59d059d909f13ba0c38fcb82"

        common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
        uid = common.authenticate(db, username, password, {})
        models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")

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

        employees = self.download_data(
            models,
            db,
            uid,
            password,
            "hr.employee",
            employee_fields,
        )

        cl_fields = [
            "id",
            "year",
            "date_calculate",
            "employee_id",
            "tier",
            "employee_code",
            "company_id",
            "department_id",
            "job_title",
            "workingday",
            "date_sign",
            "contract_type_id",
            "severance_day",
            "increase_probationary_1",
            "increase_official_1",
            "used_probationary_1",
            "used_official_1",
            "overtime_probationary_1",
            "overtime_official_1",
            "increase_probationary_2",
            "increase_official_2",
            "used_probationary_2",
            "used_official_2",
            "overtime_probationary_2",
            "overtime_official_2",
            "increase_probationary_3",
            "increase_official_3",
            "used_probationary_3",
            "used_official_3",
            "overtime_probationary_3",
            "overtime_official_3",
            "increase_probationary_4",
            "increase_official_4",
            "used_probationary_4",
            "used_official_4",
            "overtime_probationary_4",
            "overtime_official_4",
            "increase_probationary_5",
            "increase_official_5",
            "used_probationary_5",
            "used_official_5",
            "overtime_probationary_5",
            "overtime_official_5",
            "increase_probationary_6",
            "increase_official_6",
            "used_probationary_6",
            "used_official_6",
            "overtime_probationary_6",
            "overtime_official_6",
            "increase_probationary_7",
            "increase_official_7",
            "used_probationary_7",
            "used_official_7",
            "overtime_probationary_7",
            "overtime_official_7",
            "increase_probationary_8",
            "increase_official_8",
            "used_probationary_8",
            "used_official_8",
            "overtime_probationary_8",
            "overtime_official_8",
            "increase_probationary_9",
            "increase_official_9",
            "used_probationary_9",
            "used_official_9",
            "overtime_probationary_9",
            "overtime_official_9",
            "increase_probationary_10",
            "increase_official_10",
            "used_probationary_10",
            "used_official_10",
            "overtime_probationary_10",
            "overtime_official_10",
            "increase_probationary_11",
            "increase_official_11",
            "used_probationary_11",
            "used_official_11",
            "overtime_probationary_11",
            "overtime_official_11",
            "increase_probationary_12",
            "increase_official_12",
            "used_probationary_12",
            "used_official_12",
            "overtime_probationary_12",
            "overtime_official_12",
            "remaining_total_day",
            "remaining_probationary_minute",
            "remaining_official_minute",
            "remaining_total_minute",
            "total_increase_probationary",
            "total_increase_official",
            "total_increase_tv_ovt",
            "total_increase_ct_ovt",
            "total_used_probationary",
            "total_used_official",
            "remaining_probationary_minute",
            "remaining_official_minute",
            "remaining_total_minute",
            "remaining_probationary_day",
            "remaining_official_day",
            "remaining_total_day",
            "write_date",
        ]
        employee_cl = self.download_data(
            models,
            db,
            uid,
            password,
            "hr.cl.report",
            cl_fields,
            100
        )
        # Group employee data
        grouped_employee_data = self.group_data(employees, "code")
        al_fields = [
            "id",
            "year",
            "date_calculate_leave",
            "employee_id",
            "company_id",
            "employee_code",
            "department_id",
            "standard_day",
            "workingday",
            "date_sign",
            "date_apply_leave",
            "severance_day",
            "seniority_leave",
            "job_title",
            "family_leave",
            "leave_increase_by_seniority_leave",
            "leave_day",
            "leave_year",
            "remaining_leave",
            "january",
            "february",
            "march",
            "april",
            "may",
            "june",
            "july",
            "august",
            "september",
            "october",
            "november",
            "december",
            "leave_used",
            "remaining_leave_minute",
            "remaining_leave_day",
            "note",
            "file",
            "employee_ho",
            "part_time_company_id",
            "write_date",
        ]
        employee_al = self.download_data(
            models,
            db,
            uid,
            password,
            "hr.al.report",
            al_fields,
            100
        )
        # Download contract data
        contract_fields = [
            "id",
            "name",
            "company_id",
            "contract_type_id",
            "minutes_per_day",
            "employee_code",
            "employee_id",
            "date_end",
            "date_start",
            "date_sign",
            "salary_rate",
            "state",
            "active",
            "start_end_attendance",
            "resource_calendar_id",
            "depend_on_shift_time",
            "by_hue_shift",
            "write_date",
        ]
        contracts = self.download_data(
            models,
            db,
            uid,
            password,
            "hr.contract",
            contract_fields
        )

        # Process data and save to Django
        self.save_to_django(grouped_employee_data, contracts, employee_cl, employee_al)

    def download_data(
        self, models, db, uid, password, model_name, fields, limit= 300
    ):
        LIMIT_SIZE = limit
        index = 0
        len_data = 0
        merged_array = []
        if model_name == "hr.employee":
            domain = [
                [
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

    def group_data(self, data, key):
        grouped_data = defaultdict(list)
        for record in data:
            grouped_data[record[key]].append(record)
        return grouped_data

    def save_to_django(self, grouped_employee_data, contracts, cls, als):
        contract_dict = defaultdict(list)
        for contract in contracts:
            contract_dict[contract["employee_code"]].append(contract)

        cl_dict = defaultdict(list)
        for cl in cls:
            cl_dict[cl["employee_code"]].append(cl)

        al_dict = defaultdict(list)
        for al in als:
            al_dict[al["employee_code"]].append(al)

        for employee_code, records in grouped_employee_data.items():
            # Sắp xếp các record để tìm record phù hợp
            records = sorted(
                records,
                key=lambda x: (
                    x["severance_day"] is not False,
                    x["severance_day"],
                    x["workingday"] is not False,
                    x["workingday"],
                    x["id"],
                ),
                reverse=True,
            )
            # Lấy record phù hợp nhất
            selected_record = records[0]
            other_records = records[1:] if len(records) > 1 else []  # Các record không phải là employee.info
            # Lấy record phù hợp nhất
            profile, created = UserProfile.objects.get_or_create(
                employee_code=employee_code,
                defaults={
                    "info": selected_record,
                    "other_profile": other_records,  # Lưu các record khác
                },
            )

            if not created:
                profile.info = selected_record
                profile.other_profile = other_records

            # Xử lý hợp đồng
            employee_contracts = contract_dict.get(employee_code, [])
            profile.contracts = sorted(
                employee_contracts,
                key=lambda x: (
                    x["date_end"] is not False,
                    x["date_end"],
                    x["date_start"] is not False,
                    x["date_start"],
                    x["id"],
                ),
                reverse=True,
            )
            employee_cls = cl_dict.get(employee_code, [])
            profile.cl = sorted(
                employee_cls, key=lambda x: (x["date_calculate"],), reverse=True
            )

            employee_als = al_dict.get(employee_code, [])
            profile.al = sorted(
                employee_als, key=lambda x: (x["date_calculate_leave"],), reverse=True
            )

            profile.save()
