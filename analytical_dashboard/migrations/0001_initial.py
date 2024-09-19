# Generated by Django 5.0.3 on 2024-07-13 14:06

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_name', models.CharField(max_length=50)),
                ('contact', models.CharField(max_length=20)),
                ('address', models.CharField(blank=True, max_length=50, null=True)),
                ('city', models.CharField(blank=True, max_length=50, null=True)),
                ('nic', models.CharField(blank=True, max_length=20, null=True)),
                ('reference', models.CharField(blank=True, max_length=50, null=True)),
                ('credit_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=50, null=True)),
                ('credit_limit', models.DecimalField(blank=True, decimal_places=2, max_digits=50, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_name', models.CharField(default='Product Name', max_length=255)),
                ('brand', models.CharField(max_length=255, null=True)),
                ('category', models.CharField(blank=True, max_length=10)),
                ('quantity', models.IntegerField(null=True)),
                ('purchase_price', models.DecimalField(decimal_places=2, max_digits=20, null=True)),
                ('retail_price', models.DecimalField(decimal_places=2, max_digits=20, null=True)),
                ('date', models.DateField(default=django.utils.timezone.now, null=True)),
                ('purchase_variation', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('retail_variation', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('rate_per_bag', models.DecimalField(decimal_places=2, max_digits=20, null=True)),
                ('rate_per_ton', models.DecimalField(decimal_places=2, max_digits=20, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='PriceHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('old_purchase_price', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('new_purchase_price', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('purchase_variation', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('old_retail_price', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('new_retail_price', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('retail_variation', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('change_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='analytical_dashboard.product')),
            ],
        ),
        migrations.CreateModel(
            name='Sales',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('invoice_number', models.CharField(blank=True, max_length=255, unique=True)),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('customer_name', models.CharField(blank=True, max_length=255, null=True)),
                ('customer_contact', models.CharField(blank=True, max_length=20, null=True)),
                ('product_name', models.CharField(editable=False, max_length=255)),
                ('quantity', models.IntegerField()),
                ('unit', models.CharField(choices=[('bag', 'Bag'), ('ton', 'Ton')], max_length=10)),
                ('rate', models.DecimalField(decimal_places=2, max_digits=20)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=20)),
                ('payment_type', models.CharField(choices=[('cash', 'Cash'), ('credit card', 'Credit Card'), ('paypal', 'PayPal')], max_length=20)),
                ('due_balance', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=20, null=True)),
                ('subtotal', models.DecimalField(decimal_places=2, max_digits=10)),
                ('total', models.DecimalField(decimal_places=2, max_digits=10)),
                ('paid', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('discount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='analytical_dashboard.customer')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='analytical_dashboard.product')),
            ],
        ),
    ]
