from django.urls import path
from .views import (
    DeviceLoginView,
    FetchRoomChatsView,
    FetchUserChatsView,
    ProductCategoryAPIView,
    PriceAPIView,
)


app_name = "devices"


urlpatterns = [
    path('device-login/', DeviceLoginView.as_view(), name='device_login'),
    path('fetchRoomChats/', FetchRoomChatsView.as_view(), name='fetch_room_chats'),
    path('fetchUserChats/', FetchUserChatsView.as_view(), name='fetch_user_chats'),
    path('fetchProductPods/', ProductCategoryAPIView.as_view(), name='fetch_pod_products'),
    path('fetchProductPrice/', PriceAPIView.as_view(), name='fetch_price_products')
]
