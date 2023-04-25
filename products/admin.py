from django.contrib import admin
from .models import Product, ProductShoe, Producer, Color, ProductSuit, ProductShirt, ProductImage

# Register your models here.

admin.site.register(Product)
admin.site.register(Producer)
admin.site.register(ProductShoe)
admin.site.register(Color)
admin.site.register(ProductSuit)
admin.site.register(ProductShirt)
admin.site.register(ProductImage)

class ProductAdmin(admin.ModelAdmin):
    exclude = ('main_img',)