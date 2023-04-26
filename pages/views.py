from django.shortcuts import render
from django.apps import apps
from django.core.paginator import Paginator
# Create your views here.

def home_view(request):
    Product = apps.get_model('products', 'Product')
    products = Product.objects.all()
    paginator = Paginator(products, 3)

    context = {'products': products, 'paginator': paginator}
    return render(request, 'pages/home.html', context)

def about_view(request):
    context = {}
    return render(request, 'pages/about.html', context)

def contact_view(request):
    context = {}
    return render(request, 'pages/contact.html', context)


