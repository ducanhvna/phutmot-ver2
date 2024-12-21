from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse


def index(request):
    context = {'segment': 'index'}
    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))
