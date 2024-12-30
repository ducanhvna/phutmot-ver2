from django import template
from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from hrms.models import Attendance, Scheduling, Employee, Shifts, Leave
from datetime import datetime, timedelta
import json
import calendar
from django.http import JsonResponse


def get_calendar_data():
    today = datetime.today()
    current_year = today.year
    current_month = today.month
    _, num_days_in_month = calendar.monthrange(current_year, current_month)  # Lấy số ngày trong tháng hiện tại

    calendar_data = []
    start_date = datetime(current_year, current_month, 1)
    start_day_of_week = start_date.weekday()

    for i in range(num_days_in_month):  # Tạo dữ liệu cho số ngày trong tháng
        day = datetime(current_year, current_month, i + 1)
        # Tính toán hàng dựa trên số tuần
        row_start = (i + start_day_of_week) // 7 + 1
        day_of_week = day.weekday() % 7  # Chuyển đổi để chủ nhật là 6

        calendar_data.append({
            'date': day.strftime("%d"),  # Chỉ hiển thị ngày của tháng
            'day_of_week': day_of_week + 1,  # 1: Thứ 2, ..., 7: Chủ nhật
            'order_count': i % 5,  # Số lượng đơn mẫu
            'work_hours': f"{8 + i % 3}h",  # Thời gian làm việc mẫu
            'salary': f"${100 + i * 10}",  # Công tính lương mẫu
            'row_start': row_start  # Thêm ngày trong tháng để sử dụng làm hàng
        })
    return calendar_data


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
        # Lấy tham số từ query string
        code = request.GET.get('code', None)
        month = request.GET.get('month', None)
        year = request.GET.get('year', None)

        if not code:
            return HttpResponse("Code is required", status=400)

        # Lấy tháng và năm hiện tại nếu không được cung cấp
        if not month:
            month = datetime.now().month
        else:
            month = int(month)
        if not year:
            year = datetime.now().year
        else:
            year = int(year)
        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template
        # first_day_of_month = datetime.now().replace(day=1)
        # Lấy đối tượng Attendance
        attendance = Attendance.objects.get(code=f'{2630}', start_date__month=(month-1 if month>1 else 12), start_date__year=(year if month>1 else year-1))
        start_date = attendance.start_date + timedelta(days=1)
        employee = Employee.objects.get(time_keeping_code=attendance.code, start_date=start_date)
        shifts = Shifts.objects.filter(company_code='IDJ')
        scheduling = Scheduling.objects.get(employee_code=employee.employee_code, start_date=start_date)
        leave = Leave.objects.get(employee_code=employee.employee_code, start_date=start_date)
        scheduling_records = [
            {
                'date': record['date'],
                'employee_name': record['employee_name'],
                'employee_code': record['employee_code'],
                'shift_name': record['shift_name']
            }
            for record in scheduling.scheduling_records
        ]
        leave_records = [
            {
                'request_date_from': record['request_date_from'],
                'request_date_to': record['request_date_to'],
                'holiday_status_id': record['holiday_status_id'][1] if record['holiday_status_id'] else '-',
                'employee_code': record['employee_code'],
                'reasons': record['reasons'],
                'minutes': record['minutes']
            }
            for record in leave.leave_records
        ]
        calendar_data = get_calendar_data()
        # Sau đó bạn có thể đưa scheduling_records vào context
        context['schedulingrecords'] = scheduling_records
        context['calendar_data'] = calendar_data
        context['attendance'] = attendance
        context['employee'] = employee
        context['scheduling'] = scheduling
        # context['schedulingrecords'] = json.loads(scheduling.scheduling_records)
        context['shifts'] = shifts
        context['leave'] = leave
        context['leaverecords'] = leave_records

        html_template = loader.get_template('home/timesheet.html')
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except Exception:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))


def get_details(request):
    date = request.GET.get('date')
    # Thay thế bằng logic để lấy dữ liệu thực tế của bạn
    data = {
        'date': date,
        'order_count': 5,
        'work_hours': "8h",
        'salary': "$100"
    }
    return JsonResponse(data)
