# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.http.response import JsonResponse
from django.contrib.auth.models import User
from .models import Device, create_new_ref_number
from rest_framework.views import APIView
from rest_framework.response import Response
from .tasks import create_random_posts
from .models import Company, Device

def post_generator(request):
    print('aaaaaaaaaaaaaaa')
    create_random_posts.delay()
    return JsonResponse({"success": True})


@login_required(login_url="/login/")
def index(request):
    context = {'segment': 'index'}

    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template

        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))

class CreateDevice(APIView):
    def post(self, request, format=None):
        device_id = request.data.get('id')
        device_type = request.data.get('type')
        
        devices = Device.objects.filter(id=device_id)
        
        if len(devices) == 0:
            code = create_new_ref_number()
            while len(User.objects.filter(username=code)) > 0:
                code = create_new_ref_number()
            print('code: ',code)
            # device_id = request.data.get('id')
            user = User.objects.create_user(username=code,
                                    email=f'{code}@hinosoft.com',
                                    password=code)
            device = Device(type = device_type, name=code, id=device_id, user= user)
            device.save()
            result = {'device_id': device.id,'device_name': device.name, 'owner': device.user_owner, 
                'username': user.username}
            # return Response(device)
        else:
            device = devices[0]
            if not device.name:
                device.name = device.user.username if device.user else None
                device.save()
            try:
                result = {'device_id': device.id,
                            'device_name': device.name, 
                            'owner': device.user_owner.username if device.user_owner else None, 
                            'username': device.user.username if device.user else None}
            except:
                result = {'device_id': device.id,
                            'device_name': device.name, 
                            'owner': device.user_owner.username if device.user_owner else None, 
                            'username': device.user.username if device.user else None}
        try:      
            if device.user_owner:
                device_company = None if not device.user_owner.user_device else device.user_owner.user_device.company
                result['api'] = 'api/core' if not device_company else 'api/core' if not device_company.api_version else device_company.api_version
                company_info = device_company
                target_device =  device.user_owner.user_device
            else:    
                result['api'] = 'api/core' if not device.company else 'api/core' if not device.company.api_version else device.company.api_version
                company_info = device.company
                target_device =  device
            result['usr']= target_device.username
            result['pas']= target_device.password
            result['url']= company_info.username
            result['db']= company_info.dbname
        except Exception as ex:
            result['error'] = 400
            result['usr']   = ''
            result['pas']   = ''
            result['url']   = ''
            result['db']    = ''
        return Response(result)
        
# create a viewset 
class CompanyViewSet(APIView): 
    # define queryset 
    def get(self, request, *args, **kwargs): 
        result =[]
        queryset = Company.objects.all() 
        for item in queryset:
            result.append({'id': item.id, 'name': item.name, 'api_version': item.api_version, 'code': item.code})
        # print('aaaaaa')
        return Response({'count': len(result),'data':result})
        