from django.urls import path
from .views import upload_document, document_detail, oauth2callback, authorize

urlpatterns = [
    path('', oauth2callback, name='oauth2callback'),
    path('/upload/', upload_document, name='upload_document'),
    path('/<int:id>/', document_detail, name='document_detail'),
    path('/authorize/', authorize, name='authorize'),
]
