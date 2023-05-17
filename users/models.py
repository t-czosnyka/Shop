from django.db import models
from django.contrib.auth.models import User
# Create your models here.

# Make user email field required and unique
User._meta.get_field('email')._unique = True
User._meta.get_field('email').blank = False
User._meta.get_field('email').null = False


class UserData(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_data')
    state = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=50, blank=True)
    street = models.CharField(max_length=50, blank=True)
    number = models.CharField(max_length=50, blank=True)
    postal_code = models.CharField(max_length=50, blank=True)

    class Meta:
        verbose_name_plural = "Users data"

    def __str__(self):
        return str(self.user)

