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
                merged_profiles.append(merged_profile)

        return render(request, "hrms/al_tables.html", {"profiles": filtered_profiles})


class ClTablesView(View):
    def get(self, request):
        start_datetime = datetime(2024, 12, 1, 0, 0, 0)  # December 1, 2024 at 00:00:00
        filtered_profiles = Employee.objects.filter(
            Q(info__company_id__0=18), start_date=start_datetime
        )
        return render(request, 'hrms/cl_tables.html', {"profiles": filtered_profiles})
