from django.shortcuts import render
from rest_framework.views import APIView
from .models import MegaEmployee
from rest_framework.response import Response
from django.db.models import Q
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
    
class ErpProfile(APIView):
    def post(self, request): 
        result = {}
        code = request.data.get('Code')

        results = MegaEmployee.objects.filter(Q(code=code) | 
                    (Q(email=code)&  Q(email__isnull=False)) | \
                    (Q(other=code)&  Q(other__isnull=False))    )
        if len(results)> 0:
            item = results[0]
            result = {'EmployeeId': item.code, 
                        'Photo': None, 
                        'DepartmentName' : item.department, 
                        'FullName': item.name, 
                        'DepartmentId' :'', 
                        'JobTitleName' : item.title,
                        'JobTitleId': 0,
                        'HomeEmail': None,
                        'WorkEmail': item.email,
                        'chat_id': item.chat_id}
        return Response({'data': result})

class ErpLink(APIView):
    def post(self, request): 
        result = {}
        email = request.data.get('email')
        password = request.data.get('password')
        chat_id = request.data.get('chat_id')
        results = MegaEmployee.objects.filter(Q(code=email) | \
                    (Q(email=email) &  Q(email__isnull=False)) | \
                    (Q(other=email) &  Q(other__isnull=False)))
        for item in results:
            item.chat_id = chat_id
            item.save()
        return Response({'data': results})