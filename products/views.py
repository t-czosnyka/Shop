from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, ProductImage
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
    product = get_object_or_404(Product, pk=pk)
    product.assign_main_img()
    # Add specific product to cart and reload the page
    if request.GET.get('add_cart', False):
        product_specific = product.get_product_specific_by_attributes(request.GET)
        response = add_to_cart(request, product_specific)
        return response
    # get product available specific products based on request GET parameters
    specific_attributes = product.get_filtered_product_specific_attributes(request.GET)
    # get queryset of images referring this product with its main img as the first one
    if product.main_img is not None and product.main_img.main_img is not None:
        main_img_id = product.main_img.main_img.id
        main_img = ProductImage.objects.filter(product=product, id=main_img_id)
        other_img = ProductImage.objects.filter(product=product).exclude(id=main_img_id)
        images = main_img.union(other_img)
    else:
        images = ProductImage.objects.filter(product=product)
    # get ratings that involve a comment
    comments = product.ratings.exclude(comment="")
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

