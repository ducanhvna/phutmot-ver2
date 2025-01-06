from fleet.models import Vehicle
from collections import defaultdict
import xmlrpc.client
from datetime import datetime, timedelta


class Trip():
    def __init__(self, first_day_of_month=None):
        # Define your Odoo connection parameters
        if not first_day_of_month:
            first_day_of_month = datetime.now().replace(day=1)
        self.first_day_of_month = first_day_of_month

        # Lấy ngày đầu tiên của tháng trước
        self.first_day_of_last_month = self.first_day_of_month - timedelta(days=1)
        self.first_day_of_last_month = datetime(self.first_day_of_last_month.year, self.first_day_of_last_month.month, 1)
        # Calculate the last day of the current month
        if self.first_day_of_month.month == 12:
            next_month = self.first_day_of_month.replace(year=self.first_day_of_month.year + 1, month=1, day=1)
        else:
            next_month = self.first_day_of_month.replace(month=self.first_day_of_month.month + 1, day=1)

        self.last_day_of_month = next_month - timedelta(days=1)
        self.url = 'https://vantaihahai.com'
        self.db = 'fleet'
        self.username = 'admin'
        self.password = 'admin'
        common = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/common')
        self.uid = common.authenticate(self.db, self.username, self.password, {})
        self.models = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object')
        super(Trip, self).__init__()

    def download(self, max_write_date_trip=None):
        self.max_write_date_trip = max_write_date_trip
        # Format the dates
        start_str = (self.first_day_of_month - timedelta(days=1)).strftime('%Y-%m-%d')
        end_str = (self.last_day_of_month + timedelta(days=1)).strftime('%Y-%m-%d')

        print(f"Start date: {start_str}")
        print(f"End date: {end_str}")

        fields = ['id', 'equipment_id', 'schedule_date', 'location_id', 'location_dest_id', 'write_date']
        merged_data = self.download_data('fleet.trip', fields, start_str, end_str)
        grouped_data = defaultdict(list)
        for record in merged_data:
            grouped_data[record["equipment_id"][1]].append(record)
            print(f"{record['equipment_id'][1]} -- {len(grouped_data[record['equipment_id'][0]])}")

        # Save data to Django
        self.save_to_django(grouped_data, start_str, end_str)
        # Extract write_date values
        write_dates = [
            datetime.strptime(record["write_date"], "%Y-%m-%d %H:%M:%S")
            for record in merged_data
            if record.get("write_date")
        ]

        # Get the maximum write_date or None if the list is empty
        max_write_date = max(write_dates, default=None)

        # Now max_write_date contains the maximum write_date or None if there are no dates
        print(f"Maximum write_date: {max_write_date}")

        return max_write_date

    def save_to_django(self, grouped_data, start_date, end_date):
        for license_place, records in grouped_data.items():
            vehicle, created = Vehicle.objects.get_or_create(
                license_place=license_place,
                start_date=datetime.strptime(start_date, "%Y-%m-%d"),
                end_date=datetime.strptime(end_date, "%Y-%m-%d"),
            )
            if 'trips' not in vehicle.other_profile:
                vehicle.other_profile['trips'] = []

            existing_trips = vehicle.other_profile['trips']
            updated_trips = []

            # Update existing trips or add new ones
            for record in records:
                found = False
                for index, trip in enumerate(existing_trips):
                    if trip['id'] == record['id']:
                        existing_trips[index] = record  # Replace the old trip
                        found = True
                        break
                if not found:
                    updated_trips.append(record)  # Add new trip if not found

            # Extend with new trips
            vehicle.other_profile['trips'].extend(updated_trips)
            vehicle.save()

    def download_data(self, model_name, fields, start_str, end_str):
        LIMIT_SIZE = 300
        index = 0
        len_data = 0
        merged_array = []
        if model_name == 'fleet.trip':
            domain = [[
                ("schedule_date", ">=", start_str),
                ("schedule_date", "<=", end_str),
                ("schedule_date", "!=", False),
                ("equipment_id", "!=", False)
            ]]
            if self.max_write_date_trip:
                domain.append((("write_date", ">", self.max_write_date_trip.strftime("%Y-%m-%d %H:%M:%S"))))
        else:
            raise ValueError("Invalid model name")

        while (len_data == LIMIT_SIZE) or (index == 0):
            ids = self.models.execute_kw(
                self.db,
                self.uid,
                self.password,
                model_name,
                'search',
                domain,
                {'offset': index * LIMIT_SIZE, 'limit': LIMIT_SIZE},
            )
            len_data = len(ids)
            print(ids)
            merged_array = list(set(merged_array) | set(ids))
            index += 1

        # Split ids into chunks of 200
        ids_chunks = [merged_array[i:i + 200] for i in range(0, len(merged_array), 200)]
        print(ids_chunks)
        merged_data = []

        for ids_chunk in ids_chunks:
            # Fetch data from Odoo
            data_chunk = self.models.execute_kw(
                self.db,
                self.uid,
                self.password,
                model_name,
                'read',
                [ids_chunk],
                {'fields': fields},
            )
            merged_data.extend(data_chunk)

        return merged_data
