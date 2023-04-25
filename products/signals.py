from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import ProductImage
import os

@receiver(post_delete, sender=ProductImage)
def auto_delete_image_file(sender, instance, using, **kwargs):
    # delete image file after ProductImage object is deleted
    img_path = instance.img.path
    if os.path.exists(img_path):
        os.remove(img_path)
