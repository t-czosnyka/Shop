import functools
import operator
from django.db import models
from django.core.exceptions import ValidationError
import os
import pathlib
from PIL import Image
from django.db.models import Q, Avg
from django.conf import settings
from django.shortcuts import get_object_or_404, reverse
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator
import stripe
# Create your models here.

# Available product types
PRODUCT_TYPES = {'1': 'Shoe',
                 '2': 'Suit',
                 '3': 'Shirt'}

stripe.api_key = settings.STRIPE_SECRET_KEY


def get_product_specific_model(product_type):
    # Returns ProductSpecific class model based on product_type.
    type_name = PRODUCT_TYPES.get(str(product_type), '')
    if not type_name:
        return None
    model_name = "Product"+type_name
    return globals().get(model_name, None)


class Producer(models.Model):
    name = models.CharField(max_length=50, unique=True)
    address = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Product(models.Model):
    # General product model with common attributes for all products.
    TYPE_CHOICES = [(x, y) for x, y in PRODUCT_TYPES.items()]
    product_specific_model = None

    name = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    producer = models.ForeignKey(Producer, on_delete=models.CASCADE)
    added = models.DateTimeField(auto_now_add=True)
    type = models.CharField(choices=TYPE_CHOICES, max_length=3)
    promoted = models.BooleanField(default=False)
    avg_rating = models.DecimalField(max_digits=2, decimal_places=1, default=0)
    discount = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(100)])

    def __str__(self):
        return self.name

    @property
    def main_image_object(self):
        # Return main image object if assigned or first available image.
        if self.main_img.main_img is not None:
            return self.main_img.main_img
        return self.images.first()

    def get_filtered_product_specific_attributes(self, query_dict):
        # Method filters ProductSpecific objects referencing this Product with parameters from query_dict
        # and returns values of these objects attributes.
        if self.product_specific_model is None:
            return {}
        filtered_products_specific = self.product_specific_model.filter_with_query_dict(query_dict, self)
        return self.product_specific_model.get_attrs_values(filtered_products_specific, product=self)

    def get_product_specific_by_attributes(self, query_dict):
        # returns ProductSpecific object based on query_dict passed in GET request
        # if there are more products specific or some value is missing, returns empty dict
        if self.product_specific_model is None:
            return None
        product_specific_object = None
        # check if all queries are not empty
        for val in query_dict.values():
            if not val:
                return None
        # filter products with passed query_dict
        filtered = self.product_specific_model.filter_with_query_dict(query_dict, self)
        # if only one result is available return ProductSpecific object
        if len(filtered) == 1:
            product_specific_object = filtered.first()
        return product_specific_object

    @classmethod
    def get_product_specific(cls, product_id, product_specific_id):
        # Returns ProductSpecific object, with product_specific_id, referring Product object indicated by product_id.
        prod = get_object_or_404(cls, id=product_id)
        if prod is not None:
            return prod.get_product_specific_by_id(product_specific_id)

    def get_product_specific_by_id(self, product_specific_id):
        return get_object_or_404(self.product_specific_model, product=self, id=product_specific_id)

    def get_product_specific_set(self):
        type_name = PRODUCT_TYPES.get(self.type, '').lower()
        if type_name == '':
            return None
        product_specific_set_name = f"product{type_name}_set"
        return getattr(self, product_specific_set_name).all()

    def get_product_specific_model(self):
        product_specific_set = self.get_product_specific_set()
        if product_specific_set is not None:
            return product_specific_set.model
        else:
            return None

    def update_rating(self):
        calculated_avg = self.ratings.all().aggregate(Avg('value')).get('value__avg', None)
        if calculated_avg is None:
            calculated_avg = 0
        self.avg_rating = calculated_avg

    @property
    def number_of_ratings(self):
        return self.ratings.count()

    @property
    def rating_percentage(self):
        return self.avg_rating/5*100

    @property
    def current_price(self):
        # Calculate price after discount.
        return round(self.price * (100-self.discount)/100, 2)

    def save(self, **kwargs):
        super().save(**kwargs)
        # Update stripe prices of product specific
        product_specific_set = self.get_product_specific_set()
        if product_specific_set is not None:
            for product_specific in product_specific_set:
                product_specific.update_stripe_price()
                product_specific.save()

    def get_absolute_url(self):
        return reverse('products:detail', kwargs={"pk": self.pk})


