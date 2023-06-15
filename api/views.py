from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import ProductSpecificDetailSerializer, ProductSpecificListSerializer, ProductSerializer
from products.models import Product
from django.shortcuts import get_object_or_404

# Create your views here.


class ProductView(APIView):
    def get(self, request, product_pk=None):
        if product_pk is None:
            product = Product.objects.all()
            serializer = ProductSerializer(product, many=True)
        else:
            product = get_object_or_404(Product, pk=product_pk)
            serializer = ProductSerializer(product, many=False)
        return Response(serializer.data)


class ProductSpecificView(APIView):
    def get(self, request, product_pk, product_specific_pk):
        product_specific = Product.get_product_specific(product_pk, product_specific_pk)
        serializer = ProductSpecificDetailSerializer(product_specific)
        return Response(serializer.data)


class ProductCreateView(APIView):
    pass
    # def get(self, request):
    #     product = Product.objects.first()
    #     data = {
    #         "size": 42,
    #         "available": True,
    #         "color": 1,
    #         "product": product.id,
    #
    #     }
    #     serializer = ProductSpecificInlineSerializer(product.get_product_specific_set().first(), many=False , data=data)
    #     if serializer.is_valid(raise_exception=True):
    #         serializer.save()
    #     return Response(serializer.data)


