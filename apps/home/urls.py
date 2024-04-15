# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, include , re_path
from apps.home import views
from .views import post_generator, CreateDevice, CompanyViewSet
urlpatterns = [

    # The home page
    path('', views.index, name='home'),
    path('async', post_generator),
    # Matches any html file
    path('apiv2/create_device', CreateDevice.as_view(), name='api_create_device'),
    path("api/versions/", CompanyViewSet.as_view(), name='versions'),
    path("apiv2/apec/", include("apps.apec.urls")),
    path("apiv2/vantaihahai/", include("apps.apec.urls")),
    
    re_path(r'^.*\.*', views.pages, name='pages'),
]
