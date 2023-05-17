from django.contrib import admin
from .models import UserData
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm
# Register your models here.


class UserCreateForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('email', 'username', 'password1', 'password2', )


class UserAdmin(UserAdmin):
    add_form = UserCreateForm
    #prepopulated_fields = {'username': ('first_name' , 'last_name', )}

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', ),
        }),
    )


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(UserData)

