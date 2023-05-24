from django.contrib import admin
from .models import Product, ProductShoe, Producer, Color, ProductSuit, ProductShirt, ProductImage, ProductMainImage, Rating

# Register your models here.


admin.site.register(Producer)
admin.site.register(ProductShoe)
admin.site.register(ProductSuit)
admin.site.register(ProductShirt)
admin.site.register(ProductMainImage)
admin.site.register(Color)
admin.site.register(Rating)


class ProductImageAdmin(admin.ModelAdmin):
    exclude = ('thumbnail',)


class ProductAdmin(admin.ModelAdmin):
    readonly_fields = ('avg_rating',)


admin.site.register(ProductImage, ProductImageAdmin)
admin.site.register(Product, ProductAdmin)
