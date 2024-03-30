from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import SignUpForm, AddSalesForm
from .models import Sales
from django.shortcuts import render, get_object_or_404




def index(request):
    # Check if logging in
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
            return redirect('index')

    # Rendering the index page
    return render(request, 'index.html')


def logout_user(request):
    logout(request)
    messages.success(request, "You have been logged out successfully")
    return redirect('index')

def register_user(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            #Authenticate and login
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username = username, password = password)
            login(request, user)
            messages.success(request, "You have successfully Registered! Welcome!")
            return redirect('index')
    else:
        form = SignUpForm()
        return render(request, 'register.html',{'form': form})

    return render(request, 'register.html',{'form': form})

def sales_record(request):
    if request.user.is_authenticated:
        try:
            sales = Sales.objects.all()
            return render(request, 'sales_details.html', {'sales': sales})
        except Sales.DoesNotExist:
            messages.error(request, "Sales record does not exist.")
            return redirect('index')
    else:
        return render(request, 'login.html')


def customer_record(request, pk):
    if request.user.is_authenticated:
        try:
            customer_sales_record = Sales.objects.get(id=pk)
            return render(request, 'record.html', {'customer_sales_record': customer_sales_record})
        except Sales.DoesNotExist:
            messages.error(request, "Sales record does not exist.")
            return redirect('sales_details.html')  
    

def delete_record(request, pk):
    if request.user.is_authenticated:
        delete_it = Sales.objects.get(id=pk)
        delete_it.delete()
        messages.success(request, "Record deleted successfully")
        return redirect('sales_details')
    else:
        messages.success(request, "You must be logged in to delete your records.")
        return redirect('index')
    
def add_sales(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            form = AddSalesForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Record Added...")
                return redirect('index')
        else:
            form = AddSalesForm()
        return render(request, 'add_sales.html', {'form': form})
    else:
        messages.error(request, "You Must Be Logged In...")
        return redirect('index')