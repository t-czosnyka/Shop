# Generated by Django 4.2 on 2023-07-01 09:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0010_alter_productbackpack_unique_together_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='productbackpack',
            unique_together={('product', 'color', 'waterproof')},
        ),
    ]