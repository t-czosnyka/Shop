from django.contrib import messages
from django.shortcuts import redirect
from .models import ProductSpecific, Product


def add_to_cart(request, product_specific):
    if product_specific and isinstance(product_specific, ProductSpecific):
        current_cart = request.session.get('cart', {})
        id = product_specific.get_full_id()
        current_cart[id] = current_cart.get(id, 0) + 1
        request.session['cart'] = current_cart
        request.session['cart_length'] = request.session.get('cart_length', 0) + 1
        messages.success(request, f'Product {product_specific} added to cart.')
    else:
        messages.warning(request, f'Wrong product parameters.')
    return redirect(request.path)


def remove_from_cart(request, product_specific):
    current_cart = request.session.get('cart', {})
    if product_specific and isinstance(product_specific, ProductSpecific) and \
            product_specific.get_full_id() in current_cart:
        id = product_specific.get_full_id()
        current_cart[id] -= 1
        if current_cart[id] <= 0:
            del current_cart[id]
        request.session['cart'] = current_cart
        request.session['cart_length'] = request.session.get('cart_length', 0) - 1
        messages.success(request, f'Product {product_specific} removed from cart.')
    elif product_specific.get_full_id() not in current_cart:
        messages.warning(request, f'Product not in cart.')
    else:
        messages.warning(request, f'Wrong product specified.')
    return redirect(request.path)


def get_cart_specific_products_list(request):
    current_cart = request.session.get('cart', {})
    products = []
    for full_id, amount in current_cart.items():
        product_id, product_specific_id = full_id.split('_')
        product_specific = Product.get_product_specific(product_id, product_specific_id)
        products.append((product_specific, amount))
    return products

def get_cart_status(request):
    total_amount = 0
    total_value = 0
    current_cart = request.session.get('cart', {})
    for full_id, amount in current_cart.items():
        product_id, product_specific_id = full_id.split('_')
        product_specific = Product.get_product_specific(product_id, product_specific_id)
        total_amount += amount
        total_value += amount*product_specific.product.price
    request.session['cart_length'] = total_amount
    return total_amount, total_value

def clear_cart(request):
    if 'cart' in request.session:
        del request.session['cart']
    if 'cart_length' in request.session:
        del request.session['cart_length']

