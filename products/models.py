from django.db import models
from django.core.exceptions import ValidationError
import os

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


class ProductSpecific(models.Model):
    # Abstract class for specific product models with different attributes,
    # Product.type must match specififc model TYPE, allows different variants certain product
    TYPE = None

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    available = models.BooleanField()
    added = models.DateTimeField(auto_now_add=True)

    class Meta:

        abstract = True

    def validate_type(self):
        # function validates if specific product type refers to correct general product
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


class Color(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name


class ProductShoe(ProductSpecific):
    # Product type
    TYPE = '1'

    size = models.DecimalField(max_digits=2, decimal_places=0)
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True)

    class Meta:
        unique_together = ('product', 'size', 'color')

    def __str__(self):
        return f"{self.product.name} Color: {self.color}, Size: {self.size}"


class ProductSuit(ProductSpecific):
    # Product type
    TYPE = '2'

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

    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True)
    height_cm = models.DecimalField(max_digits=3, decimal_places=0)
    collar_cm = models.DecimalField(max_digits=3, decimal_places=0)

    class Meta:
        unique_together = ('product', 'height_cm', 'collar_cm', 'color')

    def __str__(self):
        return f"{self.product.name} Color: {self.color}, Size: {self.height_cm}, {self.collar_cm}"

def get_image_path(instance, filename):
    type = instance.product.get_type_display()
    return os.path.join('images', type, f"{str(instance.product.id)}")


class ProductImage(models.Model):

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    img = models.ImageField(upload_to=get_image_path)
    description = models.TextField()
    #Image is main image to represent product - only one possible
    main = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.product.name} {self.id}"

    def check_main(self):
        # check if other ProductImage refering the same Product is not already set as main
        if self.main == True:
            qs = ProductImage.objects.filter(product=self.product, main=True).first()
            if qs is not None and qs != self:
                raise ValidationError({'main': ValidationError("Only one main image per Product possible.")})

    def clean(self):
        super().clean()
        self.check_main()

    def save(self, **kwargs):
        self.check_main()
        super().save(**kwargs)
        img_path = str(self.img)
        head, tail = os.path.split(img_path)
        new_img_path = os.path.join(head,f"{self.product.id}_{self.id}")
        os.rename(img_path, new_img_path)
        self.img = new_img_path
        super().save(**kwargs)



















