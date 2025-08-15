from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('pos', views.pos, name='pos'),
    path('pos/list-product', views.pos_list_product, name='pos_list_product'),
]
