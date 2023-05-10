import functools
import operator
from django.db import models
from django.core.exceptions import ValidationError
import os
import pathlib
from PIL import Image
from django.db.models import Q
from django.conf import settings
from django.shortcuts import get_object_or_404

# Create your models here.

# Available product types
PRODUCT_TYPES = {'1': 'Shoe',
                 '2': 'Suit',
                 '3': 'Shirt'}


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

    name = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    producer = models.ForeignKey(Producer, on_delete=models.CASCADE)
    added = models.DateTimeField(auto_now_add=True)
    type = models.CharField(choices=TYPE_CHOICES, max_length=3)
    promoted = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def assign_main_img(self):
        # assigns main_img_short attribute to Product object from ProductMainImage if present or first available image
        if self.main_img is not None and self.main_img.main_img is not None:
            self.main_img_short = ProductImage.objects.get(id=self.main_img.main_img.id)
        else:
            self.main_img_short = ProductImage.objects.filter(product=self).first()

    def get_filtered_product_specific_attributes(self, query_dict):
        # method returns dictionary with attributes of ProductSpecific objects referring this Product and
        # available values of these attributes. Keys are attribute names and values are list of dicts containing:
        # actual value, how value ist displayed in form, and information if it was selected in query_dict.
        # e.g.
        # product_specific_attributes = {'size': [
        #                                           {value:'42', display:'42', selected = False}
        #                                           {value:'43', display:'43', selected = True}
        #                                         ],
        #                               'color':[
        #                                           {value:'1', display:'Black', selected = False}
        #                                           {value:'2', display:'White', selected = False}
        #                                        ]}
        #
        product_specific_attributes = {}
        # get Product specific model referring to this product based on Product.type - ProductSpecific model must
        # match the naming pattern: "ProductType"
        product_specific_model = globals().get(f"Product{self.get_type_display()}", None)
        # return empty dict if product specific model is not found
        if product_specific_model is None:
            return product_specific_attributes
        # Filter ProductSpecific objects matching query dict
        filtered_products_specific = self.get_filtered_product_specific(query_dict)
        if len(filtered_products_specific) == 0:
            return product_specific_attributes
        # Create dict based on result of filtering product_specific
        used_values = {}
        attribute_field_names = product_specific_model.get_attribute_field_names()
        # prepare keys of result dict
        for attribute in attribute_field_names:
            product_specific_attributes[attribute] = []
            # keep track of added values to remove duplicates
            used_values[attribute] = set()
        # get attribute field objects of ProductSpecific class
        attribute_field_objects = product_specific_model.get_attribute_field_objects()
        # add values of all fields to result dict for every product
        for product_specific in filtered_products_specific:
            for field in attribute_field_objects:
                value = field.value_to_string(product_specific)
                # If field is a Foreign key field get object display
                if isinstance(field, models.ForeignKey):
                    display = getattr(product_specific, f'{field.name}')
                else:
                    display = value
                if value not in used_values[field.name]:
                    used_values[field.name].add(value)
                    selected = query_dict.get(field.name, False) == value
                    product_specific_attributes[field.name].append({'value': value, 'display': display,
                                                                    'selected': selected})
        return product_specific_attributes

    def get_filtered_product_specific(self, query_dict):
        # Returns QuerySet of ProductSpecific objects matching arguments passed in query_dict
        product_specific_model = globals().get(f"Product{self.get_type_display()}", False)
        attribute_field_names = product_specific_model.get_attribute_field_names()
        # Create list of queries initialized with
        q_list = [Q(product=self.id), Q(available=True)]
        # Append queries from query_dict to q_list
        for key, val in query_dict.items():
            if key in attribute_field_names and val:
                q_list.append(Q(**{f"{key}": val}))
        # filter ProductSpecific objects with queries from q_list
        try:
            filtered = product_specific_model.objects.filter(functools.reduce(operator.and_, q_list))
        except (ValidationError, ValueError):
            filtered = {}
        return filtered

    def get_product_specific_by_attributes(self, query_dict):
        # returns ProductSpecific based on query_dict passed in GET request
        # if there are more products specific or some value is missing, returns empty dict
        # check if all values are not empty
        for key, val in query_dict.items():
            if not val:
                return None
        # filter products with passed query_dict
        filtered = self.get_filtered_product_specific(query_dict)
        # if only one result is available return ProductSpecific object
        if len(filtered) == 1:
            return filtered.first()
        else:
            return None

    @classmethod
    def get_product_specific(cls, product_id, product_specific_id):
        # Returns ProductSpecific object, with product_specific_id, referring Product object indicated by product_id.
        prod = get_object_or_404(cls, id=product_id)
        if prod is not None:
            return prod.get_product_specific_by_id(product_specific_id)

    def get_product_specific_by_id(self, product_specific_id):
        product_specific_model = globals().get(f"Product{self.get_type_display()}", None)
        return get_object_or_404(product_specific_model, product=self, id=product_specific_id)


class ProductSpecific(models.Model):
    # Abstract class for specific product models with different attributes,
    # Product.type must match specific model TYPE, allows different variants certain product
    TYPE = None
    attribute_field_names = []
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

    @classmethod
    def get_attribute_field_objects(cls):
        attribute_field_objects = []
        for field in cls._meta.get_fields():
            if field.name in cls.attribute_field_names:
                attribute_field_objects.append(field)
        return attribute_field_objects

    @classmethod
    def get_attribute_field_names(cls):
        return cls.attribute_field_names

    def get_full_id(self):
        # return tuple containing referred general Product.id,ProductSpecific.id
        return f"{self.product.id}_{self.id}"


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
