from django.urls import path
from .views import FetchSettingView, AddUserView


app_name = "bot_manager"


urlpatterns = [
    path('fetchSetting/', FetchSettingView.as_view(), name='fetch_setting'),
    path('addUser', AddUserView.as_view(), name='add_user'),
]
