from .models import PRODUCT_TYPES_PLURALS


def products_context(request):
    context = dict()
    context['product_types'] = PRODUCT_TYPES_PLURALS.values()
    return context
