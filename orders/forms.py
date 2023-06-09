from django.forms import ModelForm
from .models import Order


class OrderForm(ModelForm):

    class Meta:
        model = Order
        exclude = ['user', 'product_count', 'total', 'status', 'confirmed', 'stripe_checkout_id']
