from django.shortcuts import render, redirect
from .models import Product, ProductImage
# Create your views here.


def product_detail_view(request, pk):
    if request.method == 'GET':
        product = Product.objects.get(pk=pk)
        # Add specific product to cart and reload the page
        if request.GET.get('cart', False):
            print('Add to cart')
            specific_product = product.add_to_cart(request.GET)
            print(specific_product)
            return redirect('products:detail', pk=pk)
        #
        attributes = product.get_specific_product_variants(request.GET)
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
            'attributes': attributes,
                   }
        return render(request, 'products/product_detail.html', context)