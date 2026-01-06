from django.urls import path
from .views import jwks_view

urlpatterns = [
    path("jwks.json", jwks_view, name="jwks"),
]
