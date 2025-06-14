from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import make_password, check_password
import random
from .models import Customer,Cart,CartItem
from vendor.models import FoodItem
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import check_password
from django.shortcuts import redirect, get_object_or_404
from vendor.models import FoodItem 
from . models import  CartItem
from django.contrib.auth.decorators import login_required

from django.utils.crypto import get_random_string
from django.contrib.auth.tokens import default_token_generator
from .models import Customer
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import smart_bytes
from django.utils.timezone import now
from datetime import timedelta
from .models import Cart, CartItem, Order
from decimal import Decimal, InvalidOperation
import re

def registration_view(request):
    if request.method == "POST":
        full_name = request.POST.get('full_name')
        mobile = request.POST.get('mobile')
        email = request.POST.get('email')
        otp_input = request.POST.get('otp')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

       
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
        cache.delete(email)  # Delete OTP from cache after successful registration

        messages.success(request, "Registration successful! You can now log in.")
        return redirect('customer_login')

    return render(request, 'customer_registration.html')

def update_profile(request):
    # Retrieve the customer using email (assuming email is unique)
    customer_id = request.session.get('customer_id')
    customer = Customer.objects.get(id=customer_id)
    
    
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        mobile = request.POST.get('mobile')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password and password != confirm_password:
            messages.error(request, "Passwords do not match!")
        else:
            # ✅ Corrected field assignment
            customer.full_name = full_name  
            customer.mobile_number = mobile  
            if password:
                customer.password = make_password(password)   # Store securely in real cases
            customer.save()
            
            request.session['customer_name'] = customer.full_name  # Update session

            messages.success(request, "Profile updated successfully!")
            return redirect('update_profile')

    
    return render(request, 'update_profile.html', {'customer': customer})

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
                print("Session data:", request.session.items())
                messages.success(request, "Login successful.")
                  # Print session data for debugging
                print("Session data:", request.session.get('customer_id'))
                print("Customer name from session:", request.session.get('customer_name'))
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
        print('logout session clear from session', request.session.keys())
        messages.success(request, "Logged out successfully.")
    return redirect('home')



# Forgot Password View (Email Entry and OTP Generation)
def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            # Assuming you have a Customer model
            customer = Customer.objects.get(email=email)
            
            # Generate OTP (For simplicity, 6-digit random number)
            otp = get_random_string(length=6, allowed_chars='0123456789')

            # Store OTP in session or cache for validation
            request.session['otp'] = otp
            request.session['email'] = email

            # Send OTP to user's email
            send_mail(
                'Password Reset OTP',
                f'Your OTP for password reset is: {otp}',
                'noreply@yourdomain.com',
                [email],
                fail_silently=False,
            )

            messages.success(request, 'OTP has been sent to your email!')
            return redirect('reset_password')
        except Customer.DoesNotExist:
            messages.error(request, 'No account found with this email.')
            return redirect('forgot_password')

    return render(request, 'forgot_password.html')


