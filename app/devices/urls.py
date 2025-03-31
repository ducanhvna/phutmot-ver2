from django.urls import path
from .views import DeviceLoginView, FetchRoomChatsView


app_name = "devices"


urlpatterns = [
    path('device-login/', DeviceLoginView.as_view(), name='device_login'),
    path('fetchRoomChats/', FetchRoomChatsView.as_view(), name='fetch_room_chats')
]
