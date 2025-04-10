from django.urls import path
from .views import (
    DeviceLoginView,
    FetchRoomChatsView,
    FetchUserChatsView,
    ProductCategoryAPIView,
    PriceAPIView,
    fetchRoomDetailView,
    AiDataSupportView
)


app_name = "devices"


urlpatterns = [
    path('device-login/', DeviceLoginView.as_view(), name='device_login'),
    path('fetchRoomChats/', FetchRoomChatsView.as_view(), name='fetch_room_chats'),
    path('fetchUserChats/', FetchUserChatsView.as_view(), name='fetch_user_chats'),
    path('fetchProductPods/', ProductCategoryAPIView.as_view(), name='fetch_pod_products'),
    path('fetchProductPrice/', PriceAPIView.as_view(), name='fetch_price_products'),
    path('fetchRoomDetail/', fetchRoomDetailView.as_view(), name='fetch_room_detail'),
    path('fetchAiDataSupport/', AiDataSupportView.as_view(), name='fetch_ai_data_support'),
    path('fetchMyOwnRooms/', FetchRoomChatsView.as_view(), name='fetch_my_own_room_chats')
]
