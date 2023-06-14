from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import ProductSpecificDetailSerializer, ProductSerializer
from products.models import Product

# Create your views here.


class ProductView(APIView):

    def get(self, request, format=None):
        """
        Return a list of all users.
        """
        product = Product.objects.all()
        serializer = ProductSerializer(product, many=True)
        return Response(serializer.data)


class ProductCreateView(APIView):
    def get(self, request):
        product = Product.objects.first()
        data = {
            "size": 42,
            "available": True,
            "color": 1,
            "product": product.id,

        }
        serializer = ProductSpecificDetailSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response(serializer.data)


