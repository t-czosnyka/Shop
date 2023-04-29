from django.urls import path
from django.conf import settings
from . import views

app_name= 'products'
urlpatterns = [
    path('<int:pk>', views.product_detail_view, name='detail')
]



