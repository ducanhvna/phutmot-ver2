from django.urls import path
from .views import (
	CustomerSearchView
)
urlpatterns = [
	path("search/", CustomerSearchView.as_view(), name="customer_search"),
]