from django.urls import path
from .views import fetch_setting


app_name = "bot_manager"


urlpatterns = [
    path("fetchSetting/", fetch_setting, name="fetch_setting"),
]
