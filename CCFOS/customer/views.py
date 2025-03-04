from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import make_password, check_password
import random
from .models import Customer
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import check_password
def registration_view(request):
    if request.method == "POST":
        full_name = request.POST.get('full_name')
        mobile = request.POST.get('mobile')
        email = request.POST.get('email')
        otp_input = request.POST.get('otp')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # # Validate OTP from session storage
        # stored_otp = request.session.get('otp')
        # print(stored_otp)
        # if not stored_otp or otp_input != str(stored_otp):
        #     messages.error(request, "Invalid OTP. Please try again.")
        #     return render(request, 'customer_registration.html')

 # Validate OTP from session storage
        stored_otp = request.session.get('otp')
        if not stored_otp or otp_input != str(stored_otp):
            messages.error(request, "Invalid OTP. Please try again.")
            return render(request, 'customer_registration.html')
        # Validate password match
        if password != confirm_password:
            messages.error(request, "Passwords do not match. Please try again.")
            return render(request, 'customer_registration.html')

        # Check if email already exists
        if Customer.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return render(request, 'customer_registration.html')

        # Save the new customer with hashed password
        customer = Customer(
            full_name=full_name,
            mobile_number=mobile,
            email=email,
            password=make_password(password)  # Hashing password for security
        )
        customer.save()

        # Clear OTP after successful registration
        del request.session['otp']

        messages.success(request, "Registration successful! You can now log in.")
        return redirect('customer_login')

    return render(request, 'customer_registration.html')


def login_view(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        # print(email, password)
        try:
            customer = Customer.objects.get(email=email)
            
            if check_password(password, customer.password):
                # print("Login successful!")
                request.session['customer_id'] = customer.id
                request.session['customer_name'] = customer.full_name
                messages.success(request, "Login successful.")
                return redirect('home')
            else:
                messages.error(request, "Invalid password.")
                return render(request, 'customer_login.html')
        except Customer.DoesNotExist:
            messages.error(request, "Email not found. Please register.")
            return render(request, 'customer_login.html')
    
    return render(request, 'customer_login.html')

def logout_view(request):
    if 'customer_id' in request.session:
        del request.session['customer_id']
        del request.session['customer_name']
        messages.success(request, "Logged out successfully.")
    return redirect('home')






#@csrf_exempt  # Use only if CSRF issues occur, but not recommended for production
import random
import smtplib
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache  # Store OTP temporarily
from django.core.mail import send_mail
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
def send_otp(request):
    if request.method == "POST":
        email = request.POST.get("email")

        if not email:
            return JsonResponse({"status": "error", "message": "Email is required."})

        # Generate a 6-digit OTP
        otp = random.randint(100000, 999999)
        print(otp)

        # Store OTP in cache for 5 minutes (or use your preferred method)
        cache.set(email, otp, timeout=300)

        # Send OTP via Email
        try:
            send_mail(
                "Your OTP Code",
                f"Your OTP code is {otp}. It is valid for 5 minutes.",
                "khairnarakshay1722@gmail.com",  # Replace with your sender email
                [email],
                fail_silently=False,
            )
            return JsonResponse({"status": "sent"})
        except smtplib.SMTPException as e:
            logger.error(f"SMTP Error: {e}")  # Logs error details
            return JsonResponse({"status": "error", "message": f"Failed to send OTP: {str(e)}"})

    return JsonResponse({"status": "error", "message": "Invalid request"})


@csrf_exempt
def validate_otp(request):
    if request.method == "POST":
        email = request.POST.get("email")
        user_otp = request.POST.get("otp")
        print(f'user otp',{user_otp})
        if not email or not user_otp:
            return JsonResponse({"status": "error", "message": "Email and OTP are required."})

        stored_otp = cache.get(email)  # Retrieve OTP from cache
        print(f'Stored OTP: {stored_otp}')
        if stored_otp is None:
            return JsonResponse({"status": "error", "message": "OTP expired or not found."})

        if str(stored_otp) == str(user_otp):
            cache.delete(email)  # Remove OTP after successful verification
            print('in if block.')
            return JsonResponse({"status": "success", "message": "OTP verified successfully."})
        
        else:
            print('in else block')
            return JsonResponse({"status": "error", "message": "Invalid OTP."})

    return JsonResponse({"status": "error", "message": "Invalid request method."})



def check_email_exists(request):
    if request.method == "POST":
        email = request.POST.get("email")
        if Customer.objects.filter(email=email).exists():
            return JsonResponse({"status": "exists", "message": "Email already registered!"})
        else:
            return JsonResponse({"status": "available"})
    return JsonResponse({"status": "error", "message": "Invalid request"})