from django import template
from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from .models import UserProfile
from hrms.models import Attendance, Scheduling, Employee, Shifts, Leave, Explaination, Timesheet
from dashboard.models import Hrms
from datetime import datetime, timedelta
import json
import calendar
from django.http import JsonResponse
from dashboard.models import Fleet
from rest_framework import generics
from .serializers import UserProfileSerializer
from django.db.models import Q, Func, F
from unidecode import unidecode


class UserProfileAPIView(generics.ListAPIView):
    serializer_class = UserProfileSerializer

    def get_queryset(self):
        queryset = UserProfile.objects.all()
        query = self.request.query_params.get('q')
        if query:
            query = unidecode(query).lower()
            search_conditions = Q(employee_code__icontains=query) | \
                Q(info_unaccented__name__icontains=query) | \
                Q(info_unaccented__code__icontains=query) | \
                Q(info_unaccented__time_keeping_code__icontains=query)
            queryset = queryset.filter(search_conditions)
        return queryset


def get_calendar_data(month=None, year=None):
    today = datetime.today()
    current_year = today.year if not year else year
    current_month = today.month if not month else month
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
    employee_code = request.GET.get('employeeCode')
    selected_date = request.GET.get('date')
    user_profile = None
    employee_info = None
    ts = None
    if employee_code and selected_date:
        try:
            # Chuyển đổi selected_date thành đối tượng datetime
            selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
            # Lấy thông tin profile từ model UserProfile
            user_profile = UserProfile.objects.get(employee_code=employee_code)
            employee_info = user_profile.info
            # time_keeping_code = employee_info['time_keeping_code']
            first_day_of_month = selected_date.replace(day=1)
            # apec_dashboard = Hrms.objects.get(company_code='APEC', start_date=first_day_of_month)
            ts = Timesheet.objects.get(employee_code=employee_code, start_date=first_day_of_month)
        except Exception as ex:
            print("index ex: ", ex)
            # Nếu không tìm thấy profile hoặc định dạng ngày không hợp lệ thì bỏ qua
            pass

    first_day_of_month = datetime.now().replace(day=1)
    fleet_dashboard = Fleet.objects.get(start_date=first_day_of_month.date())
    today_trips = []
    for item in fleet_dashboard.info['today_trips']:
        start_location = item['location_id'][1] if item['location_id'] else '<chưa xác định>'
        dest_location = item['location_dest_id'][1] if item['location_dest_id'] else '<chưa xác định>'
        today_trips.append(
            {
                "start_location": start_location,
                "dest_location": dest_location,
                "schedule_date": item["schedule_date"],
            }
        )

    latest_trips = []
    for item in fleet_dashboard.info['latest_trips']:
        equipment = item['equipment_id'][1] if item['equipment_id'] else '<chưa xác định>'
        start_location = item['location_id'][1] if item['location_id'] else '<chưa xác định>'
        dest_location = item['location_dest_id'][1] if item['location_dest_id'] else '<chưa xác định>'
        latest_trips.append(
            {
                "equipment": equipment,
                "start_location": start_location,
                "dest_location": dest_location,
                "write_date": item["write_date"],
            }
        )
    attributes = {
        'Kết cấu đất': '15 Acres',
        'Chất hữu cơ': '53 Acres',
        'Chỉ số đệm': '9 Acres',
        'Nitơ': '26',
        'Giá trị pH': '8.5',
        'Magiê 1': '3.7',
        'Sắt': '5.3',
        'Magiê 2': 'East',
        'Độ ẩm đất': '45%',
        'Hàm lượng kali': '5%',
        'Hàm lượng phospho': '4%',
        'Độ dẫn điện của đất': '1.2 mS/cm',
        'Độ thấm nước của đất': '3.5 in/hr',
        'Cấu trúc đất': 'Loamy',
        'Cation exchange capacity': '25 meq/100g',
        'Hàm lượng hữu cơ trong đất': '12%',
    }

    reminder_data = [
        {'name': 'Khoai tây', 'weight': '0.58 tấn', 'location': 'Ruộng 11-DA', 'harvest_date': '17/06/2023', 'state': 'thành công'},
        {'name': 'Cà chua', 'weight': '0.28 tấn', 'location': 'Ruộng 1-VQ', 'harvest_date': '16/06/2023', 'state': 'cảnh báo'},
        {'name': 'Cà tím', 'weight': '0.67 tấn', 'location': 'Ruộng 10-UV', 'harvest_date': '14/06/2023', 'state': 'đang chờ'},
        {'name': 'Khoai tây', 'weight': '0.88 tấn', 'location': 'Ruộng 9-DP', 'harvest_date': '13/06/2023', 'state': 'thành công'},
        {'name': 'Khoai tây', 'weight': '0.88 tấn', 'location': 'Ruộng 18-EA', 'harvest_date': '11/06/2023', 'state': 'đang chờ'}
    ]

    tasks_data = [
        {'task': 'Kiểm tra đất', 'plot': '17', 'area': '4.6 ha', 'date': '13/05/2023'},
        {'task': 'Trồng cây', 'plot': '22', 'area': '3.6 ha', 'date': '20/05/2023'},
        {'task': 'Thu hoạch', 'plot': '2', 'area': '2 ha', 'date': '23/05/2023'},
        {'task': 'Thu hoạch', 'plot': '9', 'area': '4.6 ha', 'date': '28/05/2023'}
    ]

    weather_data = [
        {'date': 'Hôm nay (08/08)', 'weather': 'Mưa', 'wind': 'Gió từ phía tây 3 mph', 'humidity': '76%'},
        {'date': 'Chủ nhật (09/08)', 'weather': 'Có mây một phần', 'wind': 'Gió từ phía tây nam 7 mph', 'humidity': '51%'},
        {'date': 'Thứ bảy (06/08)', 'weather': 'Trời quang', 'wind': 'Gió từ tây bắc 12 mph', 'humidity': '34%'}
    ]

    context = {
        "segment": "index",
        "today_trips": today_trips,
        "latest_trips": latest_trips,
        "attributes": attributes,
        "reminders": reminder_data,
        "tasks": tasks_data,
        "weather_data": weather_data,
        "employee_code": employee_code
    }
    if ts:
        timesheet_records = ts.timesheet_records
        for record in timesheet_records:
            date_string = record.get('date', None)
            parsed_date = None
            # Parse the date string to a datetime object
            try:
                parsed_date = datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S')
            except Exception as ex:
                print(ex)
            if parsed_date and (parsed_date.day == selected_date.day) and (parsed_date.month == selected_date.month):
                context['timesheet'] = record
    if employee_info:
        context['job_title'] = employee_info.get('job_title', '-')
        context['name'] = employee_info.get('name', '-')

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

    # except Exception:
    #     html_template = loader.get_template('home/page-500.html')
    #     return HttpResponse(html_template.render(context, request))


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
        last_month = datetime(year=year, month=month, day=1) - timedelta(days=1)
        attendance = Attendance.objects.get(code=f'{2630}', start_date__month=last_month.month, start_date__year=last_month.year)
        start_date = attendance.start_date + timedelta(days=1)
        employee = Employee.objects.get(time_keeping_code=attendance.code, start_date=start_date)
        shifts = Shifts.objects.filter(company_code='IDJ')
        scheduling = Scheduling.objects.get(employee_code=employee.employee_code, start_date=start_date)
        leave = Leave.objects.get(employee_code=employee.employee_code, start_date=start_date)
        explaination = Explaination.objects.get(employee_code=employee.employee_code, start_date=start_date)
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
        explaination_records = [
            {
                'attendance_missing_from': record['attendance_missing_from'],
                'attendance_missing_to': record['attendance_missing_to'],
                'employee_code': record['employee_code'],
                'invalid_type': record['invalid_type'],
                'reason': record['reason'],
                'remarks': record['remarks']
            }
            for record in explaination.explaination_records
        ]
        calendar_data = get_calendar_data(year=year, month=month)
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
        context['explainationrecords'] = explaination_records
        context['month'] = month
        context['year'] = year

        html_template = loader.get_template('home/timesheet.html')
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    # except Exception:
    #     html_template = loader.get_template('home/page-500.html')
    #     return HttpResponse(html_template.render(context, request))


def get_details(request):
    # date = request.GET.get('date')
    try:
        # Lấy đối tượng hrms_dashboard với tháng hiện tại
        # first_day_of_month = datetime.strptime(date, "%Y-%m-%d").replace(day=1)
        last_day_of_last_month = datetime.now().replace(day=1) - timedelta(days=1)
        first_day_of_month = last_day_of_last_month.replace(day=1)
        hrms_dashboard = Hrms.objects.get(company_code="APEC", start_date=first_day_of_month.date())

        # Truyền giá trị của grouped_total_worktime_by_company vào biến data
        data = {
            "total_worktime": hrms_dashboard.info.get('grouped_total_worktime_by_company', {}),
            "in_time": hrms_dashboard.info.get('grouped_total_number_in_time_company', {}),
            "late_early": hrms_dashboard.info.get('grouped_total_number_late_early_company', {}),
        }
    except Hrms.DoesNotExist:
        data = {}

    return JsonResponse(data)