class ProductSpecific(models.Model):
    # Abstract class for specific product models with different attributes.
    # Product.type must match specific model TYPE, allows different variants certain product.
    TYPE = None
    # attribute_field_names - unique attributes for this type of product.
    attribute_field_names = []
    # List of how each unique attribute should be queried.
    attrs = []
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    available = models.BooleanField()
    added = models.DateTimeField(auto_now_add=True)

    stripe_product_id = models.CharField(max_length=220, null=True, blank=True)
    stripe_price_id = models.CharField(max_length=220, null=True, blank=True)

    class Meta:
        abstract = True

    def validate_type(self):
        # function validates if specific product refers to correct general product of correct type
        if self.product.type != self.TYPE:
            raise ValidationError({
                'product': ValidationError(f" {self.product.get_type_display()} is wrong product type for"
                                           f" {PRODUCT_TYPES[self.TYPE]} table.", code='invalid')
            })

    def clean_fields(self, exclude=None):
        # validate if product foreign key refers correct Product.type
        super().clean_fields(exclude=exclude)
        self.validate_type()

    def save(self, **kwargs):
        self.validate_type()
        stripe_product_object = stripe.Product.create(name=str(self))
        self.stripe_product_id = stripe_product_object.stripe_id
        self.update_stripe_price()
        super().save(**kwargs)

    def update_stripe_price(self):
        if self.stripe_product_id is not None:
            stripe_price_object = stripe.Price.create(currency="pln", product=self.stripe_product_id,
                                                      unit_amount=int(self.product.current_price*100))
            self.stripe_price_id = stripe_price_object.stripe_id

    def get_full_id(self):
        # return tuple containing referred general Product.id,ProductSpecific.id
        return f"{self.product.id}_{self.id}"

    def get_absolute_url(self):
        # Return url to ProductSpecific object.
        url = self.product.get_absolute_url()+'?'
        model = type(self)
        values = model.objects.filter(id=self.id).values(*self.attrs)
        for key, value in values.first().items():
            url += f'&{key}={value}'
        return url

    @classmethod
    def filter_with_query_dict(cls, query_dict, product=None):
        # Returns QuerySet of ProductSpecific objects with attributes matching those passed in query_dict. If product
        # is passed only ProductSpecific object referring this product will be included.
        # Initialize list of queries
        query_list = [Q(available=True)]
        if product is not None:
            query_list.append(Q(product=product))
        # Append queries from query_dict to query_list. Queries for the same attribute are connected with OR operator.
        for attribute in cls.attrs:
            attribute_query_list = []
            values = query_dict.getlist(attribute, [])
            for val in values:
                if val:
                    attribute_query_list.append(Q(**{f"{attribute}": val}))
            if len(attribute_query_list):
                query_list.append(functools.reduce(operator.or_, attribute_query_list))
        # filter ProductSpecific objects with queries from query_list
        try:
            filtered = cls.objects.filter(functools.reduce(operator.and_, query_list))
        except (ValidationError, ValueError):
            # Wrong filtering parameters - return empty queryset.
            filtered = cls.objects.none()
        return filtered

    @classmethod
    def get_attrs_values(cls, query_set=None, product=None):
        # Returns dictionary of attribute values for products in query_set if query_set is provided or all products of
        # this class.
        if query_set is None:
            query_set = cls.objects.all()
        if product is not None:
            query_set = query_set.filter(product=product)
        # Get values as separate dictionaries for each object.
        values = query_set.values(*cls.attrs)
        combined = {}
        # Combine dictionary values. Use set to avoid duplicates.
        for value_dict in values:
            for key, value in value_dict.items():
                combined[key] = combined.get(key, set()).union([value])
        # Cast set to list and sort values.
        for key, values in combined.items():
            combined[key] = sorted(list(values))
        return combined

    @classmethod
    def get_attrs_names(cls):
        # Return dictionary with attrs and their corresponding names.
        return {key: value for key, value in zip(cls.attrs, cls.attribute_field_names)}


class Color(models.Model):
    # Table containing product colors.
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name

# Classes inheriting from ProductSpecific must match naming pattern Product<Product.type>


class ProductShoe(ProductSpecific):
    # ProductSpecific Shoe class
    # Product type
    TYPE = '1'
    # attribute_field_names - unique attributes for this type of product
    attribute_field_names = ['size', 'color']
    # List of how each unique attribute should be queried.
    attrs = ['size', 'color__name']
    size = models.DecimalField(max_digits=2, decimal_places=0)
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True)

    class Meta:
        unique_together = ('product', 'size', 'color')

    def __str__(self):
        return f"{self.product.name} Color: {self.color}, Size: {self.size}"


