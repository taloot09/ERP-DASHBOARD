from django.db import models

class Sales(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    customer_name = models.CharField(max_length=255)  # Updated field
    date = models.DateField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2)
    debit_amount = models.DecimalField(max_digits=10, decimal_places=2)
    credit_amount = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=4, choices=[('tons', 'Tons'), ('bags', 'Bags')])
    grand_total = models.DecimalField(max_digits=10, decimal_places=2)
    contact = models.CharField(max_length=45)
    product_name = models.CharField(max_length=255)
    quantity = models.IntegerField()
    invoice_id = models.CharField(max_length=255)
    type = models.CharField(max_length=50)

    def __str__(self):
        return f"SalesID: {self.id}, Product Name: {self.product_name}, Customer Name: {self.customer_name}, Date: {self.date}, Total Amount: {self.total_amount}, Discount: {self.discount}, Debit Amount: {self.debit_amount}, Credit Amount: {self.credit_amount}, Unit: {self.unit}, Grand Total: {self.grand_total}, Contact: {self.contact}, Quantity: {self.quantity}, Invoice ID: {self.invoice_id}, Type: {self.type}"