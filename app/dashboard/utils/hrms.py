from hrms.utils.employee import EmployeeService
from hrms.utils.hrleave import LeaveService
from hrms.utils.trans import AttendanceTransService
from hrms.utils.attendance_report_service import AttendanceReportService
from hrms.utils.explaination import ExplainationService
# from collections import defaultdict
from hrms.models import Leave
from home.utils.shift_service import ApecShiftService
import xmlrpc.client
from dashboard.models import Hrms
from datetime import datetime, timedelta
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


class HrmsDashboard():
    def __init__(self, company_merged_data=None):
        self.company_merged_data = company_merged_data
        super(HrmsDashboard, self).__init__()

    def download_base(self):
        comany_shift_service = ApecShiftService()
        comany_shift_service.download_copanies()
        print("download company, shift, al, cl")

    def update(self, first_day_of_month=None):
        # Get the first day of the current month
        max_write_date_leave = None
        max_write_date_trans = None
        max_write_date_reports = None
        max_write_date_explainations = None
        max_write_date_employees = None

        if not first_day_of_month:
            first_day_of_month = datetime.now().replace(day=1)
        self.first_day_of_month = first_day_of_month
        self.download_base()
        leave = LeaveService(first_day_of_month)
        hrms_dashboard, created = Hrms.objects.get_or_create(
            company_code="APEC",
            start_date=first_day_of_month,
            end_date=leave.last_day_of_month,
            defaults={"info": {}},
        )
        info = hrms_dashboard.info
        if info and (info != {}):
            max_write_date_leave = info["max_write_date_leave"]
            max_write_date_trans = info.get("max_write_date_trans", None)
            max_write_date_reports = info.get('max_write_date_reports', None)
            max_write_date_explainations = info.get('max_write_date_explainations', None)
            max_write_date_employees = info.get('max_write_date_employees', None)
        new_write_date = leave.download(max_write_date_leave)
        hrms_dashboard.info["max_write_date_leave"] = (
            new_write_date.strftime("%Y-%m-%d %H:%M:%S") if new_write_date else None
        )
        today_leaves, latest_leaves = self.get_today_task()
        hrms_dashboard.info['today_leaves'] = today_leaves
        hrms_dashboard.info['latest_leaves'] = latest_leaves
        # Employee
        employee_service = EmployeeService(first_day_of_month)
        new_write_date = employee_service.download(max_write_date_employees)
        hrms_dashboard.info["max_write_date_employees"] = (
            new_write_date.strftime("%Y-%m-%d %H:%M:%S") if new_write_date else None
        )

        # AttendanceTransService
        attendance_trans = AttendanceTransService(first_day_of_month)
        new_write_date = attendance_trans.download(max_write_date_trans)
        hrms_dashboard.info["max_write_date_trans"] = (
            new_write_date.strftime("%Y-%m-%d %H:%M:%S") if new_write_date else None
        )

        # AttendanceReportService
        attendance_reports = AttendanceReportService(first_day_of_month)
        new_write_date = attendance_reports.download(max_write_date_reports)
        hrms_dashboard.info["max_write_date_reports"] = (
            new_write_date.strftime("%Y-%m-%d %H:%M:%S") if new_write_date else None
        )
        # ExplainationService
        explaination = ExplainationService(first_day_of_month, self.company_merged_data)
        new_write_date = explaination.download(max_write_date_explainations)
        hrms_dashboard.info["max_write_date_explainations"] = (
            new_write_date.strftime("%Y-%m-%d %H:%M:%S") if new_write_date else None
        )

        hrms_dashboard.save()
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "broadcast",
            {
                "type": "chat_message",
                "message": "This is a broadcast message",
                "latest_leaves": [],
            },
        )
        if not self.company_merged_data:
            self.company_merged_data = explaination.company_merged_data

    def get_today_task(self):
        # first_day_of_month = datetime.now().replace(day=1)
        # last_day_of_last_month = first_day_of_month - timedelta(days=1)
        list_leaves = Leave.objects.filter(
            start_date=self.first_day_of_month.date()
        )
        today_leave = []
        latest_leave = []
        for leave in list_leaves:
            # print(vehicle)
            leave_records = leave.leave_records
            # today_leave.extend(leaves)
            max_leave = max(leave_records, key=lambda x: x['id']) if leave_records else None
            if max_leave:
                latest_leave.append(max_leave)
        return today_leave, latest_leave
