from django.shortcuts import render, redirect
from products.cart import get_cart_products_specific_all, clear_cart
from .models import Order, OrderProducts
from django.contrib import messages
from .forms import OrderForm
# Create your views here.


def order_data_view(request):
    if request.method == "GET":
        if not request.user.is_authenticated:
            redirect()
        form = OrderForm()
        context = {
            'title': 'Order data',
            'form': form
        }
        return render(request, 'orders/order_data.html', context)

    if request.method == "POST":
        products = get_cart_products_specific_all(request)
        if len(products) == 0:
            messages.warning(request, "No products to order.")
            return redirect('pages:home')
        form = OrderForm(request.POST)
        if form.is_valid():
            order_object = form.save()
            # Create order products, not using bulk_create to call save method
            for product in products:
                order_product = OrderProducts(order=order_object, product_specific=product)
                order_product.save()
            clear_cart(request)
            messages.success(request, "Your order has been created.")
        return redirect('pages:home')


def order_create_view(request):
    products = get_cart_products_specific_all(request)
    if len(products) == 0:
        messages.warning(request, "No products to order.")
        return redirect('pages:home')
    o = Order(email="aaa@bbb.com")
    o.save()
    # Create order products, not using bulk_create to call save method
    for product in products:
        op = OrderProducts(order = o, product_specific=product)
        op.save()
    return redirect('pages:home')
