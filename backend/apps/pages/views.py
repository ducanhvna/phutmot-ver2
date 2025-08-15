from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def index(request):
    # Page from the theme 
    return render(request, 'pages/index.html', {'segment': 'dashboard'})


def pos(request):

    # Page from the theme 
    return render(request, 'backend/index.html', {'segment': 'pos'})

def pos_list_product(request):
    print("Request received at pos_list_product view")  # Debugging line

    # Page from the theme 
    return render(request, 'backend/pos-list-product.html', {'segment': 'pos_list_product'})

def pos_add_product(request):
    print("Request received at pos_add_product view")  # Debugging line

    # Page from the theme 
    return render(request, 'backend/pos-add-product.html', {'segment': 'pos_add_product'})