from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import CanteenVendor
from django.contrib.auth.hashers import make_password

def register_view(request):
 
    if request.method == 'POST':
        full_name = request.POST['full_name']
        restaurant_name = request.POST['restaurant_name']
        mobile_number = request.POST['mobile_number']
        store_description = request.POST['store_description']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        print(full_name, restaurant_name, mobile_number, store_description, password, confirm_password)
        # Password matching check
        if password != confirm_password:
            return render(request, 'register.html', {'error': 'Passwords do not match.'})

        # Hash password before storing
        hashed_password = make_password(password)

        # Create and save the vendor to the database
        vendor = CanteenVendor(
            full_name=full_name,
            restaurant_name=restaurant_name,
            mobile_number=mobile_number,
            store_description=store_description,
            password=hashed_password,
            confirm_password=hashed_password,  # Store hashed password
        )
        vendor.save()

        return redirect('login')  # Redirect to login page after registration
    
    return render(request, 'registration.html')

def home_view(request):
    return render(request, 'registration.html')

def dashboard(request):
    return render(request, 'vendor_dashboard.html')

def items(request):
    return render(request, 'vendor_items.html')

def order(request):
    return render(request, 'vendor_order.html')

def account(request):
    return render(request, 'vendor_account.html')

def login(request):
    return render(request, 'login.html')
