from django.shortcuts import render, redirect
from .models import Product, ProductImage
from django.contrib import messages
# Create your views here.


def product_detail_view(request, pk):
    if request.method == 'GET':
        product = Product.objects.get(pk=pk)
        product.assign_main_img()
        # Add specific product to cart and reload the page
        if request.GET.get('cart', False):
            print('Add to cart')
            result, specific_product = product.add_to_cart(request.GET)
            if result:
                messages.success(request, f'Product {specific_product}  added to cart.')
            else:
                messages.warning(request, f'Wrong product parameters.')
            return redirect('products:detail', pk=pk)
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
                   }
        return render(request, 'products/product_detail.html', context)