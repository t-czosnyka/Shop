from django.contrib import admin
from .models import Order, OrderProducts
# Register your models here.

admin.site.register(Order)
admin.site.register(OrderProducts)