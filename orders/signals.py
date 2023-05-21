from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import OrderProducts


@receiver(post_delete, sender=OrderProducts)
def recalculate_order(instance, **kwargs):
    # recalculate order total and product amount if OrderProduct is deleted
    instance.order.calculate_products()
    instance.order.save()

