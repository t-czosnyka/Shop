from django.contrib import admin
from .models import Order, OrderProducts
# Register your models here.

class OrderProductsAdmin(admin.ModelAdmin):
    readonly_fields = ["product_name", "product_price"]

admin.site.register(Order)
admin.site.register(OrderProducts, OrderProductsAdmin)