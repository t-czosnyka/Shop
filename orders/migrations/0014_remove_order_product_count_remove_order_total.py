# Generated by Django 4.2 on 2023-05-21 11:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0013_alter_order_product_count'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='product_count',
        ),
        migrations.RemoveField(
            model_name='order',
            name='total',
        ),
    ]
