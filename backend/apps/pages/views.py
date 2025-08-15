from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def index(request):
    print("Request received at index view")  # Debugging line
    # Page from the theme 
    return render(request, 'pages/index.html', {'segment': 'dashboard'})


def pos(request):
    print("Request received at pos view")  # Debugging line

    # Page from the theme 
    return render(request, 'backend/index.html', {'segment': 'pos'})
