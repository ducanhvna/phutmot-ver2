# hrms/tasks.py

import logging
from celery import shared_task
from fleet.utils.trip import FleetDashboard
from dashboard.utils.hrms import HrmsDashboard
from dashboard.utils.project import ProjectDashboard
from datetime import datetime, timedelta
# from datetime import timedelta

logger = logging.getLogger(__name__)


@shared_task
def check_apec_hrms_update():
    logger.info("Create attendance check apecinput")
    print("Tác vụ chạy định kỳ mỗi 30 giây check_apec_hrms_update")
    fleet_dashboard = FleetDashboard()
    fleet_dashboard.update()
    # Thực hiện công việc của bạn tại đây


@shared_task
def update_apec_hrm():
    logger.info("Create update_apec_hrm check update_apec_hrm")
    print("Tác vụ chạy định kỳ mỗi 480 giây update_apec_hrm")
    hrms_dashboard = HrmsDashboard()
    hrms_dashboard.update()
    first_day_of_month = datetime.now().replace(day=1)
    last_day_of_last_month = first_day_of_month - timedelta(days=1)
    first_day_of_last_month = last_day_of_last_month.replace(day=1)
    hrms_dashboard.update(first_day_of_last_month)


@shared_task
def update_bhl_project():
    logger.info("Create project check project")
    print("Tác vụ chạy định kỳ mỗi 360 giây project")
    project_dashboard = ProjectDashboard()
    project_dashboard.update()
    first_day_of_month = datetime.now().replace(day=1)
    last_day_of_last_month = first_day_of_month - timedelta(days=1)
    first_day_of_last_month = last_day_of_last_month.replace(day=1)
    project_dashboard.update(first_day_of_last_month)
