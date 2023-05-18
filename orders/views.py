from django.shortcuts import render, redirect, reverse, get_object_or_404
from products.cart import get_cart_products_specific_all, clear_cart
from .models import Order, OrderProducts
from django.contrib import messages
from .forms import OrderForm
from django.conf import settings
from django.contrib.auth.models import User
from django.forms.models import model_to_dict
# Create your views here.
from django.apps import apps
from django.db.models import ObjectDoesNotExist

UserData = apps.get_model('users','UserData')

def order_data_view(request):
    # get order data and create order
    # user logged in or selected to order without login
    if not request.user.is_authenticated and not request.session.get('no_login_order', False):
        url = settings.LOGIN_URL + '?next=' + request.path + '&order=True'
        return redirect(url)
    # redirect if cart is empty
    products = get_cart_products_specific_all(request)
    if len(products) == 0:
        messages.warning(request, "No products to order.")
        return redirect('pages:home')
    form = OrderForm(request.POST or None)
    # get user data and put into initial form
    if request.user.is_authenticated and not request.POST:
        user_obj = User.objects.get(id=request.user.id)
        data = model_to_dict(user_obj, fields=['email', 'first_name', 'last_name'])
        try:
            user_data_obj = UserData.objects.get(user=user_obj)
            data.update(model_to_dict(user_data_obj))
        except ObjectDoesNotExist:
            pass
        form.initial = data
    if request.method == "POST":
        if form.is_valid():
            order_object = form.save()
            # Create order products, not using bulk_create to call save method
            for product in products:
                order_product = OrderProducts(order=order_object, product_specific=product)
                order_product.save()
            clear_cart(request)
            messages.success(request, "Your order has been created.")
        return redirect('pages:home')
    context = {
        'title': 'Order data',
        'form': form
    }
    return render(request, 'orders/order_data.html', context)



