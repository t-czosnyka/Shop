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

# Create your models here.

# Available product types
PRODUCT_TYPES = {'1': 'Shoe',
                 '2': 'Suit',
                 '3': 'Shirt'}

PRODUCT_TYPES_PLURALS = {'1': 'Shoes',
                         '2': 'Suits',
                         '3': 'Shirts'}


class Producer(models.Model):
    name = models.CharField(max_length=50, unique=True)
    address = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Product(models.Model):
    # General product model with common attributes for all products
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
        filtered_products_specific = self.product_specific_model.filter_objects_with_query_dict(query_dict, self)
        return self.get_product_specific_attributes(filtered_products_specific, query_dict)

    @staticmethod
    def get_product_specific_attributes(query_set, query_dict):
        # Method returns values of attributes of all products in query_set in the form of :
        # all_attributes = {'size': [
        #                            {value:'42', display:'42', selected = False}
        #                            {value:'43', display:'43', selected = True}
        #                           ],
        #                   'color':[
        #                            {value:'1', display:'Black', selected = False}
        #                            {value:'2', display:'White', selected = False}
        #                           ]}
        all_attributes = {}
        used_values = {}
        for product_specific in query_set:
            single_object_attributes = product_specific.get_object_attribute_values()
            for attribute in single_object_attributes.keys():
                # check if attribute value is not already added
                value = single_object_attributes[attribute]['value']
                used_values_set = used_values.get(attribute, set())
                if value in used_values_set:
                    continue
                # mark value as selected if it is in query dict
                single_object_attributes[attribute]['selected'] = query_dict.get(attribute, False) == value
                # format attribute name string
                attribute_name = attribute.capitalize().replace('_',' ')
                all_attributes[attribute_name] = all_attributes.get(attribute, []) + [single_object_attributes[attribute]]
                used_values[attribute] = used_values_set.union({value})
        return all_attributes

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
        filtered = self.product_specific_model.filter_objects_with_query_dict(query_dict, self)
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

    def get_product_specific_model(self):
        type_name = PRODUCT_TYPES.get(self.type, '').lower()
        if type_name == '':
            return None
        product_specific_set_name = f"product{type_name}_set"
        return getattr(self, product_specific_set_name).model

    def update_rating(self):
        calculated_avg = self.ratings.all().aggregate(Avg('value')).get('value__avg', None)
        if calculated_avg is None:
            calculated_avg= 0
        self.avg_rating = calculated_avg

    @property
    def number_of_ratings(self):
        return self.ratings.count()

    @property
    def rating_percentage(self):
        return self.avg_rating/5*100


class ProductSpecific(models.Model):
    # Abstract class for specific product models with different attributes,
    # Product.type must match specific model TYPE, allows different variants certain product
    TYPE = None
    attribute_field_names = []
    not_attribute_field_names = ['product', 'available', 'added', 'id']
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    available = models.BooleanField()
    added = models.DateTimeField(auto_now_add=True)

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
        super().save(**kwargs)

    def get_full_id(self):
        # return tuple containing referred general Product.id,ProductSpecific.id
        return f"{self.product.id}_{self.id}"

    @property
    def url_specific(self):
        url = reverse('products:detail', kwargs={'pk': self.product.id})+'?'
        for attribute in self.attribute_field_names:
            value = self._meta.get_field(attribute).value_to_string(self)
            url += f'&{attribute}={value}'
        return url

    def get_object_attribute_values(self):
        attribute_values = {}
        for attribute in self.attribute_field_names:
            value = self._meta.get_field(attribute).value_to_string(self)
            display = getattr(self, f'{attribute}')
            attribute_values[attribute] = {'value': value, 'display': display, 'selected': False}
        return attribute_values

    @classmethod
    def filter_objects_with_query_dict(cls, query_dict, product):
        # Returns QuerySet of ProductSpecific objects matching arguments passed in query_dict
        # Initialize list of queries
        query_list = [Q(product=product), Q(available=True)]
        # Append queries from query_dict to query_list
        for attribute in cls.attribute_field_names:
            val = query_dict.get(attribute, False)
            if val:
                query_list.append(Q(**{f"{attribute}": val}))
        # filter ProductSpecific objects with queries from query_list
        try:
            filtered = cls.objects.filter(functools.reduce(operator.and_, query_list))
        except (ValidationError, ValueError) as e:
            filtered = {}
        return filtered


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
    size = models.DecimalField(max_digits=2, decimal_places=0)
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True)

    class Meta:
        unique_together = ('product', 'size', 'color')

    def __str__(self):
        return f"{self.product.name} Color: {self.color}, Size: {self.size}"


class ProductSuit(ProductSpecific):
    # Product type
    TYPE = '2'
    attribute_field_names = ['height_cm', 'chest_cm', 'waist_cm', 'color']
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


