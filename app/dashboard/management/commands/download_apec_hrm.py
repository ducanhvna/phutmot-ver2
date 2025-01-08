# your_app/management/commands/download_and_import_data.py

from django.core.management.base import BaseCommand
from dashboard.utils.hrms import HrmsDashboard
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = "Download Leave Trip data from Odoo and import into Django"

    def handle(self, *args, **kwargs):
        # Get the first day of the current month
        hrms_dashboard = HrmsDashboard()
        hrms_dashboard.update()
        first_day_of_month = datetime.now().replace(day=1)
        last_day_of_last_month = first_day_of_month - timedelta(days=1)
        first_day_of_last_month = last_day_of_last_month.replace(day=1)
        hrms_dashboard.update(first_day_of_last_month)
