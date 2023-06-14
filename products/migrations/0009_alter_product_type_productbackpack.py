# Generated by Django 4.2 on 2023-06-14 12:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0008_productshirt_stripe_price_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='type',
            field=models.CharField(choices=[('1', 'Shoe'), ('2', 'Suit'), ('3', 'Shirt'), ('4', 'Backpack')], max_length=3),
        ),
        migrations.CreateModel(
            name='ProductBackpack',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('available', models.BooleanField()),
                ('added', models.DateTimeField(auto_now_add=True)),
                ('stripe_product_id', models.CharField(blank=True, max_length=220, null=True)),
                ('stripe_price_id', models.CharField(blank=True, max_length=220, null=True)),
                ('color', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='products.color')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.product')),
            ],
            options={
                'unique_together': {('product', 'color')},
            },
        ),
    ]