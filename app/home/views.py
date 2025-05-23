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
from hrms.serializers import EmployeeWithSchedulingSerializer
from django.db.models import Q, Func, F
from unidecode import unidecode
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User, Group
from .utils.odoo_client import OdooClient
from rest_framework.permissions import AllowAny
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .models import TelegramUser
import xmlrpc.client
from collections import defaultdict
from rest_framework.pagination import PageNumberPagination

ERP_URL = "http://odoo17:8069"
ERP_DB = "odoo"
# ERP_USERNAME = "admin"
# ERP_PASSWORD = "admin"


@csrf_exempt
def handle_telegram_user(request):
    if request.method == "POST":
        try:
            # Lấy data từ client
            data = json.loads(request.body)
            username = data.get("username")
            password = data.get("password")
            telegram_data = data.get("telegram")
            url = ERP_URL
            db = ERP_DB
            common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
            uid = common.authenticate(db, username, password, {})
            if uid:
                # Kiểm tra thông tin username và password
                user = User.objects.filter(username=username).first()
                # If the user doesn't exist, create a new one
                if not user:
                    user = User.objects.create_user(
                        username=username,
                        password=password,
                        first_name=telegram_data.get("first_name"),
                        last_name=telegram_data.get("last_name")
                    )
                else:
                    if not user.check_password(password):
                        user.password = make_password(password)
                        user.save()
                # Kiểm tra nếu thông tin Telegram đã tồn tại
                telegram_user, created = TelegramUser.objects.get_or_create(
                    user=user,
                    telegram_id=telegram_data.get("id"),
                )

                # Cập nhật thông tin Telegram
                telegram_user.telegram_username = telegram_data.get("username")
                telegram_user.first_name = telegram_data.get("first_name")
                telegram_user.last_name = telegram_data.get("last_name")
                telegram_user.language_code = telegram_data.get("language_code")
                telegram_user.save()

                # apecBaocaotuanToken
                token = '7277612281:AAG3o_utZTPPdi_G30xlsJ1KINR9CD1FZgU'
                url = f"https://api.telegram.org/bot{token}/sendMessage"
                payload = {
                    'chat_id': telegram_user.telegram_id,
                    'text': "Chào mừng bạn đến với Báo cáo tuần bot",
                }
                requests.post(url, json=payload)

                return JsonResponse({"message": "Thông tin Telegram đã được lưu!", "created": created})
            else:
                return JsonResponse({"error": "Sai thông tin username hoặc password."}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "Chỉ chấp nhận phương thức POST."}, status=405)


