from django.urls import path
from .views import FetchSettingView


app_name = "bot_manager"


urlpatterns = [
    path('fetchSetting/', FetchSettingView.as_view(), name='fetch_setting'),
]
