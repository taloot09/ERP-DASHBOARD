# analytical_dashboard/views.py


import logging
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from analytical_dashboard.forms import SignUpForm
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponse
from reportlab.pdfgen import canvas
from analytical_dashboard.forms import AddProductForm
from analytical_dashboard.forms import ProductUpdateForm
from analytical_dashboard.models import Customer, Product, PriceHistory, Sales
from analytical_dashboard.forms import PriceChangeForm
import json
from decimal import Decimal, InvalidOperation
from django.utils import timezone
from django.urls import reverse
from django.http import JsonResponse
from analytical_dashboard.forms import CustomerForm
from analytical_dashboard.forms import SalesForm
from django.views.decorators.http import require_POST
import time
import uuid
from django.test import RequestFactory
from django.views.decorators.csrf import csrf_exempt
#from .views import invoice_view
from datetime import timedelta
from .forms import ExpenseForm
from .models import ExpenseCategory
from .forms import ExpenseCategoryForm
from .models import Expense
from django.db.models import Sum
from datetime import datetime
from .models import DeadStock
from .forms import DeadStockForm
from .forms import QuotationForm
from .models import Quotation
from .models import Supplier
from .forms import SupplierForm
from .models import Purchase
from .forms import PurchaseForm, ProductFormSet, PurchaseProductForm
from .models import PurchaseProduct
from django.db.models import Sum, F
from django.template.loader import render_to_string
import pdfkit
from django.template.loader import get_template
from .models import AdvanceDeposit  # Assuming you have a model for this
from .forms import AdvanceDepositForm
from django.views import View
import calendar
from django.utils.timezone import now
from django.db.models import Q
from .forms import ManageUnitsForm
from django.db import transaction
from django.forms import inlineformset_factory







def index(request):
    # Rendering the index page
    return render(request, 'index.html')

def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        # Authenticate
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "You have been logged in successfully")
            return redirect('index')
        else:
            messages.error(request, "There was an error, please try again")
            return redirect('login')  # Redirect to login page on error

    # Rendering the login page
    return render(request, 'login.html')

def logout_user(request):
    logout(request)
    messages.success(request, "You have been logged out successfully")
    return redirect('login')

def register_user(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            phone_number = form.cleaned_data.get('phone_number')
            user_type = form.cleaned_data.get('user_type')
            # Save phone number and user type to user profile or related model if needed
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, "You have successfully Registered! Welcome!")
            return redirect('index')
    else:
        form = SignUpForm()
    return render(request, 'register.html', {'form': form})

def add_user(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "User added successfully!")
            return redirect('add_user')
    else:
        form = SignUpForm()
    return render(request, 'adduser.html', {'form': form})


def add_product(request):
    if request.method == 'POST':
        form = AddProductForm(request.POST)
        if form.is_valid():
            form.save()
            if 'save_and_new' in request.POST:
                return redirect('add_product')
            return redirect('add_product')  # Update to your (product_list) view 
    else:
        form = AddProductForm()
    return render(request, 'add_product.html', {'form': form})

def manage_products(request):
    if request.method == "POST" and 'update_product' in request.POST:
        product_id = request.POST.get("update_product")
        product = get_object_or_404(Product, id=product_id)
        product.product_name = request.POST.get(f'product_name_{product_id}')
        product.quantity = request.POST.get(f'quantity_{product_id}')
        product.retail_price = request.POST.get(f'retail_price_{product_id}')
        product.save()
        return redirect("manage_products")
    else:
        products = Product.objects.all()
        average_prices = {product.id: product.average_purchase_price() for product in products}
        return render(request, "manage_products.html", {"products": products, "average_prices": average_prices})

def view_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, "view_product.html", {"product": product})

def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return redirect(reverse("manage_products"))