# Reset Password View (OTP Validation and Password Reset)
def reset_password(request):
    if request.method == 'POST':
        otp = request.POST.get('otp')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        # Validate OTP
        if otp != request.session.get('otp'):
            messages.error(request, 'Invalid OTP!')
            return render(request, 'reset_password.html')

        # Check if passwords match
        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match!')
            return render(request, 'reset_password.html')

        # Reset password for the customer
        try:
            customer = Customer.objects.get(email=request.session.get('email'))
            customer.password=make_password(new_password)  # Update password
            customer.save()

            messages.success(request, 'Password has been reset successfully!')
            return redirect('customer_login')  # Redirect to login page after successful password reset
        except Customer.DoesNotExist:
            messages.error(request, 'Customer not found.')
            return redirect('forgot_password')

    return render(request, 'reset_password.html')


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
        print("sending a OTP :",otp)

        # Store OTP in cache for 5 minutes (or use your preferred method)
        cache.set(email, otp, timeout=300)

        # Send OTP via Email
        try:
            send_mail(
                "Your OTP Code For ZEAL College Canteen Registration",
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


# def validate_otp(request):
#     if request.method == "POST":
#         email = request.POST.get("email")
#         user_otp = request.POST.get("otp")
#         print(f'user otp',{user_otp})
#         if not email or not user_otp:
#             return JsonResponse({"status": "error", "message": "Email and OTP are required."})

#         stored_otp = cache.get(email)  # Retrieve OTP from cache
#         print(f'Stored OTP: {stored_otp}')
#         if stored_otp is None:
#             return JsonResponse({"status": "error", "message": "OTP expired or not found."})

#         if str(stored_otp) == str(user_otp):
#             cache.delete(email)  # Remove OTP after successful verification
#             print('in if block.')
#             return JsonResponse({"status": "success", "message": "OTP verified successfully."})
        
#         else:
#             print('in else block')
#             return JsonResponse({"status": "error", "message": "Invalid OTP."})

#     return JsonResponse({"status": "error", "message": "Invalid request method."})


@csrf_exempt
@csrf_exempt
def validate_otp(request):
    if request.method == "POST":
        email = request.POST.get("email")
        user_otp = request.POST.get("otp")

        if not email or not user_otp:
            return JsonResponse({"status": "error", "message": "Email and OTP are required."})

        stored_otp = cache.get(email)  # Retrieve OTP from cache
        
        print(f"User Input OTP: {user_otp}, Type: {type(user_otp)}")
        print(f"Stored OTP: {stored_otp}, Type: {type(stored_otp)}")

        if stored_otp is None:
            return JsonResponse({"status": "error", "message": "OTP expired or not found."})

        # ✅ Convert both values to strings before comparison
        if str(stored_otp) == str(user_otp):
            cache.delete(email)  # Remove OTP after successful verification
            return JsonResponse({"status": "success", "message": "OTP verified successfully."})
        else:
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




# Add to cart functionality


# def add_to_cart(request, food_id):
#     # Check if the user is logged in (based on your custom session handling)
#     if 'customer_id' not in request.session:
#         return redirect('/customer/login/')  # Redirect to your custom login page

#     customer_id = request.session['customer_id']
#     customer = get_object_or_404(Customer, id=customer_id)
#     food_item = get_object_or_404(FoodItem, id=food_id)

#     # Retrieve or create a cart for the customer
#     cart, created = Cart.objects.get_or_create(user=customer)

#     # Check if the item already exists in the cart
#     cart_item, created = CartItem.objects.get_or_create(cart=cart, food_item=food_item)

#     if not created:
#         cart_item.quantity += 1
#         cart_item.save()

#     return redirect('view_cart')  # Redirect to the cart page after adding an item

# @login_required
# def view_cart(request):
#     if request.user.is_authenticated:
#         cart, created = Cart.objects.get_or_create(user=request.user)
#     else:
#         cart = Cart.objects.get_or_create(user=None)  # For guest users

#     cart_items = cart.cart_items.all()
#     total_price = cart.total_price()

#     return render(request, 'cart.html', {'cart_items': cart_items, 'total_price': total_price})
# @login_required
# def update_cart(request):
#     if request.method == 'POST':
#         food_id = request.POST.get('food_id')
#         new_quantity = int(request.POST.get('quantity'))

#         cart_item = get_object_or_404(CartItem, user=request.user, food_item_id=food_id)
#         cart_item.quantity = new_quantity
#         cart_item.save()

#         total_price = sum(item.food_item.price * item.quantity for item in CartItem.objects.filter(user=request.user))

#         return JsonResponse({
#             'total_amount': cart_item.food_item.price * new_quantity,
#             'total_price': total_price
#         })


# @login_required
# def remove_item(request):
#     if request.method == 'POST':
#         food_id = request.POST.get('food_id')

#         cart_item = CartItem.objects.filter(user=request.user, food_item_id=food_id)
#         if cart_item.exists():
#             cart_item.delete()

#         total_price = sum(item.food_item.price * item.quantity for item in CartItem.objects.filter(user=request.user))

#         return JsonResponse({'message': 'Item removed', 'total_price': total_price})


from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import FoodItem  # Import your FoodItem model

# 🚀 ADD TO CART
# def add_to_cart(request, food_id):
#     if not request.session.get('customer_id'):
#         print('customer id in add to cart', request.session.get('customer_id'))
#         return redirect('customer_login')  # Redirect to login page if customer is not authenticated
    
#     # Get the food item
#     food_item = FoodItem.objects.get(id=food_id)
#     food_name = food_item.food_name
#     print("Food Item:", food_item)
#     print("Food Itme ADDED TO CART" , food_name)
#     quantity = int(request.POST.get('quantity', 1))

#     # Get or create the customer's cart
#     customer_id = request.session.get('customer_id')
#     customer = Customer.objects.get(id=customer_id)
#     print('customer found', customer_id)
#     cart, created = Cart.objects.get_or_create(customer=customer)

#     # Check if the food item is already in the cart
#     try:
#         cart_item, created = CartItem.objects.get_or_create(cart=cart, food_item=food_item) 
#         print("cart_item:", cart_item)
        
#         if created:
#             # If the item was not in the cart, set the initial quantity and price
#             cart_item.quantity = quantity
#             cart_item.price = food_item.price
#         else:
#             # If the item is already in the cart, update the quantity
#             cart_item.quantity += quantity
        
#         cart_item.save()
#     except Exception as e:
#         print('Error in cart item:', e)
#         return redirect('view_cart')  # You can redirect to the cart view or show an error message

#     return redirect('view_cart')  # Redirect to the cart view

def add_to_cart(request, food_id):
    if not request.session.get('customer_id'):
        messages.error(request, "You must need to login to view cart!")
        return redirect('customer_login')  # Redirect to login page if customer is not authenticated
    
    # Get the food item
    food_item = get_object_or_404(FoodItem, id=food_id)
    quantity = int(request.POST.get('quantity', 1))

    # Get or create the customer's cart
    customer_id = request.session.get('customer_id')
    customer = get_object_or_404(Customer, id=customer_id)
    cart, created = Cart.objects.get_or_create(customer=customer)
    print('ca__',cart)
    print('customer found', customer_id)
    print("Food Item:", food_item)
    

    # Check if the food item is already in the cart
    try:
        cart_item, created = CartItem.objects.get_or_create(cart=cart, food_item=food_item) 
        print("cart_item:", cart_item)
        if created:
            # If the item was not in the cart, set the initial quantity and price
            cart_item.quantity = quantity
            cart_item.price = food_item.price
            
        else:
            # If the item is already in the cart, update the quantity
            cart_item.quantity += quantity
        
        # Save the cart item
        
        cart_item.save()
        print("cart item saved")
        print("cart item", cart_item)
    except Exception as e:
        print('Error in cart item:', e)
        return redirect('view_cart')  # Redirect to the cart view or show an error message

    return redirect('view_cart')  # Redirect to the cart view



# 📦 VIEW CART
# def view_cart(request):
#     # Get the logged-in customer
#     customer_id = request.session.get('customer_id')
#     if not customer_id:
#         return redirect('customer/login')

#     customer = get_object_or_404(Customer, id=customer_id)

#     # Get the customer's cart
#     # try:
#     #     cart = Cart.objects.get(customer=customer)
#     # except Cart.DoesNotExist:
#     #     cart = None  # If the cart doesn't exist, you can handle it accordingly
    
#     # return render(request, 'view_cart.html', {'cart': cart})
#     cart = Cart.objects.filter(customer=customer).first()
#     cart_items = cart.items.all() if cart else []  # Ensure we pass an empty list if no cart exists
#     return render(request, 'view_cart.html', {'cart': cart, 'cart_items': cart_items})


# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import Cart, CartItem

def view_cart(request):
    customer_id = request.session.get('customer_id')
    
    if not customer_id:
        messages.error(request, "You must need to login to view cart!")
        return redirect('customer_login')

    customer = get_object_or_404(Customer, id=customer_id)
    cart = Cart.objects.filter(customer=customer).first()
    cart_items = cart.items.order_by('-id') if cart else []
    #cart_items = cart.items.all() if cart else []

    # Calculate the total price for each cart item
    for cart_item in cart_items:
        cart_item.total_price = cart_item.quantity * cart_item.food_item.price

    return render(request, 'view_cart.html', {'cart': cart, 'cart_items': cart_items})



# ✏️ UPDATE CART ITEM QUANTITY
# def update_cart(request):
#     if request.method == 'POST':
#         print("update cart request........")
#         cart_item_id = request.POST.get('cart_item_id')
#         action = request.POST.get('action')  # 'increase' or 'decrease'

#         cart_item = get_object_or_404(CartItem, id=cart_item_id)

#         if action == 'increase':
#             cart_item.quantity += 1
#         elif action == 'decrease' and cart_item.quantity > 1:
#             cart_item.quantity -= 1

#         cart_item.save()

#         # Return the updated quantity and the total price for the cart item
#         return JsonResponse({
#             'quantity': cart_item.quantity,
#             'total_price': cart_item.total_price(),  # Ensure `total_price` method exists on the CartItem model
#         })

#     return JsonResponse({'error': 'Invalid request'}, status=400)
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import CartItem
from django.views.decorators.csrf import csrf_exempt

def update_cart(request, cart_item_id):
    if request.method == "POST":
        action = request.POST.get("action")  # "increase" or "decrease"
        cart_item = get_object_or_404(CartItem, id=cart_item_id)

        if action == "increase":
            cart_item.quantity += 1
        elif action == "decrease" and cart_item.quantity > 1:
            cart_item.quantity -= 1

        cart_item.save()
        return redirect('view_cart')  # Redirect back to the cart page

    return JsonResponse({"success": False, "error": "Invalid request"})


def remove_from_cart(request, cart_item_id):
    if request.method == "POST":
        cart_item = get_object_or_404(CartItem, id=cart_item_id)
        cart_item.delete()
        return redirect('view_cart')  # Redirect back to cart after deletion

    return JsonResponse({"success": False, "error": "Invalid request"})

# def place_order(request):
#     customer_id = request.session.get("customer_id")
    
#     if not customer_id:
#         messages.error(request, "You must be logged in to place an order.")
#         return redirect("customer_login")

#     customer = get_object_or_404(Customer, id=customer_id)
#     print("Customer Name:", customer.full_name)
    
#     cart = Cart.objects.filter(customer=customer).first()

#     if not cart or not cart.items.exists():
#         messages.error(request, "Your cart is empty. Add items before ordering.")
#         return redirect("view_cart")

#     if request.method == "POST":
#         payment_method = request.POST.get("payment_method")
#         total_amount = request.POST.get("total_amount")
        
#         # Use get to retrieve the comma-separated string and split it into a list
#         selected_cart_item_ids = request.POST.get("selected_item_ids", "").split(",")
#         print("Selected Cart Item IDs (frontend):", selected_cart_item_ids)

#         # Filter out empty strings and non-integer values
#         selected_cart_item_ids = [item_id for item_id in selected_cart_item_ids if item_id.isdigit()]
#         print("Selected Cart Item IDs (backend):", selected_cart_item_ids)

#         if not selected_cart_item_ids:
#             messages.error(request, "No valid items selected. Please add items to the cart before placing an order.")
#             return redirect("view_cart")

#         try:
#             total_amount = Decimal(total_amount)
#         except:
#             messages.error(request, "Invalid amount format.")
#             return redirect("view_cart")

#         if not payment_method:
#             messages.error(request, "Please select a payment method.")
#             return redirect("view_cart")

#         # Process card details if Card payment is selected
#         if payment_method == "Card":
#             card_number = request.POST.get("card_number", "").strip()
#             card_holder = request.POST.get("card_holder", "").strip()
#             expiry_date = request.POST.get("expiry_date", "").strip()
#             cvv = request.POST.get("cvv", "").strip()

#             if len(card_number) != 16 or not card_number.isdigit():
#                 messages.error(request, "Invalid Card Number.")
#                 return redirect("view_cart")

#             if not card_holder:
#                 messages.error(request, "Card Holder Name is required.")
#                 return redirect("view_cart")

#             if not expiry_date or not re.match(r"^(0[1-9]|1[0-2])\/\d{2}$", expiry_date):
#                 messages.error(request, "Invalid Expiry Date format (MM/YY).")
#                 return redirect("view_cart")

#             if len(cvv) != 3 or not cvv.isdigit():
#                 messages.error(request, "Invalid CVV.")
#                 return redirect("view_cart")

#         # Process only selected cart items
#         for cart_item in cart.items.filter(id__in=selected_cart_item_ids):
#             vendor = cart_item.food_item.vendor  # This retrieves the CanteenVendor instance
#             new_order = Order.objects.create(
#                 customer=customer,
#                 food_item=cart_item.food_item,
#                 quantity=cart_item.quantity,
#                 price=cart_item.price,
#                 restaurant_name=cart_item.food_item.vendor.restaurant_name,
#                 total_amount=cart_item.price * cart_item.quantity,
#                 payment_method=payment_method,
#                 order_status="Pending",
#                 payment_status="Pending",
#                 is_paid=(payment_method == "Card"),
#                # vendor=cart_item.food_item.vendor.id,  # Assuming you have a vendor field in your Order model
#                vendor=vendor,  # Link to the vendor
#             )

#             print(f"Order Created: {new_order.id} for {cart_item.food_item.food_name}")
#             cart_item.delete()  # Remove the cart item after order is created

#         messages.success(request, "Order placed successfully!")
#         return redirect("order_success")

from decimal import Decimal
import re
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.db import transaction
from .models import Customer, Cart, Order  # Adjust imports as per your project structure


def place_order(request):
    customer_id = request.session.get("customer_id")
    
    if not customer_id:
        messages.error(request, "You must be logged in to place an order.")
        return redirect("customer_login")

    customer = get_object_or_404(Customer, id=customer_id)
    print("Customer Name:", customer.full_name)

    cart = Cart.objects.filter(customer=customer).first()

    if not cart or not cart.items.exists():
        messages.error(request, "Your cart is empty. Add items before ordering.")
        return redirect("view_cart")

    if request.method == "POST":
        payment_method = request.POST.get("payment_method")
        total_amount = request.POST.get("total_amount", "0")

        selected_cart_item_ids = request.POST.get("selected_item_ids", "").split(",")
        selected_cart_item_ids = [item_id for item_id in selected_cart_item_ids if item_id.isdigit()]
        print("Selected Cart Item IDs:", selected_cart_item_ids)

        if not selected_cart_item_ids:
            messages.error(request, "No valid items selected. Please add items to the cart before placing an order.")
            return redirect("view_cart")

        try:
            total_amount = Decimal(total_amount)
        except:
            messages.error(request, "Invalid amount format.")
            return redirect("view_cart")

        if not payment_method:
            messages.error(request, "Please select a payment method.")
            return redirect("view_cart")

        if payment_method == "Card":
            card_number = request.POST.get("card_number", "").strip()
            card_holder = request.POST.get("card_holder", "").strip()
            expiry_date = request.POST.get("expiry_date", "").strip()
            cvv = request.POST.get("cvv", "").strip()

            if len(card_number) != 16 or not card_number.isdigit():
                messages.error(request, "Invalid Card Number.")
                return redirect("view_cart")

            if not card_holder:
                messages.error(request, "Card Holder Name is required.")
                return redirect("view_cart")

            if not expiry_date or not re.match(r"^(0[1-9]|1[0-2])\/\d{2}$", expiry_date):
                messages.error(request, "Invalid Expiry Date format (MM/YY).")
                return redirect("view_cart")

            if len(cvv) != 3 or not cvv.isdigit():
                messages.error(request, "Invalid CVV.")
                return redirect("view_cart")

        selected_items = cart.items.filter(id__in=selected_cart_item_ids)
        if not selected_items.exists():
            messages.error(request, "No matching items found in the cart.")
            return redirect("view_cart")

        order_list = []

        with transaction.atomic():
            for cart_item in selected_items:
                vendor = cart_item.food_item.vendor
                new_order = Order.objects.create(
                    customer=customer,
                    food_item=cart_item.food_item,
                    quantity=cart_item.quantity,
                    price=cart_item.price,
                    restaurant_name=vendor.restaurant_name,
                    total_amount=cart_item.price * cart_item.quantity,
                    payment_method=payment_method,
                    order_status="Pending",
                    payment_status="Pending",
                    is_paid=(payment_method == "Card"),
                    vendor=vendor,
                )
                order_list.append(new_order)
                cart_item.delete()

        # Assuming order_list contains all the orders, and each order has food_item, quantity, and price
        order_details = "\n".join([f"{order.food_item.food_name}(Qty: {order.quantity}) - ₹{order.price * order.quantity}" for order in order_list])

        # Calculate total amount dynamically for all items in the cart
        total_final_amount = sum(order.price * order.quantity for order in order_list)

        # Pass the updated total amount and order details to the template



        email_subject = "Your Order Confirmation"
        email_body = f"""Hello {customer.full_name},

Thank you for your order! Here are your order details:
Order ID: {order_list[0].id}
{order_details}

Total Amount: ₹{total_final_amount}
Payment Method: {payment_method}
Order Status: Pending

We'll notify you once your order is confirmed.

Best regards,
{vendor.restaurant_name}
ZealEats Team
Zeal College Canteen
"""

        send_mail(
            email_subject,
            email_body,
            "khairnarakshay1722@gmail.com",  # Replace with settings.DEFAULT_FROM_EMAIL if needed
            [customer.email],
            fail_silently=False,
        )

        messages.success(request, "Order placed successfully!")
        return redirect("order_success")

    messages.error(request, "Invalid request method.")
    return redirect("view_cart")

    
    
def view_orders(request):
    customer_id = request.session.get('customer_id')
    print("cusomer", customer_id)
    if not customer_id:
        messages.error(request, "You must be logged in to view your orders.")
        return redirect('customer_login')

    customer = get_object_or_404(Customer, id=customer_id)
    print( 'cusomer in view order')
    orders = Order.objects.filter(customer=customer).order_by('-order_date')  # Get all orders for the customer
    
    return render(request, 'view_orders.html', {'orders': orders})

def order_details(request, order_id):
    print("order id", order_id)
    order = get_object_or_404(Order, id=order_id)
    items = CartItem.objects.filter(order=order)  # Ensure you have a relationship set up

    order_data = {
        'order_date': order.order_date,
        'total_amount': order.total_amount,
        'payment_method': order.payment_method,
        'items': []
    }
    
    for item in items:
        order_data['items'].append({
            'food_item': {
                'food_name': item.food_item.food_name,
                'image': item.food_item.image.url,  # Ensure this field exists
            },
            'price': item.price,
            'quantity': item.quantity,
            'total_price': item.total_price()
        })
    
    return JsonResponse(order_data)

def print_order_details(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    #items = order.items.all()  # Assuming you have a related name for items in the Order model

    return render(request, 'print_order.html', {'order': order,})

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Order  # Adjust the import based on your models
def cancel_order(request, order_id):
    """Handles order cancellation for authenticated users only."""
    if request.method == "POST":
        # Ensure the user is authenticated via session
        customer_id = request.session.get('customer_id')
        if not customer_id:  # Check if customer_id is in the session
            messages.error(request, "You must be logged in to cancel an order.")
            return redirect(request.META.get('HTTP_REFERER', '/'))  # Redirect to the previous page or home

        # Get the order and check if it belongs to the logged-in user
        order = get_object_or_404(Order, id=order_id, customer_id=customer_id)

        # Allow cancellation only if it's not shipped/delivered
        if order.order_status in ["Pending", "Processing"]:
            order.order_status = "Cancelled"
            order.save()
            messages.success(request, "Order cancelled successfully!")
        else:
            messages.error(request, "This order cannot be cancelled.")

        return redirect(request.META.get('HTTP_REFERER', '/'))  # Redirect to the previous page or home

    messages.error(request, "Invalid request.")
    return redirect(request.META.get('HTTP_REFERER', '/'))  # Redirect to the previous page or home

def order_success(request):
    return render(request, 'order_success.html')