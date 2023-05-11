from django.shortcuts import render, redirect
from products.cart import get_cart_products_specific_all
from .models import Order, OrderProducts
# Create your views here.

def order_create(request):
    products = get_cart_products_specific_all(request)
    o = Order(email="aaa@bbb.com")
    o.save()
    batch = [OrderProducts(order=o, product_specific=prod) for prod in products]
    OrderProducts.objects.bulk_create(batch)
    print(products)
    return redirect('pages:home')
