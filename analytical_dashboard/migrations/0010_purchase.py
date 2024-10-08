# Generated by Django 5.0.3 on 2024-08-06 19:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analytical_dashboard', '0009_remove_supplier_payable_supplier_total_payable'),
    ]

    operations = [
        migrations.CreateModel(
            name='Purchase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('purchase_id', models.CharField(editable=False, max_length=50, unique=True)),
                ('date', models.DateField()),
                ('payment_type', models.CharField(choices=[('cash', 'Cash'), ('online', 'Online'), ('cheque', 'Cheque')], max_length=50)),
                ('reference', models.CharField(blank=True, max_length=255, null=True)),
                ('product_name', models.CharField(max_length=255)),
                ('product_brand', models.CharField(max_length=255)),
                ('rate', models.DecimalField(decimal_places=2, max_digits=10)),
                ('quantity', models.IntegerField()),
                ('discount', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('amount', models.DecimalField(decimal_places=2, editable=False, max_digits=10)),
                ('total', models.DecimalField(decimal_places=2, editable=False, max_digits=10)),
                ('supplier_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='analytical_dashboard.supplier')),
            ],
        ),
    ]
