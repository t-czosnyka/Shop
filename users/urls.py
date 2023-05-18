from django.urls import path
from . import views

app_name = 'users'
urlpatterns = [
    path('login', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
    path('register', views.register_view, name='register'),
    path('nologin', views.no_login_order, name='nologin'),
    path('reset/email', views.reset_insert_email_view, name='reset_insert_email'),
    path('reset/<uidb64>/<token>', views.reset_new_password_view, name='reset_new_password')
]