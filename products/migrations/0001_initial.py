# Generated by Django 4.2 on 2023-05-02 16:21

from django.db import migrations, models
import django.db.models.deletion
import products.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Color',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Producer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('address', models.CharField(max_length=50)),
                ('city', models.CharField(max_length=50)),
                ('phone_number', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('description', models.TextField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('added', models.DateTimeField(auto_now_add=True)),
                ('type', models.CharField(choices=[('1', 'Shoe'), ('2', 'Suit'), ('3', 'Shirt')], max_length=3)),
                ('promoted', models.BooleanField(default=False)),
                ('producer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.producer')),
            ],
        ),
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('img', models.ImageField(upload_to=products.models.get_image_path)),
                ('thumbnail', models.ImageField(upload_to=products.models.get_thumbnail_path)),
                ('description', models.TextField()),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='products.product')),
            ],
        ),
        migrations.CreateModel(
            name='ProductSuit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('available', models.BooleanField()),
                ('added', models.DateTimeField(auto_now_add=True)),
                ('height_cm', models.DecimalField(decimal_places=0, max_digits=3)),
                ('chest_cm', models.DecimalField(decimal_places=0, max_digits=3)),
                ('waist_cm', models.DecimalField(decimal_places=0, max_digits=3)),
                ('color', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='products.color')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.product')),
            ],
            options={
                'unique_together': {('product', 'height_cm', 'chest_cm', 'waist_cm', 'color')},
            },
        ),
        migrations.CreateModel(
            name='ProductShoe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('available', models.BooleanField()),
                ('added', models.DateTimeField(auto_now_add=True)),
                ('size', models.DecimalField(decimal_places=0, max_digits=2)),
                ('color', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='products.color')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.product')),
            ],
            options={
                'unique_together': {('product', 'size', 'color')},
            },
        ),
        migrations.CreateModel(
            name='ProductShirt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('available', models.BooleanField()),
                ('added', models.DateTimeField(auto_now_add=True)),
                ('height_cm', models.DecimalField(decimal_places=0, max_digits=3)),
                ('collar_cm', models.DecimalField(decimal_places=0, max_digits=3)),
                ('color', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='products.color')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.product')),
            ],
            options={
                'unique_together': {('product', 'height_cm', 'collar_cm', 'color')},
            },
        ),
        migrations.CreateModel(
            name='ProductMainImage',
            fields=[
                ('product', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='main_img', serialize=False, to='products.product')),
                ('main_img', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='products.productimage')),
            ],
        ),
    ]
