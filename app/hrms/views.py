from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Q
from home.models import UserProfile
import xmlrpc.client
import json
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
        filtered_profiles = UserProfile.objects.filter(Q(info__company_id__0=18))
        return render(request, "hrms/al_tables.html", {"profiles": filtered_profiles})


class ClTablesView(View):
    def get(self, request):
        filtered_profiles = UserProfile.objects.filter(Q(info__company_id__0=18))
        return render(request, 'hrms/cl_tables.html', {"profiles": filtered_profiles})