class ProductSuit(ProductSpecific):
    TYPE = '2'
    attribute_field_names = ['height_cm', 'chest_cm', 'waist_cm', 'color']
    attrs = ['height_cm', 'chest_cm', 'waist_cm', 'color__name']
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True)
    height_cm = models.DecimalField(max_digits=3, decimal_places=0)
    chest_cm = models.DecimalField(max_digits=3, decimal_places=0)
    waist_cm = models.DecimalField(max_digits=3, decimal_places=0)

    def __str__(self):
        return f"{self.product.name} Color: {self.color}, Size: {self.height_cm}, {self.chest_cm}, {self.waist_cm}"

    class Meta:
        unique_together = ('product', 'height_cm', 'chest_cm', 'waist_cm', 'color')


class ProductShirt(ProductSpecific):
    TYPE = '3'
    attribute_field_names = ['height_cm', 'collar_cm', 'color']
    attrs = ['height_cm', 'collar_cm', 'color__name']
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True)
    height_cm = models.DecimalField(max_digits=3, decimal_places=0)
    collar_cm = models.DecimalField(max_digits=3, decimal_places=0)

    class Meta:
        unique_together = ('product', 'height_cm', 'collar_cm', 'color')

    def __str__(self):
        return f"{self.product.name} Color: {self.color}, Size: {self.height_cm}, {self.collar_cm}"


def get_image_path(instance, filename):
    product_type = instance.product.get_type_display()
    file_extension = pathlib.Path(filename).suffix
    return os.path.join('images', product_type, f"{str(instance.product.id)}{file_extension}")


def get_thumbnail_path(instance, filename):
    product_type = instance.product.get_type_display()
    file_extension = pathlib.Path(filename).suffix
    return os.path.join('images', product_type, f"{str(instance.product.id)}_thumbnail{file_extension}")


class ProductImage(models.Model):
    # Table containing images and their thumbnails r
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    img = models.ImageField(upload_to=get_image_path)
    thumbnail = models.ImageField(upload_to=get_thumbnail_path)
    description = models.TextField()

    def __str__(self):
        return f"{self.product.id}-{self.product.name} {self.id}"

    def save(self, **kwargs):
        super().save(**kwargs)
        # Rename image file as "{Product.id}_{ProductImage.id}",
        # ProductImage.id available only after saving to DB
        img_path = str(self.img)
        print(img_path)
        file_extension = pathlib.Path(img_path).suffix
        head, tail = os.path.split(img_path)
        new_img_path = os.path.join(head, f"{self.product.id}_{self.id}{file_extension}")
        os.rename(os.path.join(settings.MEDIA_ROOT, img_path), os.path.join(settings.MEDIA_ROOT, new_img_path))
        self.img = new_img_path

        # Resize uploaded image and save
        image = Image.open(self.img)
        image.thumbnail((600, 600))
        image.save(os.path.join(settings.MEDIA_ROOT, new_img_path))
        # Create a thumbnail from uploaded image and assign it to thumbnail field
        image.thumbnail((100, 100))
        thumbnail_path = os.path.join(head, f"{self.product.id}_{self.id}_thumbnail{file_extension}")
        image.save(os.path.join(settings.MEDIA_ROOT, thumbnail_path))
        self.thumbnail = thumbnail_path
        super().save(**kwargs)


class ProductMainImage(models.Model):
    # junction table linking Product model to ProductImage model to set it as main image
    product = models.OneToOneField(Product, on_delete=models.CASCADE, primary_key=True, related_name='main_img')
    main_img = models.OneToOneField(ProductImage, on_delete=models.SET_NULL, null=True)

    def check_relation(self):
        #  checking if ProductImage refers to correct Product
        if self.main_img is not None and self.main_img.product != self.product:
            raise ValidationError("Selected ProductImage does not belong to this Product.")

    def clean(self):
        self.check_relation()
        super().clean()

    def save(self, **kwargs):
        self.check_relation()
        super().save(**kwargs)

    def __str__(self):
        img = ''
        if self.main_img is not None:
            img = self.main_img.id
        return f"{self.product.name}-{self.product.id} Main image:{img}"


class Rating(models.Model):
    VALUE_CHOICES = [(1, "1"), (2, "2"), (3, "3"), (4, "4"), (5, "5")]
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='ratings')
    value = models.IntegerField(choices=VALUE_CHOICES)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Product: {self.product}, User: {self.user}, value: {self.value}"

    class Meta:
        unique_together = ('product', 'user')

    @property
    def value_percentage(self):
        return self.value * 20