@method_decorator(csrf_exempt, name='dispatch')
class UserProfileAPIView(generics.ListAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = (AllowAny,)

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
        "employee_code": employee_code,
        "listitem_trans": []
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
                merge_couples_before_private = record.get('merge_couples_before_private', [])
                if len(merge_couples_before_private) == 5:
                    context['merge_couples_before_private0'] = merge_couples_before_private[0]
                    context['merge_couples_before_private1'] = merge_couples_before_private[1]
                    context['merge_couples_before_private2'] = merge_couples_before_private[2]
                    context['merge_couples_before_private3'] = merge_couples_before_private[3]
                    context['merge_couples_before_private4'] = merge_couples_before_private[4]
                else:
                    context['merge_couples_before_private0'] = []
                    context['merge_couples_before_private1'] = []
                    context['merge_couples_before_private2'] = []
                    context['merge_couples_before_private3'] = []
                    context['merge_couples_before_private4'] = []
                couple_index = 0
                for couple in context['merge_couples_before_private1']:
                    couple['description'] = 'làm việc'
                    if couple_index == 0 and couple.get('typeio', '') == 'IO':
                        couple['description'] = 'đi muộn'
                    couple_index = couple_index + 1
                for couple in context['merge_couples_before_private3']:
                    couple['description'] = 'làm việc'
                    if (couple_index == (len(context['merge_couples_before_private3']) - 1)) and couple.get('typeio', '') == 'IO':
                        couple['description'] = 'Về sớm'
                    couple_index = couple_index + 1
                listitem_trans = record.get('listitemTrans', [])
                for tran in listitem_trans:
                    try:
                        tran['hour'] = tran['time'].split(' ')[1]
                    except Exception as ex:
                        print(ex)
                context['listitem_trans'] = listitem_trans
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


@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    authentication_classes = []  # Bỏ qua xác thực cho endpoint này
    permission_classes = (AllowAny,)

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        if not username or not password:
            return Response({'status': 'fail', 'message': 'Username and password required'}, status=400)

        # Tạo instance của OdooClient
        odoo_client = OdooClient(base_url='https://hrm.mandalahotel.com.vn', db='apechrm_product_v3')
        odoo_response = odoo_client.authenticate(username, password)

        if odoo_response['status'] == 'success':
            # Tạo hoặc lấy người dùng trong Django
            user, created = User.objects.get_or_create(username=username)
            if created:
                user.set_password(password)
                user.email = odoo_response.get('email', '')  # Giả định Odoo trả về email
                user.save()

            # Gán nhóm (roles) dựa trên thông tin từ Odoo
            role_name = odoo_response.get('role', 'user')  # Giả định Odoo có thông tin role
            group, _ = Group.objects.get_or_create(name=role_name)
            user.groups.add(group)

            # Tạo token JWT cho người dùng
            refresh = RefreshToken.for_user(user)

            return Response({
                'status': 'success',
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
                'user': {
                    'name': user.get_full_name() or username,
                    'email': user.email,
                    'roles': [group.name for group in user.groups.all()],  # Trả về danh sách roles
                    'avatar': f"https://i.pravatar.cc/150?img={user.id % 70}"  # Giả lập avatar
                }
            })
        else:
            return Response({'status': 'fail', 'message': odoo_response.get('message', 'Invalid credentials')}, status=400)


def split_data_by_week(data, month, year):
    weeks = defaultdict(lambda: defaultdict(list))
    for entry in data:
        try:
            entry_date = datetime.strptime(entry["date"], "%Y-%m-%d")
            entry['month'] = entry_date.month
            entry['year'] = entry_date.year
            entry['day'] = entry_date.day
            if (entry_date.month == month) and (entry_date.year == year):
                week_number = entry_date.isocalendar()[1]  # Lấy số tuần trong năm
            if not (f"{week_number}" in weeks):
                weeks[f"{week_number}"] = [entry]
            else:
                weeks[f"{week_number}"].append(entry)
        except ValueError:
            print(f"Lỗi: Định dạng ngày tháng không hợp lệ ({entry['date']})")

    return dict(weeks)


def personal_timesheet(request):
    # Lấy tham số từ query string
    code = request.GET.get('code', 'APG230321013')
    month = request.GET.get('month', None)
    year = request.GET.get('year', None)

    # if not code:
    #     return HttpResponse("Code is required", status=400)
    # Lấy tháng và năm hiện tại nếu không được cung cấp
    if not month:
        month = datetime.now().month
    else:
        month = int(month)
    if not year:
        year = datetime.now().year
    else:
        year = int(year)
    # last_month = datetime(year=year, month=month, day=1) - timedelta(days=1)
    # attendance = Attendance.objects.get(code=f'{2630}', start_date__month=last_month.month, start_date__year=last_month.year)
    # start_date = attendance.start_date + timedelta(days=1)
    employees = Employee.objects.filter(employee_code=code)

    html_template = loader.get_template("home/tables.html")
    data = []
    for emplyee in employees:
        start_date = emplyee.start_date
        split_data = defaultdict(lambda: defaultdict(list))
        try:
            scheduling = Scheduling.objects.get(
                employee_code=code,
                start_date__month=start_date.month,
                start_date__year=start_date.year,
            )
            split_data = split_data_by_week(
                scheduling.scheduling_records, start_date.month, start_date.year
            )
        except Exception:
            scheduling = None

        # for week, entries in result.items():
        item = {
            "name": emplyee.info.get("name", "-"),
            "code": emplyee.employee_code,
            "job_title": emplyee.info.get("job_title", "-"),
            "month": start_date.month,
            "year": start_date.year,
            "timesheet": [
                {
                    "month": start_date.month,
                    "week": week,
                    "data": [
                        {
                            "date": 0,
                            "shift_name": entry.get("shift_name", "-"),
                            "id": entry.get("id", ""),
                            "day": entry.get("day", ""),
                        }
                        for entry in entries
                    ],
                }
                for week, entries in split_data.items()
            ],
        }
        data.append(item)

    context = {"data": data}
    return HttpResponse(html_template.render(context, request))


class EmployeeWithSchedulingListAPIView(APIView):
    def get(self, request):
        # Lấy các tham số filter
        name = request.GET.get('name')
        employee_code = request.GET.get('employee_code')
        time_keeping_code = request.GET.get('time_keeping_code')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        queryset = Employee.objects.all()
        # Tìm kiếm theo tên (trong info['name'] hoặc info['full_name'])
        if name:
            name_unaccented = unidecode(name).lower()
            search_conditions = Q(info__name__icontains=name) | \
                Q(info__full_name__icontains=name) | \
                Q(info_unaccented__name__icontains=name_unaccented) | \
                Q(info_unaccented__full_name__icontains=name_unaccented)
            queryset = queryset.filter(search_conditions)

        if employee_code:
            queryset = queryset.filter(code__icontains=employee_code)
        if time_keeping_code:
            queryset = queryset.filter(time_keeping_code__icontains=time_keeping_code)
        if start_date:
            queryset = queryset.filter(start_date=start_date)
        if end_date:
            queryset = queryset.filter(end_date=end_date)

        # Phân trang
        paginator = PageNumberPagination()
        paginator.page_size = int(request.GET.get('page_size', 20))
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = EmployeeWithSchedulingSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
