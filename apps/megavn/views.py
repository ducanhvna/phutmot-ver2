from django.shortcuts import render
from rest_framework.views import APIView
from .models import MegaEmployee
from rest_framework.response import Response

# Create your views here.
class GetListEmployee(APIView):
    def get(self, request, *args, **kwargs): 
        results = []
        for item in MegaEmployee.objects.all():
            results.append({'code': item.code, 
                        'group': item.group, 
                        'department' : item.department, 
                        'name': item.name, 
                        'other' :item.other, 
                        'title' : item.title,
                        'email': item.email,
                        'chat_id': item.chat_id})
        return Response({'data': results})
