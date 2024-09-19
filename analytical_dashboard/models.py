# analytical_dashboard/models.py

from django.db import models
from django.utils import timezone
from decimal import Decimal
from django.db.models import Avg
from django.db.models.signals import pre_save
from django.dispatch import receiver
import uuid
from django.urls import reverse
from django.db.models import Sum

class Customer(models.Model):
    customer_name = models.CharField(max_length=50, null=False)
    contact = models.CharField(max_length=20, unique=True, null=False)
    address = models.CharField(max_length=50, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    nic = models.CharField(max_length=20, blank=True, null=True)
    reference = models.CharField(max_length=50, null=True, blank=True)
    credit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=False, blank=False)
    credit_limit = models.DecimalField(max_digits=50, decimal_places=2, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    payable_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def __str__(self):
        return self.customer_name
    
    def update_payable_amount(self):
        total_deposit = self.advances.aggregate(total=Sum('amount'))['total'] or 0
        self.payable_amount = total_deposit
        self.save()


class AdvanceDeposit(models.Model):
    PAYMENT_CHOICES = [
        ('cash', 'Cash'),
        ('online', 'Online Transfer'),
        ('cheque', 'Cheque Payable'),
    ]

    customer = models.ForeignKey(Customer, related_name='advances', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_type = models.CharField(max_length=10, choices=PAYMENT_CHOICES)
    date = models.DateTimeField(auto_now_add=True)
    def save(self, *args, **kwargs):
        # Update the customer’s total payable amount before saving
        if self.pk:  # If updating an existing record
            old_instance = AdvanceDeposit.objects.get(pk=self.pk)
            if old_instance.amount != self.amount:
                self.customer.update_payable_amount()
        else:  # If creating a new record
            super().save(*args, **kwargs)
            self.customer.update_payable_amount()
            return

        super().save(*args, **kwargs)
        self.customer.update_payable_amount()



class Product(models.Model):
    product_name = models.CharField(max_length=255, default='Product Name')
    brand = models.CharField(max_length=255, null=True, blank=False)
    category = models.CharField(max_length=10, null=False, blank=True)
    quantity = models.IntegerField(null=True)
    purchase_price = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    retail_price = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    date = models.DateField(default=timezone.now, null=True)
    purchase_variation = models.DecimalField(max_digits=20, decimal_places=2, default=0.00, null=False)
    retail_variation = models.DecimalField(max_digits=20, decimal_places=2, default=0.00, null=False)
    rate_per_bag = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    rate_per_ton = models.DecimalField(max_digits=20, decimal_places=2, null=True)

    @property
    def available_stock(self):
        # Example logic to calculate available stock, you can modify this as needed
        return self.quantity

    def __str__(self):
        return self.product_name

    def save(self, *args, **kwargs):
        if self.pk is not None:
            original = Product.objects.get(pk=self.pk)
            
            # Track purchase price changes
            if self.purchase_price is not None and original.purchase_price is not None:
                purchase_variation = Decimal(self.purchase_price) - Decimal(original.purchase_price)
                self.purchase_variation += purchase_variation
                PriceHistory.objects.create(
                    product=self,
                    old_purchase_price=original.purchase_price,
                    new_purchase_price=self.purchase_price,
                    purchase_variation=purchase_variation
                )
            
            # Track retail price changes
            if self.retail_price is not None and original.retail_price is not None:
                retail_variation = Decimal(self.retail_price) - Decimal(original.retail_price)
                self.retail_variation += retail_variation
                PriceHistory.objects.create(
                    product=self,
                    old_retail_price=original.retail_price,
                    new_retail_price=self.retail_price,
                    retail_variation=retail_variation
                )
        super(Product, self).save(*args, **kwargs)

    def average_purchase_price(self):
        purchase_prices = PriceHistory.objects.filter(product=self).values_list('new_purchase_price', flat=True)
        valid_prices = [price for price in purchase_prices if price is not None]
        if valid_prices:
            return sum(valid_prices) / len(valid_prices)
        return Decimal('0.00')
    
    def get_rate(self, unit):
        if unit == 'bag':
            return self.rate_per_bag
        elif unit == 'ton':
            return self.rate_per_ton
        else:
            raise ValueError('Invalid unit')

    def get_available_quantity(self, unit):
        if unit == 'bag':
            return self.quantity
        elif unit == 'ton':
            return self.quantity // 20
        else:
            raise ValueError('Invalid unit')

    def reduce_stock(self, quantity, unit):
        if unit == 'bag':
            self.quantity -= quantity
        elif unit == 'ton':
            self.quantity -= quantity * 20

        # Ensure quantity does not become negative
        if self.quantity < 0:
            raise ValueError("Insufficient stock available")
        self.save()

class PriceHistory(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    old_purchase_price = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    new_purchase_price = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    purchase_variation = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    
    old_retail_price = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    new_retail_price = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    retail_variation = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    
    change_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.product.product_name} price change on {self.change_date}"


class Sales(models.Model):
    invoice_number = models.CharField(max_length=255, unique=True, blank=True)
    date = models.DateField(default=timezone.now)
    customer_name = models.CharField(max_length=255, null=True, blank=True)
    customer_contact = models.CharField(max_length=20, null=True, blank=True)
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255, editable=False)  # Automatically set field
    quantity = models.IntegerField()
    unit = models.CharField(max_length=10, choices=[('bag', 'Bag'), ('ton', 'Ton')])
    rate = models.DecimalField(max_digits=20, decimal_places=2)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    payment_type = models.CharField(max_length=20, choices=[('cash', 'Cash'), ('credit card', 'Credit Card'), ('Cheque', 'Cheque')])
    due_balance = models.DecimalField(max_digits=20, decimal_places=2, default=0.00, null=True, blank=True)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, null=False)
    total = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    paid = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    def __str__(self):
        return f'Invoice {self.invoice_number}'
    
    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = self.generate_invoice_number()  # Use instance method
        if self.product and not self.product_name:
            self.product_name = self.product.product_name
        super().save(*args, **kwargs)

    def generate_invoice_number(self):  # Define instance method
        return str(uuid.uuid4().hex[:10].upper())  # Generate a UUID and format it

    @property
    def get_absolute_url(self):  # Define instance method
        return reverse('invoice_detail', kwargs={'pk': self.pk})

