from products.models import PRODUCT_TYPES
from django.utils.http import urlsafe_base64_encode


def products_context(request):
    context = dict()
    context['product_types'] = PRODUCT_TYPES
    return context


def uidb64_context(request):
    context = dict()
    if request.user.is_authenticated:
        uidb64 = urlsafe_base64_encode(str(request.user.id).encode())
        context['uidb64'] = uidb64
    return context

