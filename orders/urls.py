from django.urls import path
from . import views

app_name = 'orders'
urlpatterns = [
    path('data/', views.order_data_view, name='data'),
    path('<int:id>/', views.order_detail_view, name='detail'),
    path('confirm/<slug:token>', views.order_confirm_view, name='confirm')
]