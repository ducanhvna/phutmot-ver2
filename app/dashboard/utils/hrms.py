from hrms.utils.hrleave import LeaveService
# from collections import defaultdict
from hrms.models import Leave
import xmlrpc.client
from dashboard.models import Hrms
from datetime import datetime, timedelta
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


class HrmsDashboard():
    def update(self, first_day_of_month=None):
        # Get the first day of the current month
        max_write_date_leave = None
        if not first_day_of_month:
            first_day_of_month = datetime.now().replace(day=1)
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
        new_write_date = leave.download(max_write_date_leave)
        hrms_dashboard.info["max_write_date_leave"] = (
            new_write_date.strftime("%Y-%m-%d %H:%M:%S") if new_write_date else None
        )
        today_leaves, latest_leaves = self.get_today_task()
        hrms_dashboard.info['today_leaves'] = today_leaves
        hrms_dashboard.info['latest_leaves'] = latest_leaves
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

    def get_today_task(self):
        first_day_of_month = datetime.now().replace(day=1)
        # last_day_of_last_month = first_day_of_month - timedelta(days=1)
        list_leaves = Leave.objects.filter(
            start_date=first_day_of_month.date()
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
