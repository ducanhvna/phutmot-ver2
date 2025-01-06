from django.core.management.base import BaseCommand
from fleet.utils.trip import Trip
from datetime import datetime


class Command(BaseCommand):
    help = 'Download Leave data from Odoo and import into Django'

    def handle(self, *args, **kwargs):
        # Get the first day of the current month
        first_day_of_month = datetime.now().replace(day=1)
        trip = Trip(first_day_of_month)
        trip.download()
