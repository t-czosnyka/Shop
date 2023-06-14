from django.urls import path
from . import views

urlpatterns = [
    path('products/', views.ProductView.as_view(), name="products"),
    path('products/create/', views.ProductCreateView.as_view(), name="product-create"),
]

