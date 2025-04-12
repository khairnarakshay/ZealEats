from django.shortcuts import render
from vendor.models import FoodItem , CanteenVendor
from customer.models import Customer 
from .models import ContactUs
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
# Create your views here.
# def home(request):
#     food_items = FoodItem.objects.all()
#     customer_name = request.session.get('customer_name','')
#     context = {'user_logged_in': request.session.get('user_id') is not None}
#     print(food_items)
    
#     # Pass both context variables in a single dictionary
#     return render(request, 'home.html', {'food_items': food_items, 'customer_name': customer_name, 'context': context})
def home(request):
    food_items = FoodItem.objects.all()
    customer_name = request.session.get('customer_name', '')
    user_logged_in = request.session.get('user_id') is not None

    # Merge all variables in a single context dictionary
    context = {
        'food_items': food_items,
        'customer_name': customer_name,
        'user_logged_in': user_logged_in
    }

    return render(request, 'home.html', context)


def MyCart(request):
    return render(request, 'mycart.html')

def MyOrder(request):
    return render(request, 'myorder.html')


def AboutUs(request):
    return render(request, 'aboutus.html')


from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib import messages

from django.conf import settings

from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from .models import ContactUs
import re

def Contactus(request):
    if request.method == 'POST':
        # Get form data from POST
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        # Validate required fields
        if not name or not email or not subject or not message:
            messages.error(request, 'All fields are required.')
            return render(request, 'contactus.html')

        # Validate email format
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            messages.error(request, 'Please enter a valid email address.')
            return render(request, 'contactus.html')

        # Save the contact form data to the database
        ContactUs.objects.create(name=name, email=email, subject=subject, message=message)

        # Send a thank-you email to the user
        send_mail(
            subject=f'Thank You for Contacting Us',
            message=f'{name} We have received your message and will get back to you shortly.',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
        )

        # Show a success message
        messages.success(request, 'Thank you for contacting us! We will get back to you shortly.')

        # Redirect to a success page or show the success message on the same page
       # return redirect('success_page')  # Optionally, change to your desired redirect URL

    return render(request, 'contactus.html')





