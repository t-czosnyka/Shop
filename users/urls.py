from django.urls import path
from . import views

app_name = 'users'
urlpatterns = [
    path('login', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
    path('register', views.register_view, name='register'),
    path('nologin', views.no_login_order, name='nologin'),
    path('change_password/<slug:uidb64>', views.change_password_view, name='change_password'),
    path('change_data/<slug:uidb64>', views.change_data_view, name='change_data'),
    path('reset/email', views.reset_insert_email_view, name='reset_insert_email'),
    path('reset/<slug:uidb64>/<slug:token>', views.reset_new_password_view, name='reset_new_password')
]