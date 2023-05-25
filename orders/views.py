from django.shortcuts import render, redirect, reverse, get_object_or_404
from products.cart import get_cart_products_specific_all, clear_cart
from .models import Order, OrderProducts
from django.contrib import messages
from .forms import OrderForm
from django.conf import settings
from django.contrib.auth.models import User
from django.forms.models import model_to_dict
from django.apps import apps
from django.db.models import ObjectDoesNotExist
from django.http import HttpResponseForbidden
# Create your views here.

UserData = apps.get_model('users', 'UserData')


def order_data_view(request):
    # get order data and create order
    user_object = None
    if request.user.is_authenticated:
        user_object = User.objects.get(id=request.user.id)
    # user logged in or selected to order without login
    if user_object is None and not request.session.get('no_login_order', False):
        url = settings.LOGIN_URL + '?next=' + request.path + '&order=True'
        return redirect(url)
    # redirect if cart is empty
    products = get_cart_products_specific_all(request)
    if len(products) == 0:
        messages.warning(request, "No products to order.")
        return redirect('pages:home')
    form = OrderForm(request.POST or None)
    # get user data and put into initial form
    if request.method == "GET" and user_object is not None:
        data = model_to_dict(user_object, fields=['email', 'first_name', 'last_name'])
        try:
            user_data_object = UserData.objects.get(user=user_object)
            data.update(model_to_dict(user_data_object))
        except ObjectDoesNotExist:
            pass
        form.initial = data
    elif request.method == "POST":
        if form.is_valid():
            order_object = form.save(commit=False)
            # if user is logged in order is automatically confirmed and user is assigned
            if user_object is not None:
                order_object.user = user_object
                order_object.confirmed = True
            # Create order products, not using bulk_create to call save method
            for product in products:
                order_product = OrderProducts(order=order_object, product_specific=product)
                order_product.save(create=True)
            clear_cart(request)
            order_object.send_to_user()
            messages.success(request, f"Your order number {order_object.id} has been created.")
            return redirect('pages:home')
        else:
            messages.warning(request, "Wrong data inserted.")
    context = {
        'title': 'Order data',
        'form': form
    }
    return render(request, 'orders/order_data.html', context)


def order_detail_view(request, id):
    order_object = get_object_or_404(Order, id=id)
    # Check if user is authenticated.
    if not request.user.is_authenticated:
        # redirect to login page
        messages.warning(request, "Login required.")
        url = settings.LOGIN_URL + '?next=' + request.path
        return redirect(url)
    # Check if user is authorized to access this page.
    elif order_object.user is None or order_object.user.id != request.user.id:
        return HttpResponseForbidden(request)
    context ={
        'title': 'Order details',
        'order': order_object,
    }
    return render(request, 'orders/order_detail.html', context)


def order_confirm_view(request, token):
    pass



