from rest_framework.decorators import api_view, renderer_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import ProductSpecificDetailSerializer, ProductSpecificListSerializer, ProductSerializer
from products.models import Product
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer

# Create your views here.


class ProductListView(APIView):
    serializer_class = ProductSerializer

    def get(self, request):
        context = {'request': request}
        product = Product.objects.all()
        serializer = ProductSerializer(product, many=True, context=context)
        return Response(serializer.data)

    def post(self, request):
        context = {'request': request}
        serializer = ProductSerializer(data=request.data, context=context)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductDetailRenderer(BrowsableAPIRenderer):
    # Adds POST form to create ProductSpecific objects referencing current Product
    # Adds PUT form with current Product instance

    def get_context(self, data, accepted_media_type, renderer_context):
        context = super().get_context(data, accepted_media_type, renderer_context)
        try:
            pk = data.get('pk')
        except AttributeError:
            pk = None
        post_form = None
        put_form = None
        if pk is not None:
            # PUT form - Product
            product = get_object_or_404(Product, pk=pk)
            product_serializer = ProductSerializer(instance=product, context=context)
            put_form = self.render_form_for_serializer(product_serializer)
            # POST form - ProductSpecific
            product_specific_model = product.get_product_specific_model()
            serializer = ProductSpecificDetailSerializer(model=product_specific_model, context=context)
            # Remove product field from form.
            serializer.fields.pop('product')
            post_form = self.render_form_for_serializer(serializer)
        context['display_edit_forms'] = pk is not None
        context['post_form'] = post_form
        context['put_form'] = put_form
        return context


class ProductDetailView(APIView):

    renderer_classes = [JSONRenderer, ProductDetailRenderer]

    def get(self, request, product_pk):
        context = {'request': request}
        product = get_object_or_404(Product, pk=product_pk)
        serializer = ProductSerializer(product, many=False, context=context)
        return Response(serializer.data)

    def delete(self, request, product_pk):
        product = get_object_or_404(Product, pk=product_pk)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def put(self, request, product_pk):
        product = get_object_or_404(Product, pk=product_pk)
        serializer = ProductSerializer(instance=product, many=False, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, product_pk):
        # Create new ProductSpecific referencing this Product.
        product = get_object_or_404(Product, pk=product_pk)
        context = {'request': request}
        data = request.data.copy()
        data['product'] = product.pk
        serializer = ProductSpecificDetailSerializer(data=data, context=context)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductSpecificDetailView(APIView):
    serializer_class = ProductSpecificDetailSerializer

    def get(self, request, product_pk, product_specific_pk):
        context = {'request': request}
        product_specific = Product.get_product_specific(product_pk, product_specific_pk)
        serializer = ProductSpecificDetailSerializer(product_specific, many=False, context=context)
        return Response(serializer.data)

    def delete(self, request, product_pk, product_specific_pk):
        product_specific = Product.get_product_specific(product_pk, product_specific_pk)
        product_specific.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def put(self, request, product_pk, product_specific_pk):
        context = {'request': request}
        product_specific = Product.get_product_specific(product_pk, product_specific_pk)
        serializer = ProductSpecificDetailSerializer(instance=product_specific, data=request.data, context=context)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)








