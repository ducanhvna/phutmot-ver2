from django.urls import path
from . import views

urlpatterns = [
    # ví dụ: endpoint login
    path("token/", views.LoginView.as_view(), name="get_token"),
]
