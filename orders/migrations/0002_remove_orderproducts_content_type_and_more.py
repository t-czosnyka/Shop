# Generated by Django 4.2 on 2023-05-11 15:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderproducts',
            name='content_type',
        ),
        migrations.RemoveField(
            model_name='orderproducts',
            name='object_id',
        ),
    ]
