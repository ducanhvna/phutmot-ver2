from django import template
from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from hrms.models import Attendance, Scheduling, Employee, Shifts, Leave
from datetime import timedelta
import json


def index(request):
    context = {'segment': 'index'}
    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))


def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template

        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except Exception:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))


def timesheet(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template
        # Lấy đối tượng Attendance
        attendance = Attendance.objects.get(code='2630')
        start_date = attendance.start_date + timedelta(days=1)
        employee = Employee.objects.get(time_keeping_code=attendance.code, start_date=start_date)
        shifts = Shifts.objects.filter(company_code='IDJ')
        scheduling = Scheduling.objects.get(employee_code=employee.employee_code, start_date=start_date)
        leave = Leave.objects.get(employee_code=employee.employee_code, start_date=start_date)
        scheduling_records = []
        for record in scheduling.scheduling_records:
            scheduling_records.append({
                'date': record['date'],
                'employee_name': record['employee_name'],
                'employee_code': record['employee_code'],
                'shift_name': record['shift_name']
            })

        # Sau đó bạn có thể đưa scheduling_records vào context
        context['schedulingrecords'] = scheduling_records

        context['attendance'] = attendance
        context['employee'] = employee
        context['scheduling'] = scheduling
        # context['schedulingrecords'] = json.loads(scheduling.scheduling_records)
        context['shifts'] = shifts
        context['leave'] = leave

        html_template = loader.get_template('home/timesheet.html')
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except Exception:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))
