from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def index(request):

    # Page from the theme 
    return render(request, 'pages/index.html', {'segment': 'dashboard'})


def pos(request):

    # Page from the theme 
    return render(request, 'backend/index.html', {'segment': 'pos'})
