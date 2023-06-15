from django.contrib import admin
from .models import Product, ProductShoe, Producer, Color, ProductSuit, ProductShirt,\
    ProductImage, ProductMainImage, Rating, ProductBackpack
from django.forms import ModelForm
from django.db.models import ObjectDoesNotExist

# Register your models here.
admin.site.register(Producer)
admin.site.register(Color)
admin.site.register(Rating)


class ProductImageAdmin(admin.ModelAdmin):
    exclude = ('thumbnail',)


class ProductAdmin(admin.ModelAdmin):
    readonly_fields = ('avg_rating',)


class ProductSpecificAdmin(admin.ModelAdmin):
    # Filter products only matching ProductSpecific TYPE.
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "product":
            kwargs["queryset"] = Product.objects.filter(type=self.model.TYPE)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    readonly_fields = ('stripe_product_id', 'stripe_price_id')


# Filter ProductImages only referring to set Product.
class MainImageForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            self.fields['main_img'].queryset = ProductImage.objects.filter(product=self.instance.product)
        except ObjectDoesNotExist:
            pass


class ProductMainImageAdmin(admin.ModelAdmin):

    form = MainImageForm


admin.site.register(ProductImage, ProductImageAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductShoe, ProductSpecificAdmin)
admin.site.register(ProductSuit, ProductSpecificAdmin)
admin.site.register(ProductShirt, ProductSpecificAdmin)
admin.site.register(ProductBackpack, ProductSpecificAdmin)
admin.site.register(ProductMainImage, ProductMainImageAdmin)
