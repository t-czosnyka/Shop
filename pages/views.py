from django.shortcuts import render
from django.apps import apps

# Create your views here.

def home_view(request):
    Product = apps.get_model('products', 'Product')
    products = Product.objects.all()
    context = {'products': products}
    return render(request, 'pages/home.html', context)

def about_view(request):
    context = {}
    return render(request, 'pages/about.html', context)

def contact_view(request):
    context = {}
    return render(request, 'pages/contact.html', context)


