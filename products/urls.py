from django.urls import path
from django.conf import settings
from . import views

app_name = 'products'
urlpatterns = [
    path('<int:pk>', views.product_detail_view, name='detail'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/clear', views.clear_cart_view, name='clear-cart'),
    path('cart/add/<int:p_id>/<int:ps_id>', views.add_cart_view, name='add-cart'),
    path('cart/remove/<int:p_id>/<int:ps_id>', views.remove_cart_view, name='remove-cart'),
]



