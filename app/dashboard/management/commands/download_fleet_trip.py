from django.core.management.base import BaseCommand
from fleet.utils.trip import Trip
from dashboard.models import Fleet
from datetime import datetime


class Command(BaseCommand):
    help = "Download Fleet Trip data from Odoo and import into Django"

    def handle(self, *args, **kwargs):
        # Get the first day of the current month
        max_write_date_trip = None
        first_day_of_month = datetime.now().replace(day=1)
        trip = Trip(first_day_of_month)
        fleet_dashboard = Fleet.objects.get_or_create(
            company_code="VANTAIHAHAI",
            start_date=first_day_of_month,
            end_date=trip.last_day_of_month,
            defaults={"info": {}},
        )
        info = fleet_dashboard.info
        if info and (info != {}):
            max_write_date_trip = ["max_write_date_trip"]
        new_write_date = trip.download(max_write_date_trip)
        fleet_dashboard.info["max_write_date_trip"] = (
            new_write_date.strftime("%Y-%m-%d %H:%M:%S") if new_write_date else None
        )
        fleet_dashboard.save()
