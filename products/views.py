from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from .models import Product, PRODUCT_TYPES, get_product_specific_attributes
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
    ORDERING = {
        '1': {'key': lambda x: x.current_price, 'reverse': False},  # Lowest price.
        '2': {'key': lambda x: x.current_price, 'reverse': True},  # Highest price.
        '3': {'key': lambda x: x.avg_rating, 'reverse': True},   # Best rating.
        '4': {'key': lambda x: x.avg_rating, 'reverse': False}   # Worst rating.
    }
    product = Product.objects.filter(type=product_type).first()
    # Get attribute values of all products of this type for filtering options.
    ProductSpecific_model = product.get_product_specific_model()
    all_products_specific = ProductSpecific_model.objects.all()
    attributes = get_product_specific_attributes(all_products_specific, request.GET)
    # Filter products_specific with request.GET parameters
    filtered_products_specific = ProductSpecific_model.filter_with_query_dict(request.GET)
    filtered_products_ids = filtered_products_specific.values_list('product', flat=True).distinct()
    filtered_products = get_list_or_404(Product, id__in=filtered_products_ids)
    # Ordering products
    ordering = request.GET.get('order', '1')
    filtered_products.sort(**ORDERING.get(ordering, ORDERING['1']))
    type_name = PRODUCT_TYPES[str(product_type)]
    context = {
        'title': f"Category {type_name}s",
        'products': filtered_products,
        'type_name': type_name,
        'attributes': attributes,
    }
    return render(request, 'products/product_type.html', context)

