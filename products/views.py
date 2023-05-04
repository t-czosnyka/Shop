from django.shortcuts import render, redirect
from .models import Product, ProductImage
from .cart import add_to_cart, clear_cart, get_cart_specific_products, remove_from_cart
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
    cart_products = get_cart_specific_products(request)
    context = {
        'title': 'Cart',
        'cart_products': cart_products
    }
    return render(request, 'products/cart.html', context)

def clear_cart_view(request):
    clear_cart(request)
    return redirect('products:cart')


def product_detail_view(request, pk):
    if request.method == 'GET':
        product = Product.objects.get(pk=pk)
        product.assign_main_img()
        # Add specific product to cart and reload the page
        if request.GET.get('add_cart', False):
            product_specific = product.check_product_specific(request.GET)
            response = add_to_cart(request, product_specific)
            return response
        # get product variants filtered based on GET request parameters
        specific_attributes = product.get_filtered_product_specific_attributes(request.GET)
        # get queryset of images referring this product with its main img as the first one
        if product.main_img is not None and product.main_img.main_img is not None:
            main_img_id = product.main_img.main_img.id
            main_img = ProductImage.objects.filter(product=product, id=main_img_id)
            other_img = ProductImage.objects.filter(product=product).exclude(id=main_img_id)
            images = main_img.union(other_img)

        else:
            images = ProductImage.objects.filter(product=product)
        context = {
            'product': product,
            'images': images,
            'specific_attributes': specific_attributes,
            'title' : 'Detail'
                   }
        return render(request, 'products/product_detail.html', context)