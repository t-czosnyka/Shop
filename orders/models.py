from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
# Create your models here.


class Order(models.Model):
    email = models.EmailField()
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    street = models.CharField(max_length=50)
    number = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=50)

    total = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True)
    product_count = models.IntegerField(default=0, blank=True)

    def __str__(self):
        return f"{self.id}-{self.email}"

    def calculate_products(self):
        products = self.order_products.objects.all()
        self.product_count = len(products)
        for product in products:
            self.total += product.product_price


class OrderProducts(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_products")
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    product_specific = GenericForeignKey("content_type", "object_id")

    product_name = models.CharField(max_length=100, default='', blank=True)
    product_price = models.DecimalField(default=0, blank=True, max_digits=10, decimal_places=2)

    class Meta:
        verbose_name_plural = "OrderProducts"

    def save(self, **kwargs):
        # save current product name and price in database(in case price changes in the future)
        if self.product_specific is not None:
            self.product_name = str(self.product_specific)
            try:
                self.product_price = self.product_specific.product.price
            except AttributeError as e:
                pass
        super().save(**kwargs)

    def __str__(self):
        return f"Order:{self.order.id}-{self.product_name}"
