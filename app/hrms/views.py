from django.views import View
from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader


def taskcreate(request):
    context = {}
    html_template = loader.get_template('hrms/task_create.html')
    return HttpResponse(html_template.render(context, request))
