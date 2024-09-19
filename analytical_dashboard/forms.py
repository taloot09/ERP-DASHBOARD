# analytical_dashboard/forms.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dash_pro.settings')
django.setup()

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import Product
from .models import Customer
from .models import Sales
from .models import Expense
from .models import ExpenseCategory
from .models import DeadStock
from .models import Quotation
from .models import Supplier
from .models import Purchase
from django.forms import inlineformset_factory
from .models import Purchase, PurchaseProduct
from .models import AdvanceDeposit



class SignUpForm(UserCreationForm):
    email = forms.EmailField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}))
    first_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
    phone_number = forms.CharField(label="", max_length=15, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}))
    user_type = forms.ChoiceField(label="", choices=[('admin', 'Admin'), ('user', 'User')], widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'user_type', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['username'].widget.attrs['placeholder'] = 'User Name'
        self.fields['username'].label = ''
        self.fields['username'].help_text = '<span class="form-text text-muted"><small>Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.</small></span>'

        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['placeholder'] = 'Password'
        self.fields['password1'].label = ''
        self.fields['password1'].help_text = '<ul class="form-text text-muted small"><li>Your password can\'t be too similar to your other personal information.</li><li>Your password must contain at least 8 characters.</li><li>Your password can\'t be a commonly used password.</li><li>Your password can\'t be entirely numeric.</li></ul>'

        self.fields['password2'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'
        self.fields['password2'].label = ''
        self.fields['password2'].help_text = '<span class="form-text text-muted"><small>Enter the same password as before, for verification.</small></span>'


class AddProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_name', 'brand', 'category']
        widgets = {
            'product_name': forms.TextInput(attrs={'placeholder': 'Product Name', 'class': 'mt-3'}),
            'brand': forms.TextInput(attrs={'placeholder': 'Brand', 'class': 'mt-3'}),
            'category': forms.TextInput(attrs={'placeholder': 'Category', 'class': 'mt-3'}),
        }

class ProductUpdateForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_name', 'quantity', 'retail_price']

class PriceChangeForm(forms.ModelForm):
    new_purchase_price = forms.DecimalField(max_digits=20, decimal_places=2)
    new_retail_price = forms.DecimalField(max_digits=20, decimal_places=2)
    quantity = forms.IntegerField()

    class Meta:
        model = Product
        fields = ['new_purchase_price', 'new_retail_price', 'quantity']

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = [
            'customer_name',
            'contact',
            'address',
            'city',
            'credit_amount',
            'credit_limit',
            'email',
            'nic',
            'reference'
        ]

class AdvanceDepositForm(forms.ModelForm):
    class Meta:
        model = AdvanceDeposit
        fields = ['customer', 'amount', 'payment_type']
        widgets = {
            'payment_type': forms.Select(choices=AdvanceDeposit.PAYMENT_CHOICES),
        }
        



class SalesForm(forms.ModelForm):
    #existing_customer_id = forms.CharField(widget=forms.HiddenInput(), required=False)
    
    class Meta:
        model = Sales
        fields = ['invoice_number', 'date', 'customer_name', 'customer_contact', 'customer', 'product', 'quantity', 'unit', 'rate', 'amount', 'payment_type', 'due_balance', 'paid', 'total', 'subtotal', 'discount']
        widgets = {
            'invoice_number': forms.TextInput(attrs={'class': 'form-control', 'readonly': True}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'customer_name': forms.TextInput(attrs={'class': 'form-control'}),
            'customer_contact': forms.TextInput(attrs={'class': 'form-control'}),
            'customer': forms.HiddenInput(),
            'product': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'unit': forms.Select(attrs={'class': 'form-control'}),
            'rate': forms.NumberInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'payment_type': forms.Select(attrs={'class': 'form-control'}),
            'due_balance': forms.NumberInput(attrs={'class': 'form-control'}),
            'paid': forms.NumberInput(attrs={'class': 'form-control'}),
            'total': forms.NumberInput(attrs={'class': 'form-control'}),
            'subtotal': forms.NumberInput(attrs={'class': 'form-control'}),
            'discount': forms.NumberInput(attrs={'class': 'form-control'}),
        }
    def clean_subtotal(self):
        subtotal = self.cleaned_data.get('subtotal')
        # Ensure it adheres to the new constraints
        if len(str(subtotal).split('.')[0]) > 10:  # Example for 10 digits before decimal
            raise forms.ValidationError('Ensure that there are no more than 10 digits before the decimal point.')
        return subtotal


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['expense_name', 'expenser_name', 'category', 'amount', 'payment_type']


class ExpenseCategoryForm(forms.ModelForm):
    class Meta:
        model = ExpenseCategory
        fields = ['name']


class DeadStockForm(forms.ModelForm):
    class Meta:
        model = DeadStock
        fields = ['product_name', 'unit', 'quantity', 'description']
        widgets = {
            'product_name': forms.TextInput(attrs={'class': 'form-control'}),
            'unit': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
        }


class QuotationForm(forms.ModelForm):
    class Meta:
        model = Quotation
        fields = ['name', 'datetime', 'description']
        widgets = {
            'datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['supplier_name', 'contact', 'address', 'reference']


class PurchaseForm(forms.ModelForm): 
    class Meta: 
        model = Purchase 
        fields = ['supplier_name', 'date', 'payment_type', 'reference', 'payable'] 
        widgets = { 
            'supplier_name': forms.Select(attrs={'class': 'form-control'}), 
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), 
            'payment_type': forms.Select(attrs={'class': 'form-control'}), 
            'reference': forms.TextInput(attrs={'class': 'form-control'}), 
            'payable': forms.NumberInput(attrs={'class': 'form-control'}), }

class PurchaseProductForm(forms.ModelForm): 
    class Meta: 
        model = PurchaseProduct 
        fields = ['product_name', 'product_brand', 'rate', 'quantity', 'discount', 'units'] 
        widgets = { 
            'product_name': forms.TextInput(attrs={'class': 'form-control'}), 
            'product_brand': forms.TextInput(attrs={'class': 'form-control'}), 
            'rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}), 
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}), 
            'discount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}), 
            'units': forms.HiddenInput(attrs={'value': 'bags'}) # Set default unit 
            } 
ProductFormSet = inlineformset_factory(Purchase, PurchaseProduct, form=PurchaseProductForm, extra=1, can_delete=True)

class ManageUnitsForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_name', 'retail_price', 'rate_per_bag', 'rate_per_ton']
        widgets = {
            'product_name': forms.TextInput(attrs={'readonly': 'readonly'}),
            'retail_price': forms.TextInput(attrs={'readonly': 'readonly'}),
            'rate_per_bag': forms.NumberInput(attrs={'class': 'form-control'}),
            'rate_per_ton': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(ManageUnitsForm, self).__init__(*args, **kwargs)
        # Initialize the rate_per_bag and rate_per_ton fields
        self.fields['rate_per_bag'].initial = self.instance.retail_price
        self.fields['rate_per_ton'].initial = self.instance.retail_price * 20