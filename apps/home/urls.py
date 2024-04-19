# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, include , re_path
from apps.home import views
from .views import post_generator, CreateDevice, CompanyViewSet
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
urlpatterns = [

    # The home page
    path('', views.index, name='home'),
    path('async', post_generator),
    # Matches any html file
    path('apiv2/create_device', CreateDevice.as_view(), name='api_create_device'),
    path("api/versions/", CompanyViewSet.as_view(), name='versions'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("apiv2/apec/", include("apps.apec.urls")),
    path("apiv2/vantaihahai/", include("apps.vantaihahai.urls")),
    
    re_path(r'^.*\.*', views.pages, name='pages'),
]
