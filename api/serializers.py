from rest_framework import serializers
from products.models import Product, ProductSpecific
from django.db.models.query import QuerySet


class ProductSerializer(serializers.ModelSerializer):
    product_variants = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'producer', 'type', 'avg_rating', 'current_price', 'product_variants']

    def get_product_variants(self, obj):
        qs = obj.get_product_specific_set()
        serializer = ProductSpecificListSerializer(qs, many=True)
        return serializer.data


class ProductSpecificDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = None
        fields = ['product', 'available', 'added']
        read_only_fields = ['added']

    def __init__(self, *args, **kwargs):
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
                product_id = data.get("product")
                product = Product.objects.get(id=product_id)
                model = product.get_product_specific_model()
        if model is not None and issubclass(model, ProductSpecific):
            self.Meta.model = model
            self.Meta.fields += self.Meta.model.attribute_field_names
            self.Meta.read_only_fields = self.Meta.fields
        elif model is not None:
            raise TypeError("Instance is not subclass of ProductSpecific")


class ProductSpecificListSerializer(serializers.ModelSerializer):

    class Meta:
        model = None
        fields = []

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
            self.Meta.fields = self.Meta.model.attribute_field_names + ['available']
            self.Meta.read_only_fields = self.Meta.fields

    # def create(self, validated_data):
    #     if self.Meta.model is None:
    #         product = validated_data.get('product', None)
    #     return super().create(validated_data)

    # def __new__(cls, *args, **kwargs):
    #     return super().__new__(cls, *args, **kwargs)

    def create(self, validated_data):
        raise NotImplementedError("Create not allowed with this serializer.")

    def update(self, instance, validated_data):
        raise NotImplementedError("Update not allowed with this serializer.")






