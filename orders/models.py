from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
# Create your models here.


class Order(models.Model):
    WAIT_PAYMENT = "1"
    WAIT_SENDING = "2"
    SENT = "3"
    DELIVERED = "4"
    STATUS_CHOICES = [
        (WAIT_PAYMENT, "Waiting for payment"),
        (WAIT_SENDING, "Waiting for sending"),
        (SENT, "Sent"),
        (DELIVERED, "Delivered")]
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
    status = models.CharField(choices=STATUS_CHOICES, default=WAIT_PAYMENT, max_length=40)

    def __str__(self):
        return f"{self.id}-{self.email}"

    def __iter__(self):
        for field in self._meta.fields:
            name = field.verbose_name.capitalize()
            value = field.value_to_string(self)
            if field.choices is not None:
                f_name = 'get_' + field.name + '_display'
                display = getattr(self, f_name)
                value = display()
            if name.lower() in ['id', 'user', 'created', 'modified']:
                continue
            yield (name, value)

    def get_order_data(self):
        order_data = []
        for field in self:
            order_data.append(field)
        return order_data

    def get_order_products(self):
        return self.order_products.all()

    def send_to_user(self):
        # Send email to user with order data
        subject = f"Your Order nr: {self.id}"
        message = f"Your order number {self.id} has been created. Order data:\n"
        for data in self.get_order_data():
            message += f"{data[0]}: {data[1]}\n"
        message += "List of products: \n"
        i = 1
        for product in self.get_order_products():
            message += f"{i}. " + str(product.product_specific)
        self.user.email_user(subject=subject, message=message)

    @property
    def total_value(self):
        value = 0
        products = self.order_products.all()
        for product in products:
            value += product.product_price
        return value

    @property
    def total_items(self):
        return len(self.order_products.all())


class OrderProducts(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_products")
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    product_specific = GenericForeignKey("content_type", "object_id")

    product_name = models.CharField(max_length=100, default='', blank=True)
    product_price = models.DecimalField(default=0, blank=True, max_digits=10, decimal_places=2)

    class Meta:
        verbose_name_plural = "OrderProducts"

    def save(self, create=False, **kwargs):
        # save current product name and price in database(in case price changes in the future)
        if self.product_specific is not None and create:
            self.product_name = str(self.product_specific)
            try:
                self.product_price = self.product_specific.product.price
            except AttributeError as e:
                pass
        super().save(**kwargs)

    def __str__(self):
        return f"Order:{self.order.id}-{self.product_name}"