def update_product(request, product_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        product = get_object_or_404(Product, id=product_id)
        product.product_name = data.get('product_name')
        product.quantity = data.get('quantity')
        product.retail_price = data.get('retail_price')
        product.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return super(DecimalEncoder, self).default(obj)

def price_change(request):
    products = Product.objects.all()
    if request.method == 'POST':
        product_id = request.POST['product_id']
        new_purchase_price = Decimal(request.POST['new_purchase_price'])
        new_retail_price = Decimal(request.POST['new_retail_price'])
        quantity = int(request.POST['quantity'])

        product = get_object_or_404(Product, id=product_id)
        original_purchase_price = product.purchase_price
        original_retail_price = product.retail_price

        # Ensure product.quantity is initialized or handle None case
        if product.quantity is None:
            product.quantity = 0
        
        product.purchase_price = new_purchase_price
        product.retail_price = new_retail_price
        product.quantity += quantity
        product.save()


        # Save the price history
        if original_purchase_price is not None and original_retail_price is not None:
            purchase_variation = new_purchase_price - original_purchase_price
            retail_variation = new_retail_price - original_retail_price

            PriceHistory.objects.create(
                product=product,
                change_date=timezone.now(),  # Using change_date instead of date
                purchase_variation=purchase_variation,
                retail_variation=retail_variation,
                old_purchase_price=original_purchase_price,
                new_purchase_price=new_purchase_price,
                old_retail_price=original_retail_price,
                new_retail_price=new_retail_price
            )

        return redirect('price_change')

    # Ensure products JSON is properly encoded
    products_json = json.dumps(list(products.values('id', 'product_name', 'purchase_price', 'retail_price', 'quantity')), cls=DecimalEncoder)

    price_history = PriceHistory.objects.order_by('-change_date')[:10]  # Using change_date instead of date

    # Log products for debugging
    print(products_json)

    return render(request, 'price_change.html', {
        'products': products,
        'products_json': products_json,
        'price_history': price_history,
    })

def add_customer(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('customer_list')  # Correct URL name for customer list
    else:
        form = CustomerForm()
    return render(request, 'add_customer.html', {'form': form})

def customer_list(request):
    customers = Customer.objects.all()
    return render(request, 'allcustomers.html', {'customers': customers})

#Invoice
logger = logging.getLogger(__name__)

def generate_invoice_number():
    return 'I' + str(uuid.uuid4().hex[:9].upper())

# Define the create_invoice function
def create_invoice(request):
    if request.method == 'POST':
        # Print POST data for debugging
        print("POST data:", request.POST)

        # Extract necessary data from POST request
        invoice_number = generate_invoice_number()
        customer_name = request.POST.get('customer_name', '').strip()

        # Initialize monetary amounts
        try:
            discount = Decimal(request.POST.get('discount', '0.00'))
        except InvalidOperation:
            discount = Decimal('0.00')

        try:
            paid = Decimal(request.POST.get('paid', '0.00'))
        except InvalidOperation:
            paid = Decimal('0.00')

        customer = None
        if customer_name:
            existing_customers = Customer.objects.filter(customer_name__iexact=customer_name)
            if existing_customers.exists():
                customer = existing_customers.first()

        # Retrieve form data for multiple product entries
        product_ids = request.POST.getlist('product_id[]')
        quantities = request.POST.getlist('quantity[]')
        rates = request.POST.getlist('rate[]')
        amounts = request.POST.getlist('amount[]')
        units = request.POST.getlist('unit[]')

        # Ensure that we have matching form data for all fields
        if len(product_ids) != len(quantities) or len(product_ids) != len(rates) or len(product_ids) != len(amounts) or len(product_ids) != len(units):
            return JsonResponse({'error': 'Mismatch in form data lengths.'}, status=400)

        total = Decimal('0.00')
        sales_instances = []

        for i in range(len(product_ids)):
            product_id = product_ids[i]
            quantity = quantities[i]
            rate = rates[i]
            amount = amounts[i]
            unit = units[i]

            # Ensure each field has valid data
            if product_id and quantity and rate and amount and unit:
                try:
                    quantity = Decimal(quantity)
                    rate = Decimal(rate)
                    amount = Decimal(amount)
                except InvalidOperation:
                    print(f"Error converting values for product ID {product_id}: Quantity: {quantity}, Rate: {rate}, Amount: {amount}")
                    continue  # Skip this iteration if conversion fails

                product = Product.objects.filter(id=product_id).first()
                if product:
                    sales_instance = Sales(
                        invoice_number=invoice_number,
                        customer=customer,
                        customer_name=customer_name,
                        product=product,
                        product_name=product.product_name,
                        quantity=quantity,
                        rate=rate,
                        amount=amount,
                        unit=unit,
                        subtotal=total,
                        total=total + amount,
                        discount=discount,
                        paid=paid,
                    )
                    sales_instances.append(sales_instance)
                    total += amount

                    # Reduce stock based on the sale
                    product.reduce_stock(quantity, unit)

        # Save all sales instances to the database
        if sales_instances:
            Sales.objects.bulk_create(sales_instances)  # This will insert multiple entries in a single query
            return JsonResponse({'success': True, 'invoice_number': invoice_number})
        else:
            return JsonResponse({'error': 'No valid sales data found.'}, status=400)

    # Handle GET request - Render the invoice form
    else:
        invoice_number = generate_invoice_number()
        sales_form = SalesForm(initial={'invoice_number': invoice_number})

        products = Product.objects.all().values('id', 'product_name')
        customers = Customer.objects.all()

        return render(request, 'invoice.html', {
            'products': list(products),
            'customers': customers,
            'sales_form': sales_form,
        })






# To get rate of each product
def get_product_rates(request):
    product_id = request.GET.get('product_id')
    if product_id:
        try:
            product = Product.objects.get(id=product_id)
            data = {
                'rate_per_bag': product.rate_per_bag,
                'rate_per_ton': product.rate_per_ton,
            }
            return JsonResponse(data)
        except Product.DoesNotExist:
            return JsonResponse({'error': 'Product not found.'}, status=404)
    return JsonResponse({'error': 'Invalid request.'}, status=400)


#to get available stockon sales page.
def get_available_stock(request):
    product_id = request.GET.get('product_id')
    print('Product ID from request:', product_id)  # Debugging
    if product_id:
        try:
            product = Product.objects.get(id=product_id)
            print('Product found:', product.product_name, 'Available stock:', product.quantity)  # Debugging
            return JsonResponse({'available_stock': product.quantity})
        except Product.DoesNotExist:
            print('Product does not exist')  # Debugging
            return JsonResponse({'available_stock': 0})
    print('No product ID provided')  # Debugging
    return JsonResponse({'available_stock': 0})



# Add a view to handle AJAX request for getting due balance
from django.http import JsonResponse

# fetch Due balance functionality

def get_customer_due_balance(request):
    customer_name = request.GET.get('customer_name')
    print(f"Received customer_name: {customer_name}")  # Debug statement
    if customer_name:
        try:
            customer = Customer.objects.get(customer_name=customer_name)
            due_balance = customer.credit_amount
            return JsonResponse({'status': 'success', 'due_balance': due_balance})
        except Customer.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'No customer found'})
    return JsonResponse({'status': 'error', 'message': 'Customer name not provided'})



