import functools
import operator
from django.db import models
from django.core.exceptions import ValidationError
import os, pathlib
from PIL import Image
from django.db.models import Q

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
        # assigns main_img_short attribute to Product object from ProducMainImage if present or first available image
        if self.main_img is not None and self.main_img.main_img is not None:
            self.main_img_short= ProductImage.objects.get(id = self.main_img.main_img.id)
        else:
            self.main_img_short= ProductImage.objects.filter(product=self).first()

    def get_specific_product_attributes(self, query_dict):
        # function returns dictionary with specific product attributes and available values of this attributes based
        # on ProductSpecific objects referring to this Product object e.g. {'size': [42,43], 'color':['Black','White']}
        attributes = {}
        # Get queryset of specific products referring this Product class
        variants = self.__getattribute__(f"product{self.get_type_display().lower()}_set")
        variant_object = variants.first()
        variant_field_names = variant_object.get_variant_field_names()
        # Return empty dict if there are no ProductSpecific objects referring to this Product object
        if len(variants.all()) == 0:
            return attributes
        # Filter ProductSpecific objects matching query dict
        filtered = self.get_specific_products(query_dict)
        used_values = {}
        for field_name in variant_field_names:
            attributes[field_name] = []
            used_values[field_name] = set()
        variant_field_objects = variant_object.get_variant_field_objects()
        for variant in filtered:
            for field in variant_field_objects:
                # Check if field object is a Foreign Key
                value = field.value_to_string(variant)
                if isinstance(field, models.ForeignKey):
                    display = getattr(variant, f'{field.name}')
                else:
                    display = field.value_to_string(variant)
                if value not in used_values[field.name]:
                    used_values[field.name].add(value)
                    attributes[field.name].append({'value': value, 'display': display})
        return attributes

    def get_specific_products(self, query_dict):
        # Returns QuerySet of products with matching attributes
        # Create list of queries
        variants = self.__getattribute__(f"product{self.get_type_display().lower()}_set")
        variant_object = variants.first()
        variant_field_names = variant_object.get_variant_field_names()
        q_list = [Q(product=self.id), Q(available=True)]
        # Append queries from query_dict to q_List
        for key, val in query_dict.items():
            if key in variant_field_names and val:
                q_list.append(Q(**{f"{key}": val}))
        # filter Product with passed queries
        try:
            filtered = variants.filter(functools.reduce(operator.and_, q_list))
        except ValueError as e:
            return {}
        else:
            return filtered

    def add_to_cart(self, query_dict):
        # check if all values are not empty
        for key, val in query_dict.items():
            if not val:
                print("empty values")
                return {}
        filtered = self.get_specific_products(query_dict)
        if len(filtered) == 1:
            return filtered.first()
        else:
            return {}


class ProductSpecific(models.Model):
    # Abstract class for specific product models with different attributes,
    # Product.type must match specififc model TYPE, allows different variants certain product
    TYPE = None
    variant_field_names = []

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

    def save(self,**kwargs):
        self.validate_type()
        super().save(**kwargs)

    def get_variant_field_objects(self):
        variant_field_objects = []
        for field in self._meta.get_fields():
            if field.name in self.variant_field_names:
                variant_field_objects.append(field)
        return variant_field_objects

    @classmethod
    def get_variant_field_names(cls):
        return cls.variant_field_names


class Color(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name


class ProductShoe(ProductSpecific):
    # Product type
    TYPE = '1'
    variant_field_names = ['size', 'color']
    size = models.DecimalField(max_digits=2, decimal_places=0)
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True)

    class Meta:
        unique_together = ('product', 'size', 'color')

    def __str__(self):
        return f"{self.product.name} Color: {self.color}, Size: {self.size}"


class ProductSuit(ProductSpecific):
    # Product type
    TYPE = '2'
    variant_field_names = ['height_cm', 'chest_cm', 'waist_cm', 'color']
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
    variant_field_names = ['height_cm', 'collar_cm', 'color']
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True)
    height_cm = models.DecimalField(max_digits=3, decimal_places=0)
    collar_cm = models.DecimalField(max_digits=3, decimal_places=0)

    class Meta:
        unique_together = ('product', 'height_cm', 'collar_cm', 'color')

    def __str__(self):
        return f"{self.product.name} Color: {self.color}, Size: {self.height_cm}, {self.collar_cm}"

def get_image_path(instance, filename):
    type = instance.product.get_type_display()
    file_extension = pathlib.Path(filename).suffix
    return os.path.join('images', type, f"{str(instance.product.id)}{file_extension}")

def get_thumbnail_path(instance, filename):
    type = instance.product.get_type_display()
    file_extension = pathlib.Path(filename).suffix
    return os.path.join('images', type, f"{str(instance.product.id)}_thumbnail{file_extension}")


class ProductImage(models.Model):

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
        file_extension = pathlib.Path(img_path).suffix
        head, tail = os.path.split(img_path)
        new_img_path = os.path.join(head,f"{self.product.id}_{self.id}{file_extension}")
        os.rename(img_path, new_img_path)
        self.img = new_img_path

        # Resize uploaded image and save
        image = Image.open(self.img)
        image.thumbnail((600, 600))
        image.save(new_img_path)
        # Create a thumbnail from uploaded image and assign it to thumbnail field
        image.thumbnail((100, 100))
        thumbnail_path = os.path.join(head,f"{self.product.id}_{self.id}_thumbnail{file_extension}")
        image.save(thumbnail_path)
        self.thumbnail = thumbnail_path
        super().save(**kwargs)


class ProductMainImage(models.Model):
    # junction table linking product to its main image, checking if ProductImage refers to correct Product
    product = models.OneToOneField(Product, on_delete=models.CASCADE, primary_key=True, related_name='main_img')
    main_img = models.OneToOneField(ProductImage, on_delete=models.SET_NULL, null=True)

    def check_relation(self):
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
























