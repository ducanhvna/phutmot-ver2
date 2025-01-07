from django.core.management.base import BaseCommand
from fleet.utils.trip import FleetDashboard
from datetime import datetime


class Command(BaseCommand):
    help = "Download Fleet Trip data from Odoo and import into Django"

    def handle(self, *args, **kwargs):
        # Get the first day of the current month
        fleet_dashboard = FleetDashboard()
        fleet_dashboard.update()
