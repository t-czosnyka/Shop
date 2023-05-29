from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from .models import Product, PRODUCT_TYPES
from .cart import add_to_cart, clear_cart, get_cart_products_specific_list, remove_from_cart, get_cart_status
from .forms import RatingForm
from django.conf import settings
from django.contrib import messages
# Create your views here.


def add_cart_view(request, p_id, ps_id):
    ps = Product.get_product_specific(p_id, ps_id)
    add_to_cart(request, ps)
    return redirect('products:cart')


def remove_cart_view(request, p_id, ps_id):
    ps = Product.get_product_specific(p_id, ps_id)
    remove_from_cart(request, ps)
    return redirect('products:cart')


def cart_view(request):
    cart_products = get_cart_products_specific_list(request)
    cart_length, cart_value = get_cart_status(request)
    context = {
        'title': 'Cart',
        'cart_products': cart_products,
        'cart_length': cart_length,
        'cart_value': cart_value,
    }
    return render(request, 'products/cart.html', context)


def clear_cart_view(request):
    clear_cart(request)
    return redirect('products:cart')


def product_detail_view(request, pk):
    ORDERING = {
        '1': '-created',  # newest
        '2': 'created',  # oldest
        '3': '-value',  # highest value
        '4': 'value',   # lowest value
    }
    product = get_object_or_404(Product, pk=pk)
    # Add specific product to cart and reload the page
    if request.GET.get('add_cart', False):
        product_specific = product.get_product_specific_by_attributes(request.GET)
        response = add_to_cart(request, product_specific)
        return response
    # get product available specific products based on request GET parameters
    specific_attributes = product.get_filtered_product_specific_attributes(request.GET)
    # create list of images with main image as first object
    main_image = product.main_image_object
    other_images = list(product.images.exclude(id=main_image.id))
    images = [main_image] + other_images
    # get ratings that involve a comment
    comments = product.ratings.exclude(comment="")
    # order comments by order parameter in query dict, default from the newest to oldest
    order = request.GET.get('order', '1')
    comments = comments.order_by(ORDERING.get(order, '-created'))
    context = {
        'title': 'Product Detail',
        'product': product,
        'images': images,
        'specific_attributes': specific_attributes,
        'comments': comments
               }
    return render(request, 'products/product_detail.html', context)


def product_rate_view(request, pk):
    # check if user already rated this product
    instance = None
    if request.user.is_authenticated:
        product = get_object_or_404(Product, pk=pk)
        instance = product.ratings.filter(user=request.user).first()
    else:
        # redirect to login page
        messages.warning(request, "Login required.")
        url = settings.LOGIN_URL + '?next=' + request.path
        return redirect(url)
    form = RatingForm(request.POST or None, instance=instance)
    if request.method == 'POST':
        if form.is_valid():
            rating = form.save(commit=False)

            rating.product = product
            rating.user = request.user
            rating.save()
            return redirect('products:detail', pk=pk)
    context = {
        'title': 'Rate Product',
        'form': form
    }
    return render(request, 'products/product_rate_form.html', context)


def product_type_view(request, product_type):
    products = get_list_or_404(Product, type=product_type)
    type_name = PRODUCT_TYPES[str(product_type)]
    context = {
        'title': f"Category {type_name}s",
        'products': products,
        'type_name': type_name
    }
    return render(request, 'products/product_type.html', context)