def sales_view(request):
    # Fetch all sales records
    sales = Sales.objects.all().order_by('-date')  # Order by date, most recent first
    return render(request, 'sales_view.html', {'sales': sales})



def get_product_details(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    return JsonResponse({
        'available_stock': product.available_stock,
        'rate_per_bag': product.rate_per_bag,
        'rate_per_ton': product.rate_per_ton,
    })
    

# @csrf_exempt
# def save_customer_info(request):
#     if request.method == 'POST':
#         name = request.POST.get('name')
#         contact = request.POST.get('contact')
#         city = request.POST.get('city')
#         nic = request.POST.get('nic')
#         reference = request.POST.get('reference')

#         if name and contact:
#             # Save data to the database
#             customer = Customer.objects.create(
#                 customer_name=name,
#                 contact=contact,
#                 address=city,
#                 nic=nic,
#                 reference=reference
#             )
#             return JsonResponse({'status': 'success', 'customer_id': customer.id})
#         else:
#             return JsonResponse({'status': 'fail', 'error': 'Missing name or contact'})
#     return JsonResponse({'status': 'fail', 'error': 'Invalid request method'}, status=405)
    

# def get_customer_details(request, contact):
#     try:
#         customer = Customer.objects.get(contact=contact)
#         return JsonResponse({
#             'name': customer.customer_name,
#             'due_balance': customer.credit_amount,
#             'customer_id': customer.id
#         })
#     except Customer.DoesNotExist:
#         return JsonResponse({'name': '', 'due_balance': 0, 'customer_id': ''})

    

def invoice_view(request):
    if request.method == 'POST':
        form = SalesForm(request.POST)
        if form.is_valid():
            sales_instance = form.save()  # Save form and get the instance
            return render(request, 'invoice.html', {'sales_instance': sales_instance})
        else:
            
            print(f"Form errors: {form.errors}")  # Check form validation errors
    else:
        form = SalesForm()
    
    return render(request, 'invoice.html', {'sales_form': form})


def cashbook(request):
    filter_option = request.GET.get('filter', 'cash')  # Get filter option from request
    now = timezone.now()
    
    if filter_option == 'today':
        start_date = now.date()
        end_date = now.date() + timedelta(days=1)
    elif filter_option == 'month':
        start_date = now.replace(day=1).date()
        end_date = (now.replace(day=1) + timedelta(days=32)).replace(day=1).date()
    elif filter_option == 'year':
        start_date = now.replace(month=1, day=1).date()
        end_date = now.replace(year=now.year + 1, month=1, day=1).date()
    else:  # 'all'
        start_date = None
        end_date = None
    
    if start_date and end_date:
        cash_sales = Sales.objects.filter(payment_type='cash', date__range=(start_date, end_date))
    else:
        cash_sales = Sales.objects.filter(payment_type='cash')
    
    context = {
        'cash_sales': cash_sales,
        'today_date': now.strftime('%d-%m-%Y'),
        'printed_date': now.strftime('%d-%m-%Y'),
        'printed_time': now.strftime('%I:%M:%S %p'),
        'filter_option': filter_option,  # Pass filter option to template
    }
    return render(request, 'cashbook.html', context)


def record_expense(request):
    categories = ExpenseCategory.objects.all()
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            form.save()
            if 'save_new' in request.POST:
                return redirect('record_expense')  # Redirect back to the form for a new entry
            return redirect('record_expense')  # Replace with your success page
        else:
            print(form.errors)  # Debugging line to print form errors
    else:
        form = ExpenseForm()
    return render(request, 'record_expense.html', {'categories': categories})



def add_expense_category(request):
    if request.method == 'POST':
        form = ExpenseCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('add_expense_category')  # Replace with your success page or URL name
    else:
        form = ExpenseCategoryForm()
    return render(request, 'add_expense_category.html', {'form': form})

def delete_category(request, category_id):
    category = get_object_or_404(ExpenseCategory, id=category_id)
    if request.method == 'POST':
        category.delete()
        return redirect('add_category')
    return render(request, 'confirm_delete.html', {'category': category})


def expense_statement(request):
    # Fetch all expenses with related category
    expenses = Expense.objects.select_related('category').all()
    
    # Calculate total expenses
    total_amount = expenses.aggregate(total=Sum('amount'))['total'] or 0
    
    # Get current date and time for display
    current_date = datetime.now().strftime('%d-%m-%Y')
    current_time = datetime.now().strftime('%I:%M:%S %p')
    
    return render(request, 'expensestatement.html', {
        'expenses': expenses,
        'total_amount': total_amount,
        'current_date': current_date,
        'current_time': current_time,
        'printed_date': current_date,  # You can adjust this as needed
    })


def cheque_transactions(request):
    # Query to fetch all transactions with payment mode 'Cheque'
    transactions = Sales.objects.filter(payment_type='cheque')

    context = {
        'transactions': transactions
    }
    return render(request, 'cheque_transactions.html', context)


def record_dead_stock(request):
    if request.method == 'POST':
        form = DeadStockForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('record_dead_stock')
    else:
        form = DeadStockForm()

    dead_stock_entries = DeadStock.objects.all()
    return render(request, 'record_dead_stock.html', {'form': form, 'dead_stock_entries': dead_stock_entries})


def add_quotations(request):
    if request.method == 'POST':
        form = QuotationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('add_quotations')
    else:
        form = QuotationForm()
    quotations = Quotation.objects.all()
    return render(request, 'add_quotations.html', {'form': form, 'quotations': quotations})

#CHARTS

@csrf_exempt
def sales_data(request):
    sales = Sales.objects.all().values('date', 'amount')
    data = list(sales)
    return JsonResponse(data, safe=False)


def supplier_list(request):
    suppliers = Supplier.objects.all()
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('supplier_list')
    else:
        form = SupplierForm()
    return render(request, 'supplier_list.html', {'form': form, 'suppliers': suppliers})


# Assuming the Purchase and PurchaseProduct models
ProductFormSet = inlineformset_factory(Purchase, PurchaseProduct, form=PurchaseProductForm, extra=1, can_delete=True)

def add_purchase(request):
    if request.method == 'POST':
        form = PurchaseForm(request.POST)
        formset = ProductFormSet(request.POST, prefix='products')

        if form.is_valid() and formset.is_valid():
            # Create the main purchase entry
            purchase = form.save()
            total = 0  # Initialize total to 0

            # Loop through the formset to save each product
            for product_form in formset:
                if product_form.cleaned_data:
                    # Save each product related to this purchase
                    purchase_product = product_form.save(commit=False)
                    purchase_product.purchase = purchase  # Link the product to the main purchase
                    purchase_product.save()  # This will calculate and save amount automatically
                    total += purchase_product.amount  # Add amount to total from product instance

            # Save total in the purchase and payable if not provided
            purchase.total = total
            purchase.payable = purchase.payable or total  # Assign total if payable is not provided
            purchase.save()

            # Redirect or show success message
            return redirect('manage_purchases')  # Assuming 'manage_purchases' is the view

        else:
            # Debugging formset errors
            print(form.errors)
            print(formset.errors)
            messages.error(request, "There were errors in your form submission.")

    else:
        form = PurchaseForm()
        formset = ProductFormSet(prefix='products')

    context = {
        'form': form,
        'formset': formset,
    }

    return render(request, 'add_purchase.html', context)



#purchase view
def manage_purchases(request):
    purchases = Purchase.objects.all()
    context = {
        'purchases': purchases,
    }
    return render(request, 'manage_purchases.html', context)


#REPORTS

#PROFIT/LOSS REPORT


def profit_loss_report(request):
    # Aggregate total sales directly from the database
    total_sales = Sales.objects.aggregate(total_sales=Sum('total'))['total_sales'] or 0

    # Aggregate total expenses directly from the database
    total_expenses = Expense.objects.aggregate(total_expenses=Sum('amount'))['total_expenses'] or 0

    # Calculate total purchase cost from the sales data
    sales_data = Sales.objects.all()
    total_purchase_cost = sum(
        sale.product.purchase_price * sale.quantity if sale.product.purchase_price else 0
        for sale in sales_data
    )

    # Calculate profit or loss
    profit_loss = total_sales - total_purchase_cost - total_expenses

    return render(request, 'profit_loss_report.html', {
        'total_sales': total_sales,
        'total_purchase_cost': total_purchase_cost,
        'total_expenses': total_expenses,
        'profit_loss': profit_loss,
    })

def download_profit_loss_pdf(request):
    period = request.GET.get('period', 'all')

    # Filter sales data based on the selected period
    if period == 'monthly':
        start_date = timezone.now().replace(day=1)
        end_date = (start_date + timedelta(days=31)).replace(day=1)
        sales_data = Sales.objects.filter(date__range=[start_date, end_date])
        expenses_data = Expense.objects.filter(date__range=[start_date, end_date])
    elif period == 'yearly':
        start_date = timezone.now().replace(month=1, day=1)
        end_date = (start_date + timedelta(days=365)).replace(month=1, day=1)
        sales_data = Sales.objects.filter(date__range=[start_date, end_date])
        expenses_data = Expense.objects.filter(date__range=[start_date, end_date])
    elif period == 'weekly':
        start_date = timezone.now() - timedelta(days=timezone.now().weekday())
        end_date = start_date + timedelta(days=7)
        sales_data = Sales.objects.filter(date__range=[start_date, end_date])
        expenses_data = Expense.objects.filter(date__range=[start_date, end_date])
    else:
        sales_data = Sales.objects.all()
        expenses_data = Expense.objects.all()

    # Calculation of total sales, purchase cost, and profit/loss
    total_sales = sum(sale.total for sale in sales_data)
    total_purchase_cost = sum(sale.product.purchase_price * sale.quantity for sale in sales_data)
    total_expenses = sum(expense.amount for expense in expenses_data)
    profit_loss = total_sales - total_purchase_cost - total_expenses

    # Generate context data
    context = {
        'total_sales': total_sales,
        'total_purchase_cost': total_purchase_cost,
        'total_expenses': total_expenses,
        'profit_loss': profit_loss,
        'period': period,
        'expenses': expenses_data
    }
    
    # Render the report to an HTML string
    html_string = render_to_string('profit_loss_report_pdf.html', context)
    
    # Generate PDF
    pdf = pdfkit.from_string(html_string, False)
    
    # Return PDF as a download response
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="profit_loss_report.pdf"'
    return response


#SALES REPORT

def sales_report(request):
    sales_data = Sales.objects.all()

    # Calculating totals
    total_sales = sales_data.aggregate(Sum('total'))['total__sum'] or 0
    total_quantity = sales_data.aggregate(Sum('quantity'))['quantity__sum'] or 0
    total_due_balance = sales_data.aggregate(Sum('due_balance'))['due_balance__sum'] or 0
    total_paid = sales_data.aggregate(Sum('paid'))['paid__sum'] or 0
    total_wholesales = sales_data.filter(unit='ton').aggregate(Sum('quantity'))['quantity__sum'] or 0
    total_normal_sales = sales_data.filter(unit='bag').aggregate(Sum('quantity'))['quantity__sum'] or 0

    context = {
        'sales_data': sales_data,
        'total_sales': total_sales,
        'total_quantity': total_quantity,
        'total_due_balance': total_due_balance,
        'total_paid': total_paid,
        'total_wholesales': total_wholesales,
        'total_normal_sales': total_normal_sales,
    }

    return render(request, 'sales_report.html', context)

#SALES PDF
def download_sales_report_pdf(request):
    # Retrieve sales data
    sales_data = Sales.objects.all()

    # Calculation of totals
    total_sales = sales_data.aggregate(Sum('total'))['total__sum'] or 0
    total_quantity = sales_data.aggregate(Sum('quantity'))['quantity__sum'] or 0
    total_due_balance = sales_data.aggregate(Sum('due_balance'))['due_balance__sum'] or 0
    total_paid = sales_data.aggregate(Sum('paid'))['paid__sum'] or 0
    total_wholesales = sales_data.filter(unit='ton').aggregate(Sum('quantity'))['quantity__sum'] or 0
    total_normal_sales = sales_data.filter(unit='bag').aggregate(Sum('quantity'))['quantity__sum'] or 0

    # Prepare context data for rendering
    context = {
        'sales_data': sales_data,
        'total_sales': total_sales,
        'total_quantity': total_quantity,
        'total_due_balance': total_due_balance,
        'total_paid': total_paid,
        'total_wholesales': total_wholesales,
        'total_normal_sales': total_normal_sales,
    }
    
    # Render the HTML template with context data
    html_string = render_to_string('sales_report_pdf.html', context)
    
    # Generate PDF from HTML string
    pdf = pdfkit.from_string(html_string, False)
    
    # Return the PDF as a response
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'
    return response

#PRODUCT WISE REPORT

def product_wise_report(request):
    products = Product.objects.all()
    product_data = []
    for product in products:
        sales = Sales.objects.filter(product=product)
        total_sales = sales.aggregate(Sum('total'))['total__sum'] or 0
        total_quantity = sales.aggregate(Sum('quantity'))['quantity__sum'] or 0
        product_data.append({
            'product': product,
            'sales': sales,
            'total_sales': total_sales,
            'total_quantity': total_quantity,
        })
    return render(request, 'product_wise_report.html', {'product_data': product_data})

def product_list(request):
    products = Product.objects.all()
    return render(request, 'product_list.html', {'products': products})

def manage_units(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ManageUnitsForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_list')  # Redirect to product list after saving
    else:
        form = ManageUnitsForm(instance=product)

    context = {
        'form': form,
        'product': product,
    }
    return render(request, 'manage_units.html', context)


def dashboard_view(request):
    # Get the current month and year
    current_month = timezone.now().month
    current_year = timezone.now().year

    # Calculate the total revenue for the current month
    monthly_revenue = Sales.objects.filter(date__month=current_month, date__year=current_year).aggregate(total_revenue=Sum('total'))['total_revenue'] or 0

    # Print the monthly revenue to the console
    print("Monthly Revenue:", monthly_revenue)

    context = {
        'monthly_revenue': monthly_revenue,
    }
    print("Context Data:", context)
    return render(request, 'index.html', context)

def profit_graph(request):
    # Get the current month and year
    current_month = timezone.now().month
    current_year = timezone.now().year

    # Calculate monthly profit
    profit_data = Sales.objects.filter(date__month=current_month, date__year=current_year).annotate(
        cost=F('quantity') * F('product__purchase_price'),
        profit=F('total') - F('quantity') * F('product__purchase_price')
    ).values('date', 'profit')

    # Prepare data for the chart
    x_values = [entry['date'].strftime('%Y-%m-%d') for entry in profit_data]
    y_values = [entry['profit'] for entry in profit_data]

    context = {
        'x_values': json.dumps(x_values),  # Convert to JSON
        'y_values': json.dumps(y_values),  # Convert to JSON
        'monthly_profit': sum(y_values)  # Calculate total profit for the month
    }
    
    return render(request, 'index.html', context)


def sales_overview_data(request):
    today = timezone.now()
    start_date = today - timedelta(days=30)
    previous_start_date = start_date - timedelta(days=30)
    previous_end_date = start_date - timedelta(days=1)

    current_sales = Sales.objects.filter(
        sale_date__range=(start_date, today)
    ).aggregate(current=Sum('amount'))['current'] or 0

    previous_sales = Sales.objects.filter(
        sale_date__range=(previous_start_date, previous_end_date)
    ).aggregate(previous=Sum('amount'))['previous'] or 0

    chart_data = [
        {"time_period": "Last 30 Days", "current": current_sales, "previous": previous_sales}
    ]

    return JsonResponse(chart_data, safe=False)

def advance_deposit(request):
    if request.method == "POST":
        form = AdvanceDepositForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('advance_deposit')
    else:
        form = AdvanceDepositForm()
    deposits = AdvanceDeposit.objects.all()
    return render(request, 'advance_deposit.html', {'form': form, 'deposits': deposits})

def update_deposit(request, pk):
    deposit = get_object_or_404(AdvanceDeposit, pk=pk)
    if request.method == "POST":
        form = AdvanceDepositForm(request.POST, instance=deposit)
        if form.is_valid():
            form.save()  # This triggers the save method in the model
            print("Form saved successfully")
            return redirect('advance_deposit')
        else:
            print("Form errors:", form.errors)
    else:
        form = AdvanceDepositForm(instance=deposit)
    return render(request, 'update_deposit.html', {'form': form})

def delete_deposit(request, pk):
    deposit = get_object_or_404(AdvanceDeposit, pk=pk)
    if request.method == "POST":
        deposit.delete()
        return redirect('advance_deposit')
    else:
        return redirect('advance_deposit')
    

class CustomerProfileView(View):
    def get(self, request, pk):
        # Fetch the customer object or return a 404 if not found
        customer = get_object_or_404(Customer, pk=pk)
        
        # Retrieve the sales related to the customer
        sales = Sales.objects.filter(customer=customer)
        
        # Calculate the total sales amount
        total_sales_amount = sum(sale.total for sale in sales)
        
        # Fetch the deposit amount (assuming it’s stored in a different model or context)
        # Initialize deposit_amount to 0 if you have no deposit logic yet
        deposit_amount = 0  # Replace this with actual logic to fetch deposit
        
        # Calculate balance
        credit_amount = customer.credit_amount or 0
        balance = credit_amount + deposit_amount
        
        # Prepare the context for the template
        context = {
            'customer': customer,
            'sales': sales,
            'total_sales_amount': total_sales_amount,
            'balance': balance,
        }
        
        # Render the template with the context
        return render(request, 'customer_profile.html', context)
    
def delete_invoice(request, invoice_id):
    try:
        invoice = get_object_or_404(Sales, id=invoice_id)
        invoice.delete()
        return redirect('customer_profile')  # Make sure 'invoice_list' is a valid URL name
    except Sales.DoesNotExist:
        return HttpResponse("No invoice found with this ID.", status=404)
    
#Sales Graph:

def statistics_view(request):
    return render(request, 'statistics.html')

def get_monthly_sales(request):
    current_year = now().year
    sales_data = Sales.objects.filter(date__year=current_year).values(
        'date__month'
    ).annotate(
        total_sales=Sum('total')
    ).order_by('date__month')

    # Prepare data for FusionCharts
    data = []
    for month in range(1, 13):
        month_sales = next((item for item in sales_data if item['date__month'] == month), {'total_sales': 0})
        month_name = calendar.month_abbr[month]
        data.append({
            'label': month_name,
            'value': str(month_sales['total_sales'])
        })

    return JsonResponse(data, safe=False)

def product_performance(request):
    return render(request, 'product_performance.html')

def get_sales_data(request):
    # Query for total sales grouped by product name
    sales_data = Sales.objects.values('product_name').annotate(total_sales=Sum('amount'))
    
    # Format data for FusionCharts
    response_data = {
        'chart': {
            'caption': "Sales by Product",
            'subcaption': "For the year 2024",
            'xaxisname': "Product",
            'yaxisname': "Total Sales",
            'numbersuffix': "$",
            'theme': "candy"
        },
        'data': [{'label': sale['product_name'], 'value': sale['total_sales']} for sale in sales_data]
    }
    
    return JsonResponse(response_data)

def price_changes_graph(request, product_id):
    product = Product.objects.filter(id=product_id).order_by('date')
    data = {
        'dates': [p.date.strftime("%Y-%m-%d") for p in product],
        'purchase_prices': [float(p.purchase_price) for p in product],
        'retail_prices': [float(p.retail_price) for p in product],
    }
    return JsonResponse(data)

def search_view(request):
    query = request.GET.get('q', '')
    if query:
        customers = Customer.objects.filter(customer_name__icontains=query).values('customer_name')
        products = Product.objects.filter(product_name__icontains=query).values('product_name')
        sales = Sales.objects.filter(customer_name__icontains=query).values('customer_name')
        expenses = Expense.objects.filter(expense_name__icontains=query).values('expense_name')
        suppliers = Supplier.objects.filter(supplier_name__icontains=query).values('supplier_name')

        results = []
        for customer in customers:
            results.append({'name': customer['customer_name'], 'model': 'Customer'})
        for product in products:
            results.append({'name': product['product_name'], 'model': 'Product'})
        for sale in sales:
            results.append({'name': sale['customer_name'], 'model': 'Sales'})
        for expense in expenses:
            results.append({'name': expense['expense_name'], 'model': 'Expense'})
        for supplier in suppliers:
            results.append({'name': supplier['supplier_name'], 'model': 'Supplier'})

        return JsonResponse(results, safe=False)
    return JsonResponse([], safe=False)