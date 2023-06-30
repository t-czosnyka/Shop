from rest_framework import serializers
from products.models import Product, ProductSpecific
from django.db.models.query import QuerySet
from rest_framework.reverse import reverse


class ProductSerializer(serializers.ModelSerializer):
    product_variants = serializers.SerializerMethodField(read_only=True)
    detail_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Product
        fields = ['pk', 'name', 'description', 'price', 'producer', 'type', 'avg_rating', 'current_price',
                  'product_variants', 'detail_url']
        read_only_fields = ['avg_rating', 'detail_url', 'product_variants']

    def get_product_variants(self, obj):
        qs = obj.get_product_specific_set()
        request = self.context.get('request')
        serializer = ProductSpecificListSerializer(qs, many=True, context={'request':request})
        return serializer.data

    def get_detail_url(self, obj):
        request = self.context.get('request')
        return reverse('api:product-detail', kwargs={'product_pk': obj.pk}, request=request)


class ProductSpecificDetailSerializer(serializers.ModelSerializer):

    product_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = None
        fields = ['pk', 'product', 'product_url', 'added', 'available']
        read_only_fields = ['added']

    def __init__(self, *args, **kwargs):
        model_class = kwargs.pop('model', None)
        super().__init__(*args, **kwargs)
        model = None
        if self.instance is not None:
            single_object = self.instance
            if isinstance(self.instance, QuerySet):
                single_object = self.instance.first()
            if single_object is not None:
                model = single_object.__class__
        else:
            # No instance provided. Get model based on provided product data.
            data = kwargs.get('data')
            if data is not None:
                product_pk = data.get("product")
                product = Product.objects.get(pk=product_pk)
                if product is not None:
                    model = product.get_product_specific_model()
            elif model_class is not None:
                model = model_class
        if model is not None and issubclass(model, ProductSpecific):
            self.Meta.model = model
            self.Meta.fields += self.Meta.model.attribute_field_names
        elif model is not None:
            raise TypeError("Instance is not subclass of ProductSpecific")

    def get_product_url(self, obj):
        request = self.context.get('request')
        return reverse('api:product-detail', kwargs={'product_pk': obj.product.pk}, request=request)


class ProductSpecificListSerializer(serializers.ModelSerializer):

    detail_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = None
        fields = []

    def get_detail_url(self, obj):
        product_pk = obj.product.pk
        product_specific_pk = obj.pk
        request = self.context.get('request')
        return reverse('api:product-specific-detail',
                       kwargs={'product_pk':product_pk, 'product_specific_pk':product_specific_pk}, request=request)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance is None:
            raise TypeError("Instance required for this serializer.")
        else:
            single_object = self.instance
            if isinstance(self.instance, QuerySet):
                single_object = self.instance.first()
        if isinstance(single_object, ProductSpecific):
            self.Meta.model = single_object.__class__
            self.Meta.fields = ['pk', 'available', 'detail_url'] + self.Meta.model.attribute_field_names
            self.Meta.read_only_fields = self.Meta.fields

    def create(self, validated_data):
        raise NotImplementedError("Create not allowed with this serializer.")

    def update(self, instance, validated_data):
        raise NotImplementedError("Update not allowed with this serializer.")