def update_total(sender, instance, **kwargs):
    if instance.discount is None:
        instance.discount = Decimal('0.00')
    
    if instance.amount is None:
        instance.amount = Decimal('0.00')

    instance.total = instance.amount - instance.discount

class ExpenseCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Expense(models.Model):
    expense_name = models.CharField(max_length=100, null=True, blank=True)
    expenser_name = models.CharField(max_length=100, null=True, blank=True)
    category = models.ForeignKey(ExpenseCategory, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_type = models.CharField(max_length=50, choices=[('cash', 'Cash'), ('bank', 'Bank'), ('online', 'Online')])

    def __str__(self):
        return f"{self.expense_name} - {self.amount}"
    

class DeadStock(models.Model):
    PRODUCT_UNITS = [
        ('BAGS', 'Bags'),
        ('TONS', 'Tons'),
    ]
    product_name = models.CharField(max_length=255)
    unit = models.CharField(max_length=10, choices=PRODUCT_UNITS)
    quantity = models.PositiveIntegerField()
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product_name} - {self.quantity} {self.unit}"
    

class Quotation(models.Model):
    name = models.CharField(max_length=255)
    datetime = models.DateTimeField()
    description = models.TextField()
    
    def __str__(self):
        return self.name
    

class Supplier(models.Model):
    supplier_name = models.CharField(max_length=255)
    contact = models.CharField(max_length=255)
    address = models.TextField()
    reference = models.CharField(max_length=255, null=True, blank=True)
    total_payable = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def update_total_payable(self):
        # Update total_payable based on related purchases
        total_payable = self.purchase_set.aggregate(total=Sum('payable'))['total'] or 0     
        self.total_payable = total_payable
        self.save()

    def __str__(self):
        return self.supplier_name
    
    

class Purchase(models.Model):
    PURCHASE_UNITS = [
        ('bags', 'Bags'),
        ('tons', 'Tons'),
    ]

    purchase_id = models.CharField(max_length=50, unique=True, editable=False)
    supplier_name = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    date = models.DateField()
    payment_type = models.CharField(max_length=50, choices=[('cash', 'Cash'), ('online', 'Online'), ('cheque', 'Cheque')])
    reference = models.CharField(max_length=255, null=True, blank=True)
    payable = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)


    def generate_purchase_id(self):
        unique_id = str(uuid.uuid4())
        self.purchase_id = 'P' + unique_id[:7]

    def save(self, *args, **kwargs):
        if not self.purchase_id:
            self.generate_purchase_id()

        super().save(*args, **kwargs)


class PurchaseProduct(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name='products')
    product_name = models.CharField(max_length=255)
    product_brand = models.CharField(max_length=255)
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    amount = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    units = models.CharField(max_length=50, default='bags')  # Default is 'bags', no choices needed

    def save(self, *args, **kwargs):
        self.amount = (self.rate * self.quantity) - self.discount
        super().save(*args, **kwargs)