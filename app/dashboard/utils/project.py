from hrms.utils.employee import EmployeeService
from hrms.utils.hrleave import LeaveService
from hrms.utils.trans import AttendanceTransService
from hrms.utils.attendance_report_service import AttendanceReportService
from hrms.utils.explaination import ExplainationService
# from collections import defaultdict
from hrms.models import Leave
from home.utils.shift_service import ApecShiftService
from projects.utils.project_service import ProjectService
import xmlrpc.client
from dashboard.models import Hrms, Projecttask
from datetime import datetime, timedelta
# from asgiref.sync import async_to_sync
# from channels.layers import get_channel_layer


class ProjectDashboard():
    def __init__(self, company_merged_data=None):
        self.company_merged_data = company_merged_data
        super(ProjectDashboard, self).__init__()

    def update(self, first_day_of_month=None):
        # Get the first day of the current month
        max_write_date_project = None

        if not first_day_of_month:
            first_day_of_month = datetime.now().replace(day=1)
        self.first_day_of_month = first_day_of_month
        # self.download_base()
        leave = LeaveService(first_day_of_month)

        projecttask_dashboard, created = Projecttask.objects.get_or_create(
            company_code="BHL",
            start_date=first_day_of_month,
            end_date=leave.last_day_of_month,
            defaults={"info": {}},
        )

        info = projecttask_dashboard.info
        if info and (info != {}):
            max_write_date_project = info.get('max_write_date_project', None)

        project_service = ProjectService(first_day_of_month)
        new_write_date_project = project_service.download(max_write_date_project)
        projecttask_dashboard.info["max_write_date_projects"] = (
            new_write_date_project.strftime("%Y-%m-%d %H:%M:%S") if new_write_date_project else None
        )
        projecttask_dashboard.save()
