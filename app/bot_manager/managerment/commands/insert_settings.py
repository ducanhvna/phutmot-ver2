from django.core.management.base import BaseCommand
from myapp.models import Setting
from datetime import datetime


class Command(BaseCommand):
    help = "Insert initial settings into the database"

    def handle(self, *args, **kwargs):
        settings_data = {
            "app_name": "Chatter.",
            "setRoomUsersLimit": 10,
            "minute_limit_in_creating_story": 1,
            "minute_limit_in_choosing_video_for_story": 1,
            "minute_limit_in_choosing_video_for_post": 1,
            "max_images_can_be_uploaded_in_one_post": 4,
            "ad_banner_android": "ca-app-pub-3940256099942544/6300978111",
            "ad_interstitial_android": "ca-app-pub-3940256099942544/1033173712",
            "ad_banner_iOS": "ca-app-pub-3940256099942544/2934735716",
            "ad_interstitial_iOS": "ca-app-pub-3940256099942544/4411468910",
            "is_admob_on": False,
            "created_at": datetime(2023, 3, 4, 9, 43, 26),
            "updated_at": datetime(2024, 4, 26, 3, 34, 25),
        }

        setting, created = Setting.objects.update_or_create(
            id=1, defaults=settings_data
        )

        if created:
            self.stdout.write(self.style.SUCCESS("Settings inserted successfully"))
        else:
            self.stdout.write(self.style.SUCCESS("Settings updated successfully"))
