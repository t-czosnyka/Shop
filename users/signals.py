from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import UserData, User

@receiver(post_save, sender=User)
def create_user_data(sender, instance, created, **kwargs):
    # Create user data every time new User is created
    if created:
        user_data = UserData(user=instance)
        user_data.save()