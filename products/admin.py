from django.contrib import admin
from .models import Product, ProductShoe, Producer, Color, ProductSuit, ProductShirt, ProductImage, ProductMainImage

# Register your models here.

admin.site.register(Product)
admin.site.register(Producer)
admin.site.register(ProductShoe)
admin.site.register(ProductSuit)
admin.site.register(ProductShirt)
admin.site.register(ProductMainImage)
admin.site.register(Color)


class ProductImageAdmin(admin.ModelAdmin):
    exclude = ('thumbnail',)

admin.site.register(ProductImage, ProductImageAdmin)