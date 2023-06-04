from django.urls import path
from . import views

app_name = 'orders'
urlpatterns = [
    path('data/', views.order_data_view, name='data'),
    path('<int:id>/', views.order_detail_view, name='detail'),
    path('confirm/<slug:oidb64>/<slug:token>', views.order_confirm_view, name='confirm'),
    path('checkout/success', views.checkout_successful_view, name='checkout_success'),
    path('checkout/cancelled', views.checkout_cancelled_view, name='checkout_cancelled'),
    path('webhooks/stripe/', views.stripe_webhook, name='stripe_webhook')
]