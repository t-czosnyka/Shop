from django.db.models.signals import post_delete, post_save, post_init
from django.dispatch import receiver
from .models import ProductImage, Product, ProductMainImage
import os

@receiver(post_delete, sender=ProductImage)
def auto_delete_image_file(sender, instance, using, **kwargs):
    # delete image file and thumbnail file after ProductImage object is deleted
    img_path = instance.img.path
    thumbnail_path = instance.thumbnail.path
    if os.path.exists(img_path):
        os.remove(img_path)
    if os.path.exists(thumbnail_path):
        os.remove(thumbnail_path)

@receiver(post_save, sender=Product)
def create_product_main_img(sender, instance, created, **kwargs):
    # Create ProductMainImg object as Product is created
    if created:
        prod_main_img = ProductMainImage(product=instance, main_img=None)
        prod_main_img.save()
