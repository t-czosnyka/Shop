from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.core.mail import send_mail
from .token_generator import order_confirmation_token_generator
from django.utils.http import urlsafe_base64_encode

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
        (DELIVERED, "Delivered"),]
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
    confirmed = models.BooleanField(default=False)
    stripe_checkout_id = models.CharField(max_length=220, blank=True, null=True)

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

    def send_to_user(self, request, checkout_url=None):
        # Send email to user with order data and confirmation link if necessary. If order is already confirmed send
        # checkout_url to complete payment.
        subject = f"Your Order nr: {self.id}"
        message = f"Your order number {self.id} has been created. Order data:\n"
        for data in self.get_order_data():
            message += f"{data[0]}: {data[1]}\n"
        message += "List of products: \n"
        i = 1
        for product in self.order_products.all():
            message += f"{i}. {str(product.product_specific)}\n"
        if not self.confirmed:
            oidb64 = urlsafe_base64_encode(str(self.id).encode())
            token = order_confirmation_token_generator.make_token(self)
            url = request.build_absolute_uri(f'/orders/confirm/{oidb64}/{token}')
            message += f"\nYour order is not confirmed. Follow this link to confirm it:\n"
            message += url
            subject += " (Unconfirmed)"
        elif checkout_url is not None:
            message += f"\nYour order is confirmed. Link to payment:\n"
            message += checkout_url
        send_mail(subject=subject, message=message, from_email="Django MyShop", recipient_list=[self.email])

    def send_confirmation_ok_email(self, checkout_url):
        subject = f"Your Order nr: {self.id} is now confirmed."
        message = f"Your order has been successfully confirmed."
        if checkout_url is not None:
            message += f"\nLink to payment:\n"
            message += checkout_url
        send_mail(subject=subject, message=message, from_email="Django MyShop", recipient_list=[self.email])

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
                self.product_price = self.product_specific.product.current_price
            except AttributeError as e:
                pass
        super().save(**kwargs)

    def __str__(self):
        return f"Order:{self.order.id}-{self.product_name}"
