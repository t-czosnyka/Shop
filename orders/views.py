from django.shortcuts import render, redirect, reverse, get_object_or_404, HttpResponse
from products import cart
from .models import Order, OrderProducts
from django.contrib import messages
from .forms import OrderForm
from django.conf import settings
from django.contrib.auth.models import User
from django.forms.models import model_to_dict
from django.apps import apps
from django.db.models import ObjectDoesNotExist
from django.http import HttpResponseForbidden
from django.utils.http import urlsafe_base64_decode
from .token_generator import order_confirmation_token_generator
from django.http import HttpResponseNotFound
from django.utils import timezone
import stripe
from django.views.decorators.csrf import csrf_exempt
# Create your views here.

UserData = apps.get_model('users', 'UserData')

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_checkout(request, order_object_id):
    try:
        order = Order.objects.get(id=order_object_id)
    except (ValueError, ObjectDoesNotExist):
        return None
    # Create stripe checkout session if order is confirmed.
    if order.confirmed:
        line_items = []
        for product in order.order_products.all():
            if product.product_specific.stripe_price_id is not None:
                line_items.append(
                    {
                        'price': product.product_specific.stripe_price_id,
                        'quantity': product.amount
                    }
                )
        success_url = request.build_absolute_uri(reverse('orders:checkout_success'))
        cancel_url = request.build_absolute_uri(reverse('orders:checkout_cancelled'))
        if line_items:
            stripe_checkout_session = stripe.checkout.Session.create(
                line_items=line_items,
                mode="payment",
                success_url=success_url,
                cancel_url=cancel_url,
                customer_email=order.email,
            )
            order.stripe_checkout_id = stripe_checkout_session.stripe_id
            order.save()
            return stripe_checkout_session.url
    return None


def order_data_view(request):
    ORDER_COOLDOWN_SEC = 60
    # get order data and create order
    user_object = None
    if request.user.is_authenticated:
        user_object = User.objects.get(id=request.user.id)
    # user logged in or selected to order without login
    if user_object is None and not request.session.get('no_login_order', False):
        url = settings.LOGIN_URL + '?next=' + request.path + '&order=True'
        return redirect(url)
    # redirect if cart is empty
    products = cart.get_cart_products_specific_list(request)
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
            # Check if last order on this email address was created after cooldown time to prevent duplicate orders.
            try:
                last_order = Order.objects.filter(email=form.cleaned_data['email']).latest('created')
                if (timezone.now() - last_order.created).seconds < ORDER_COOLDOWN_SEC:
                    messages.warning(request, "You can't create another order so quickly.")
                    return redirect('pages:home')
            except ObjectDoesNotExist:
                pass
            order_object = form.save(commit=False)
            # if user is logged in order is automatically confirmed and user is assigned
            if user_object is not None:
                order_object.user = user_object
                order_object.confirmed = True
            order_object.save()
            # Create order products, not using bulk_create to call save method
            for product, amount in products:
                order_product = OrderProducts(order=order_object, product_specific=product, amount=amount)
                order_product.save(create=True)
            checkout_session_url = create_checkout(request, order_object.id)
            order_object.send_to_user(request,  checkout_session_url)
            messages.success(request, f"Your order number {order_object.id} has been created.")
            cart.clear_cart(request)
            if checkout_session_url is not None:
                return redirect(checkout_session_url)
            else:
                messages.warning(request, "Confirm your order to checkout.")
                return redirect('pages:home')
        else:
            messages.warning(request, "Wrong data inserted.")
    context = {
        'title': 'Order data',
        'form': form
    }
    return render(request, 'orders/order_data.html', context)


def order_detail_view(request, pk):
    order_object = get_object_or_404(Order, pk=pk)
    # Check if user is authenticated.
    if not request.user.is_authenticated:
        # redirect to login page
        messages.warning(request, "Login required.")
        url = settings.LOGIN_URL + '?next=' + request.path
        return redirect(url)
    # Check if user is authorized to access this page.
    elif order_object.user is None or order_object.user.id != request.user.id:
        return HttpResponseForbidden(request)
    context = {
        'title': 'Order details',
        'order': order_object,
    }
    return render(request, 'orders/order_detail.html', context)


def order_confirm_view(request, oidb64, token):
    # Get order from base 64 encoded oidb64.
    try:
        order_id = urlsafe_base64_decode(oidb64)
        order = Order.objects.get(id=order_id)
    except (ValueError, ObjectDoesNotExist):
        return HttpResponseNotFound(request)

    if order.confirmed:
        messages.success(request, "Order already confirmed.")
    # Check provided token.
    elif order_confirmation_token_generator.check_token(order, token):
        order.confirmed = True
        order.save()
        checkout_session_url = create_checkout(request, order_id)
        order.send_confirmation_ok_email(checkout_session_url)
        if checkout_session_url is not None:
            return redirect(checkout_session_url)
    else:
        return HttpResponse('401 Unauthorized. Token error.', status=401)
    return redirect('pages:home')


def checkout_successful_view(request):
    return render(request, 'orders/checkout_successful.html')


def checkout_cancelled_view(request):
    return render(request, 'orders/checkout_cancelled.html')


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)
    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        data_object = event['data']['object']
        email = data_object.get('customer_email')
        checkout_id = data_object.get('id')
        try:
            order_object = Order.objects.get(email=email, stripe_checkout_id=checkout_id)
        except ObjectDoesNotExist:
            # No object found.
            return HttpResponse(status=400)
        # Change order status and send email confirmation to user.
        order_object.status = order_object.WAIT_SENDING
        order_object.save()
        order_object.send_payment_ok_email()
    return HttpResponse(status=200)

