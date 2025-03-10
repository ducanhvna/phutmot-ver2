from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Q
from .models import Employee
from home.models import UserProfile
import xmlrpc.client
import json
from datetime import datetime
from dateutil.parser import parse
from django.core.paginator import Paginator
from hrms.utils.odoo_xmlrpc import OdooXMLRPC

ODOO_URL = "http://odoo17:8069"
ODOO_DB = "odoo"
ODOO_USERNAME = "admin"
ODOO_PASSWORD = "admin"


def get_projects_from_odoo():
    url = ODOO_URL
    db = ODOO_DB
    username = ODOO_USERNAME
    password = ODOO_PASSWORD
    common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
    uid = common.authenticate(db, username, password, {})
    models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
    projects = models.execute_kw(db, uid, password, 'project.project', 'search_read', [[], ['id', 'name']])
    return projects


class TaskCreateView(View):
    def get(self, request):
        projects = get_projects_from_odoo()
        return render(request, 'hrms/task_create.html', {'projects': projects})


@method_decorator(csrf_exempt, name='dispatch')
class TaskCreateAPIView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        url = ODOO_URL
        db = ODOO_DB
        username = ODOO_USERNAME
        password = ODOO_PASSWORD
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        uid = common.authenticate(db, username, password, {})
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

        task_id = models.execute_kw(db, uid, password, 'project.task', 'create', [{
            'name': data['name'],
            # 'project_id': data['project_id'],
            # 'stage_id': data['stage'],
            # 'date_start': data['start_date'],
            'date_deadline': parse(data['deadline']).strftime('%Y-%m-%d %H:%M:%S'),
        }])

        return JsonResponse({'task_id': task_id})


class AlTablesView(View):
    def get(self, request):
        start_datetime = datetime(2024, 12, 1, 0, 0, 0)  # December 1, 2024 at 00:00:00
        filtered_profiles = Employee.objects.filter(
            Q(info__company_id__0=18), start_date=start_datetime
        )
        # Step 2: Extract employee_code
        employee_code_array = [
            emp.employee_code for emp in filtered_profiles if emp.employee_code
        ]

        # Step 3: Fetch UserProfile records
        user_profiles = UserProfile.objects.filter(
            employee_code__in=employee_code_array
        )

        # Step 4: Merge the two lists based on employee_code
        merged_profiles = []
        for emp in filtered_profiles:
            matching_user_profiles = [
                up for up in user_profiles if up.employee_code == emp.employee_code
            ]
            for up in matching_user_profiles:
                merged_profile = {"employee": emp, "user_profile": up}
                filtered_al = [entry for entry in up.al if entry.get("date_calculate_leave") == "2025-02-01"]
                merged_profile['january'] = 0 if not filtered_al else filtered_al[-1].get("january", 0)
                merged_profile['february'] = 0 if not filtered_al else filtered_al[-1].get("february", 0)
                merged_profile['march'] = 0 if not filtered_al else filtered_al[-1].get("march", 0)
                merged_profile['april'] = 0 if not filtered_al else filtered_al[-1].get("april", 0)
                merged_profile['may'] = 0 if not filtered_al else filtered_al[-1].get("may", 0)
                merged_profile['june'] = 0 if not filtered_al else filtered_al[-1].get("june", 0)
                merged_profile['july'] = 0 if not filtered_al else filtered_al[-1].get("july", 0)
                merged_profile['august'] = 0 if not filtered_al else filtered_al[-1].get("august", 0)
                merged_profile['september'] = 0 if not filtered_al else filtered_al[-1].get("september", 0)
                merged_profile['october'] = 0 if not filtered_al else filtered_al[-1].get("october", 0)
                merged_profile['november'] = 0 if not filtered_al else filtered_al[-1].get("november", 0)
                merged_profile['december'] = 0 if not filtered_al else filtered_al[-1].get("december", 0)
                merged_profiles.append(merged_profile)

        return render(request, "hrms/al_tables.html", {"profiles": merged_profiles})


class ClTablesView(View):
    def get(self, request):
        start_datetime = datetime(2024, 12, 1, 0, 0, 0)  # December 1, 2024 at 00:00:00
        filtered_profiles = Employee.objects.filter(
            Q(info__company_id__0=18), start_date=start_datetime
        )
        # Step 2: Extract employee_code
        employee_code_array = [
            emp.employee_code for emp in filtered_profiles if emp.employee_code
        ]

        # Step 3: Fetch UserProfile records
        user_profiles = UserProfile.objects.filter(
            employee_code__in=employee_code_array
        )

        # Step 4: Merge the two lists based on employee_code
        merged_profiles = []
        for emp in filtered_profiles:
            matching_user_profiles = [
                up for up in user_profiles if up.employee_code == emp.employee_code
            ]
            for up in matching_user_profiles:
                merged_profile = {"employee": emp, "user_profile": up}
                filtered_cl = [entry for entry in up.cl if entry.get("date_calculate") == "2025-02-01"]
                for month_index in range(1, 13):
                    merged_profile[f'increase_probationary_{month_index}'] = 0 if not filtered_cl else filtered_cl[-1].get(f"increase_probationary_{month_index}", 0)
                    merged_profile[f'increase_official_{month_index}'] = 0 if not filtered_cl else filtered_cl[-1].get(f"increase_official_{month_index}", 0)
                    merged_profile[f'used_probationary_{month_index}'] = 0 if not filtered_cl else filtered_cl[-1].get(f"used_probationary_{month_index}", 0)
                    merged_profile[f'used_official_{month_index}'] = 0 if not filtered_cl else filtered_cl[-1].get(f"used_official_{month_index}", 0)
                    merged_profile[f'overtime_probationary_{month_index}'] = 0 if not filtered_cl else filtered_cl[-1].get(f"overtime_probationary_{month_index}", 0)
                    merged_profile[f'overtime_official_{month_index}'] = 0 if not filtered_cl else filtered_cl[-1].get(f"overtime_official_{month_index}", 0)
                merged_profiles.append(merged_profile)

        return render(request, 'hrms/cl_tables.html', {"profiles": merged_profiles})


class Employees(View):
    def get(self, request):
        page_number = int(request.GET.get('page_number', 1))
        page_size = int(request.GET.get('page_size', 20))  # Default 20 items per page
        offset = (page_number - 1) * page_size

        odoo_xmlrpc = OdooXMLRPC()
        employees = odoo_xmlrpc.get_employees(offset=offset, limit=page_size)

        # Get total record count
        total_records = odoo_xmlrpc.get_total_records()

        paginator = Paginator(employees, page_size)
        page_obj = paginator.get_page(page_number)

        context = {
            "page_obj": page_obj,
            "total_records": total_records,
            "page_size": page_size,
            "page_number": page_number
        }

        return render(request, "hrms/employees.html", context)
