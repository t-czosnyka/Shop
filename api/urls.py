from django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token


app_name = 'api'

urlpatterns = [
    path('products/', views.ProductListView.as_view(), name="product-list"),
    path('token/', views.AdminObtainAuthToken.as_view()),
    path('products/<int:product_pk>', views.ProductDetailView.as_view(), name="product-detail"),
    path('products/<int:product_pk>/<int:product_specific_pk>', views.ProductSpecificDetailView.as_view(),
         name="product-specific-detail"),
]

