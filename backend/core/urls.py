# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib import admin
from django.urls import path, include  # add this

urlpatterns = [
    path('admin/', admin.site.urls),          # Django admin route
    path('accounts/', include('allauth.urls')),
    path('api/customers/', include('apps.customers.urls')),
    path('api/users/', include('apps.users.urls')),
    path("", include("apps.authentication.urls")), # Auth routes - login / register
    path("", include(("apps.producttemplates.urls", "product"), namespace="product")),
    path("", include("apps.home.urls")),             # UI Kits Html files
    

]
