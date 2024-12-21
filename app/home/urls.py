from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    re_path(r'^.*\.*', views.pages, name='pages'),
]
