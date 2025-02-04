from django.urls import path
from .views import upload_document, document_detail

urlpatterns = [
    path('upload/', upload_document, name='upload_document'),
    path('<int:id>/', document_detail, name='document_detail'),
]
