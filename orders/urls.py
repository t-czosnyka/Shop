from django.urls import path
from . import views

app_name = 'orders'
urlpatterns = [
    path('data/', views.order_data_view, name='data'),
    path('create/', views.order_create_view, name='create')
]