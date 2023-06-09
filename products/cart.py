from django.contrib import messages
from django.shortcuts import redirect
from .models import ProductSpecific, Product

# Cart is implemented by adding 'cart' key to session containing a dict.
# This dict contains keys formatted as full_id:"<Product.id>_<ProductSpecific.id>" and values are amounts of
# these products currently in the cart.


def add_to_cart(request, product_specific):
    # Add product_specific object to cart.
    # Check if correct product is passed into function.
    if not product_specific or not isinstance(product_specific, ProductSpecific):
        messages.warning(request, 'Wrong product specified.')
    else:
        current_cart = request.session.get('cart', {})
        # get identification of product specific "Product.id"_"ProductSpecific.id"
        full_id = product_specific.get_full_id()
        # increase amount of product_specific or add new key
        current_cart[full_id] = current_cart.get(full_id, 0) + 1
        # update cart and cart length in session
        request.session['cart'] = current_cart
        request.session['cart_length'] = request.session.get('cart_length', 0) + 1
        messages.success(request, f'Product {product_specific} added to cart.')
    return redirect(request.path)


def remove_from_cart(request, product_specific):
    # Remove product_specific object from cart.
    current_cart = request.session.get('cart', {})
    if not product_specific or not isinstance(product_specific, ProductSpecific):
        messages.warning(request, 'Wrong product specified.')
        return redirect(request.path)
    full_id = product_specific.get_full_id()
    if full_id not in current_cart:
        messages.warning(request, 'Product not in cart.')
    else:
        # decrease amount of product_specific in cart
        current_cart[full_id] -= 1
        # if amount is less than equal zero remove the product_specific key form cart dict
        if current_cart[full_id] <= 0:
            del current_cart[full_id]
        # update session
        request.session['cart'] = current_cart
        request.session['cart_length'] = request.session.get('cart_length', 0) - 1
        messages.success(request, f'Product {product_specific} removed from cart.')
    return redirect(request.path)


def get_cart_products_specific_list(request):
    # Function returns ProductsSpecific objects in cart as a list of tuples
    # containing ProductSpecific object and amount of this object.
    current_cart = get_current_cart(request)
    products = []
    for full_id, amount in current_cart.items():
        product_id, product_specific_id = full_id.split('_')
        product_specific = Product.get_product_specific(product_id, product_specific_id)
        products.append((product_specific, amount))
    return products

def get_cart_status(request):
    # calculate total amount of items in cart and value of those items
    total_amount = 0
    total_value = 0
    # get current cart dictionary from user session
    current_cart = get_current_cart(request)
    for full_id, amount in current_cart.items():
        # split full_id into product and product_specific_ids
        product_id, product_specific_id = full_id.split('_')
        product_specific = Product.get_product_specific(product_id, product_specific_id)
        total_amount += amount
        total_value += amount*product_specific.product.current_price
    # update cart_length session object
    request.session['cart_length'] = total_amount
    request.session['cart_value'] = str(total_value)
    return total_amount, total_value


def clear_cart(request):
    # delete all cart information from user session
    if 'cart' in request.session:
        del request.session['cart']
    if 'cart_length' in request.session:
        del request.session['cart_length']
    if 'cart_value' in request.session:
        del request.session['cart_value']


def get_current_cart(request):
    # function to get current cart status and check if it contains correct values and remove incorrect keys
    current_cart = {}
    check_cart = request.session.get('cart', {})
    if not isinstance(check_cart, dict):
        return current_cart
    delete_keys = []
    for key in check_cart.keys():
        if not isinstance(key, str) or '_' not in key:
            delete_keys.append(key)
    for key in delete_keys:
        del check_cart[key]
    current_cart = check_cart
    return current_cart
