from django.shortcuts import render
from django.apps import apps
# Create your views here.


def home_view(request):
    Product = apps.get_model('products', 'Product')
    # Get 9 promoted products in random order to display on home page.
    products = Product.objects.filter(promoted=True).order_by("?")[:9]
    context = {'products': products}
    return render(request, 'pages/home.html', context)




