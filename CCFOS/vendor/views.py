from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages
from .models import CanteenVendor, FoodItem
from django.contrib.auth import logout as auth_logout  # Keep logout for admin
from django.contrib.auth.decorators import login_required
from customer.models import Order 
from django.db.models import Sum, Count
from django.utils.timezone import now, timedelta
from datetime import datetime, timedelta
import io
import xlsxwriter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from django.template.loader import render_to_string

# def admin_logout(request):
#     if request.user.is_authenticated and request.user.is_superuser:
#         auth_logout(request)  # Logs out only admin users
#         messages.success(request, "Admin logged out successfully.")
#         return redirect('/admin/login/')  # Redirect to admin login
#     return redirect("dashboard")  # Prevent logging out vendors


def register_view(request):
    if request.method == 'POST':
        full_name = request.POST['full_name']
        restaurant_name = request.POST['restaurant_name']
        mobile_number = request.POST['mobile']
        store_description = request.POST['description']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        # Password matching check
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'registration.html', {
                'full_name': full_name,
                'restaurant_name': restaurant_name,
                'mobile_number': mobile_number,
                'store_description': store_description
            })

        # Check if mobile number already exists
        if CanteenVendor.objects.filter(mobile_number=mobile_number).exists():
            messages.error(request, "Mobile number already registered.")
            return render(request, 'registration.html', {
                'full_name': full_name,
                'restaurant_name': restaurant_name,
                'mobile_number': mobile_number,
                'store_description': store_description
            })

        # Hash password before storing
        hashed_password = make_password(password)

        # Create and save the vendor to the database
        vendor = CanteenVendor(
            full_name=full_name,
            restaurant_name=restaurant_name,
            mobile_number=mobile_number,
            store_description=store_description,
            password=hashed_password
        )
        vendor.save()

        messages.success(request, "Registration successful! You can now log in.")
        return redirect('login')  # Redirect to login page after successful registration

    return render(request, 'registration.html')

def vendor_login(request):
    if request.method == "POST":
        mobile_number = request.POST["mobile"]
        password = request.POST["password"]

        try:
            vendor = CanteenVendor.objects.get(mobile_number=mobile_number)

            if not vendor.is_approved:
                messages.error(request, "Your account is not approved by the admin.")
                return render(request, "login.html")
            
            if check_password(password, vendor.password):
                request.session["vendor_id"] = vendor.id
                print(vendor.id)
                request.session["vendor_name"] = vendor.full_name
                print(request.session["vendor_name"])
                messages.success(request, "Login successful.")
                return redirect("dashboard")  # Redirect vendors only

            else:
                messages.error(request, "Invalid password.")
                return render(request, "login.html")

        except CanteenVendor.DoesNotExist:
            messages.error(request, "Vendor does not exist.")
            return render(request, "login.html")

    return render(request, "login.html")

#@login_required
def dashboard(request):
    if "vendor_id" not in request.session:
        messages.error(request, "You must be logged in to access the dashboard.")
        return redirect("login")
    else:
        vendor_id = request.session["vendor_id"]
        vendor = CanteenVendor.objects.get(id=vendor_id)
        all_orders = Order.objects.filter(vendor=vendor).order_by('-updated_at')
        completed_orders = Order.objects.filter(order_status='Completed', vendor=vendor)
        cancelled_orders = Order.objects.filter(order_status='Cancelled', vendor=vendor)
        pending_orders = Order.objects.filter(order_status='Pending', vendor=vendor)

        context = {
            'all_orders': all_orders,
            'completed_orders':  completed_orders,
            'cancelled_orders': cancelled_orders,
            'pending_orders': pending_orders,
            'vendor_name': request.session.get("vendor_name", "Default Vendor") 
        }
        orders = Order.objects.all()
        print(orders)
        return render(request, 'vendor_dashboard.html', context, )
    
from django.utils.dateparse import parse_date
# def admin_statistics(request):
#     vendor_id = request.session.get('vendor_id')
#     today = datetime.now().date()
#     week_ago = today - timedelta(days=7)
#     month_ago = today - timedelta(days=30)

#     completed_orders = Order.objects.filter(order_status='Completed', vendor_id=vendor_id)
#    #get date from frontend
#     first_order_date = Order.objects.filter(vendor_id=vendor_id).aggregate(Min('order_date'))['order_date__min']
#     first_order_date = first_order_date.date() if first_order_date else today

#     # Get dates from user input (GET parameters)
#     from_date_str = request.GET.get('from_date')
#     to_date_str = request.GET.get('to_date')
#     from_date = parse_date(from_date_str) if from_date_str else first_order_date
#     to_date = parse_date(to_date_str) if to_date_str else today
    
#     # Totals
#     daily_total = completed_orders.filter(order_date__date=today).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
#     weekly_total = completed_orders.filter(order_date__date__gte=week_ago).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
#     monthly_total = completed_orders.filter(order_date__date__gte=month_ago).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
#     total_collection = completed_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
#     total_orders = completed_orders.count()
    
#     today_orders = Order.objects.filter(order_date__date=today , vendor_id=vendor_id)  # Today's orders for the logged-in vendor

#     # Today's completed and cancelled count
#     today_completed_count = today_orders.filter(order_status='Completed').count()
#     today_cancelled_count = today_orders.filter(order_status='Cancelled').count()
#     today_total_count = today_orders.count()

#     # Graph data (last 7 days)
#     delta = (to_date - from_date).days + 1
#     labels = []
#     data_values = []

#     for i in range(7):
#         day = today - timedelta(days=i)
#         total = completed_orders.filter(order_date__date=day).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
#         labels.append(day.strftime('%d %b'))  # e.g., "06 Apr"
#         data_values.append(float(total))

#     labels.reverse()
#     data_values.reverse()
    
#     food_stats = (
#         Order.objects
#         .filter(order_status='Completed',updated_at__date=now().date(), vendor_id=vendor_id)
#         .values('food_item__food_name')
#         .annotate(
#             total_earned=Sum('total_amount'),
#             total_quantity=Sum('quantity')
#         )
#         .order_by('-total_earned')
#     )
    
#     # Prepare labels and data for the bar graph
#     food_labels = [item['food_item__food_name'] for item in food_stats]
#     food_data = [item['total_quantity'] for item in food_stats]
    
    
#     context = {
#         'daily_total': daily_total,
#         'weekly_total': weekly_total,
#         'monthly_total': monthly_total,
#         'total_collection': total_collection,
#         'total_orders': total_orders,
#         'graph_labels': labels,
#         'graph_data': data_values,
#         'food_stats': food_stats, 
#         'food_labels': food_labels,
#         'food_data': food_data,
#         'today_total_count': today_total_count,
#         'today_completed_count': today_completed_count,
#         'today_cancelled_count': today_cancelled_count,
#     }

#     return render(request, 'admin_statistics.html', context)

from django.utils.dateparse import parse_date
from django.db.models import Sum, Min
from django.shortcuts import render
from datetime import datetime, timedelta


# def admin_statistics(request):
#     vendor_id = request.session.get('vendor_id')
#     today = datetime.now().date()

#     # Fetch all completed orders for this vendor
#     completed_orders = Order.objects.filter(order_status='Completed', vendor_id=vendor_id)

#     # Get first order date
#     first_order_date = completed_orders.aggregate(Min('order_date'))['order_date__min']
#     first_order_date = first_order_date.date() if first_order_date else today

#     # Date filter
#     from_date_str = request.GET.get('from_date')
#     to_date_str = request.GET.get('to_date')
#     show_all = request.GET.get('show_all')
    
#     if show_all == '1':
#         from_date = None
#         to_date = None
#     elif from_date_str and to_date_str:
#         from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date()
#         to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date()
#     else:
#         to_date = today
#         from_date = today - timedelta(days=6)

#     from_date = parse_date(from_date_str) if from_date_str else today - timedelta(days=6)  # Default last 7 days
#     to_date = parse_date(to_date_str) if to_date_str else today

#     # Line Chart Data (sales over time)
#     delta = (to_date - from_date).days + 1
#     line_labels = []
#     line_data = []

#     for i in range(delta):
#         day = from_date + timedelta(days=i)
#         total = completed_orders.filter(order_date__date=day).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
#         line_labels.append(day.strftime('%d %b'))
#         line_data.append(float(total))

#     # Bar Chart Data (top food items sold)
#     bar_filtered_orders = completed_orders.filter(order_date__date__range=(from_date, to_date))
#     food_stats = (
#         bar_filtered_orders
#         .values('food_item__food_name')
#         .annotate(
#             total_earned=Sum('total_amount'),
#             total_quantity=Sum('quantity')
#         )
#         .order_by('-total_earned')
#     )
#     bar_labels = [item['food_item__food_name'] for item in food_stats]
#     bar_data = [item['total_quantity'] for item in food_stats]

#     # Summary stats
#     daily_total = completed_orders.filter(order_date__date=today).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
#     weekly_total = completed_orders.filter(order_date__date__gte=today - timedelta(days=7)).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
#     monthly_total = completed_orders.filter(order_date__date__gte=today - timedelta(days=30)).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
#     total_collection = completed_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
#     total_orders = completed_orders.count()

#     today_orders = Order.objects.filter(order_date__date=today, vendor_id=vendor_id)
#     today_completed_count = today_orders.filter(order_status='Completed').count()
#     today_cancelled_count = today_orders.filter(order_status='Cancelled').count()
#     today_total_count = today_orders.count()

#     context = {
#         'daily_total': daily_total,
#         'weekly_total': weekly_total,
#         'monthly_total': monthly_total,
#         'total_collection': total_collection,
#         'total_orders': total_orders,
#         'today_total_count': today_total_count,
#         'today_completed_count': today_completed_count,
#         'today_cancelled_count': today_cancelled_count,
#         'food_stats': food_stats,
#         # Charts
#         'graph_labels': line_labels,
#         'graph_data': line_data,
#         'food_labels': bar_labels,
#         'food_data': bar_data,

#         # Form values
#         'from_date': from_date.strftime('%Y-%m-%d'),
#         'to_date': to_date.strftime('%Y-%m-%d'),
#     }

#     return render(request, 'admin_statistics.html', context)

def admin_statistics(request):
    vendor_id = request.session.get('vendor_id')
    today = datetime.now().date()

    # Fetch all completed orders for this vendor
    completed_orders = Order.objects.filter(order_status='Completed', vendor_id=vendor_id)

    # Get first order date
    first_order_date = completed_orders.aggregate(Min('order_date'))['order_date__min']
    first_order_date = first_order_date.date() if first_order_date else today

    # Date filter
    from_date_str = request.GET.get('from_date')
    to_date_str = request.GET.get('to_date')
    show_all = request.GET.get('show_all')

    # Handle date ranges and show_all logic
    if show_all == '1':
        # Show all data by removing date filtering
        completed_orders = Order.objects.filter(order_status='Completed', vendor_id=vendor_id)
        from_date = None  # No date filtering
        to_date = None    # No date filtering
    else:
        if from_date_str and to_date_str:
            from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date()
            to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date()
            completed_orders = Order.objects.filter(order_status='Completed', vendor_id=vendor_id, order_date__date__range=(from_date, to_date))
        else:
            to_date = today
            from_date = today - timedelta(days=6)
            completed_orders = Order.objects.filter(order_status='Completed', vendor_id=vendor_id, order_date__date__range=(from_date, to_date))

    # --- Line Chart Data (sales over time) ---
    if show_all == '1':
        # If "show_all" is selected, show the sales from the first order date to today
        first_order_date = completed_orders.aggregate(Min('order_date'))['order_date__min']
        first_order_date = first_order_date.date() if first_order_date else today
        delta = (today - first_order_date).days + 1  # Days from the first order to today
        line_labels = []
        line_data = []

        for i in range(delta):
            day = first_order_date + timedelta(days=i)
            total = completed_orders.filter(order_date__date=day).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
            line_labels.append(day.strftime('%d %b'))
            line_data.append(float(total))
    else:
        # If a date range is selected, show sales over the specified time period
        delta = (to_date - from_date).days + 1
        line_labels = []
        line_data = []

        for i in range(delta):
            day = from_date + timedelta(days=i)
            total = completed_orders.filter(order_date__date=day).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
            line_labels.append(day.strftime('%d %b'))
            line_data.append(float(total))

    # --- Bar Chart Data (top food items sold) ---
    # Get food item statistics (if show_all is selected, consider all data)
    if show_all == '1':
        # When 'show_all' is enabled, filter all completed orders without date restriction
        bar_filtered_orders = completed_orders
    else:
        # Apply date range filtering if a date range is provided
        bar_filtered_orders = completed_orders.filter(order_date__date__range=(from_date, to_date))

    # Aggregate food item sales
    food_stats = (
        bar_filtered_orders
        .values('food_item__food_name')
        .annotate(
            total_earned=Sum('total_amount'),
            total_quantity=Sum('quantity')
        )
        .order_by('-total_earned')  # Sort by total earnings (highest first)
    )

    # Prepare data for the bar chart
    bar_labels = [item['food_item__food_name'] for item in food_stats]
    bar_data = [item['total_quantity'] for item in food_stats]

    # --- Summary stats ---
    daily_total = completed_orders.filter(order_date__date=today).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    weekly_total = completed_orders.filter(order_date__date__gte=today - timedelta(days=7)).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    monthly_total = completed_orders.filter(order_date__date__gte=today - timedelta(days=30)).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_collection = completed_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_orders = completed_orders.count()

    today_orders = Order.objects.filter(order_date__date=today, vendor_id=vendor_id)
    today_completed_count = today_orders.filter(order_status='Completed').count()
    today_cancelled_count = today_orders.filter(order_status='Cancelled').count()
    today_total_count = today_orders.count()

    # --- Pass everything to the context ---
    context = {
        'daily_total': daily_total,
        'weekly_total': weekly_total,
        'monthly_total': monthly_total,
        'total_collection': total_collection,
        'total_orders': total_orders,
        'today_total_count': today_total_count,
        'today_completed_count': today_completed_count,
        'today_cancelled_count': today_cancelled_count,
        'food_stats': food_stats,
        # Charts
        'graph_labels': line_labels,
        'graph_data': line_data,
        'food_labels': bar_labels,
        'food_data': bar_data,

        # Form values for filtering
        'from_date': from_date.strftime('%Y-%m-%d') if from_date else '',
        'to_date': to_date.strftime('%Y-%m-%d') if to_date else '',
    }

    return render(request, 'admin_statistics.html', context)


    
def vendor_logout(request):
    request.session.pop("vendor_id", None)
    request.session.pop("vendor_name", None)

    messages.success(request, "Vendor logged out successfully.")
    return redirect("login")

def vendor_update_profile(request):
    vendor = CanteenVendor.objects.get(id=request.session.get('vendor_id'))  # assuming session holds vendor_id

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        restaurant_name = request.POST.get('restaurant_name')
        mobile = request.POST.get('mobile')
        description = request.POST.get('description')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
        else:
            vendor.full_name = full_name
            vendor.restaurant_name = restaurant_name
            vendor.mobile_number = mobile
            vendor.store_description = description
            vendor.password = password 
            if password:
                vendor.password = make_password(password)#this in real-world!
            vendor.save()
            messages.success(request, "Profile updated successfully.")
            request.session.update({"vendor_name": full_name})  # Update session name

    context = {
        'full_name': vendor.full_name,
        'restaurant_name': vendor.restaurant_name,
        'mobile_number': vendor.mobile_number,
        'store_description': vendor.store_description,
        
    }
    return render(request, 'vendor_account.html', context)

def home_view(request):
    return render(request, 'registration.html')

def additems(request):

    
    if request.method == "POST":

         # Get vendor details from session (assuming they are stored after login)
        vendor_id = request.session.get('vendor_id')
        vendor_full_name = request.session.get('full_name')
        print(vendor_id)
        if vendor_id is None:
            return redirect('login')  # Redirect if vendor is not logged in


         # Retrieve form data
        food_name = request.POST["foodName"]
        description = request.POST["description"]
        food_type = request.POST["FoodType"]
        category = request.POST["Category"]
        price = request.POST["Price"]
        image = request.FILES["image"]
      
       # Retrieve the vendor using the vendor_id from session
        vendor = CanteenVendor.objects.get(id=vendor_id)
        
       

        #retrive vendor name 
        
        
        # Create and save the food item to the database
        food_item = FoodItem(
            vendor=vendor,
            #reasturant_name = reasturant_name,
            food_name=food_name,
            description=description,
            food_type=food_type,
            category=category,
            price=price,
            image=image
        )
        
        food_item.save()
        messages.success(request, "Food item added successfully.")
        return redirect("manage_items")
                  
    return render(request, 'add_items.html')

def manage_items(request):

    vendor_id = request.session.get("vendor_id")

    if vendor_id is None:
        return redirect("login")  # Redirect if vendor is not logged in

    # Fetch food items belonging to the logged-in vendor
    food_items = FoodItem.objects.filter(vendor_id=vendor_id)

    # for items in food_items :  # Debugging: Check if items exist in the terminal
    #     print(f'Name : {items}')
    return render(request, "manage_items.html", {"food_items": food_items})

def update_items(request, id):
    food_items = get_object_or_404(FoodItem, id=id)
    print("you are updatating a food item " ,id)
    
    if request.method == "POST":
        print("updatting a item")
        
        food_items.food_name = request.POST["foodName"]
        food_items.description = request.POST["description"] 
        food_items.food_type = request.POST["FoodType"]
        food_items.category = request.POST["Category"]
        food_items.price = request.POST["Price"]
        
          # Check if a new image is uploaded
        try :  
            if "image" in request.FILES:
                food_items.image = request.FILES["image"] 
        except :
            messages.error(request, "please add a image")

        food_items.save()
        messages.success(request, "Food item updated successfully.")
        return redirect("manage_items")
    
    

    return render(request, 'update_items.html', {'food_item': food_items})


from django.shortcuts import get_object_or_404, redirect
def delete_item(request, item_id):
    item = get_object_or_404(FoodItem, id=item_id)
    item.delete()
    messages.success(request, "Food item deleted successfully.")
    return redirect("manage_items")



def mark_out_of_stock(request, item_id):
    item = get_object_or_404(FoodItem, id=item_id)
    item.in_stock = False
    item.save()
    return redirect('manage_items')  

def mark_in_stock(request, item_id):
    item = get_object_or_404(FoodItem, id=item_id)
    item.in_stock = True
    item.save()
    return redirect('manage_items')  
# def order(request):
#     return render(request, 'order.html')

def account(request):
    return render(request, 'vendor_account.html')

# def admin_dashboard(request):
#     #Fetch data from the database
#     orders = Order.objects.filter(status='Completed')
#     cancelled_orders = Order.objects.filter(status='Cancelled')
#     pending_orders = Order.objects.filter(status='Pending')

#     context = {
#         'orders': orders,
#         'cancelled_orders': cancelled_orders,
#         'pending_orders': pending_orders,
#         ''
#     }
#     orders = Order.objects.all()
#     print(orders)
#     return render(request, 'vendor_dashboard.html', {'orders': orders})
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
def update_order_status(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        print("ode sause exist")
        
        print(order.order_status)
        new_status = request.POST.get('status')
        order.order_status  = new_status
        order.save()
          # If the status is "Complete", send the email with invoice details
        if new_status.lower() == 'completed':
            # Get the associated items in the order (assuming you have an OrderItem model)
            order = get_object_or_404(Order, id=order_id)
            print(order.customer.email)
            # Prepare the invoice details
            invoice_details = ""
            total_amount = 0
            
            invoice_details = f"Restaurnt Name : {order.restaurant_name}\n Item: {order.food_item}\n Quantity: {order.quantity}\n Price: {order.price}\n, "
            total_amount = order.total_amount

            invoice_details += f"\nTotal Amount: {total_amount}"

            # Send email with the invoice details
            send_mail(
                subject=f"Your order #{order_id} is complete!",
                message=f"Dear {order.customer.full_name}\n\nYour order #{order_id} has been marked as complete. Here are the details of your order:\n\n{invoice_details}\n\nThank you for your purchase!",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[order.customer.email],  # Assuming the order model has a `customer` field with an email address
            )

            # Show a success message
            messages.success(request, f"Order #{order.id} status updated to {new_status}. An email with the invoice has been sent to the customer.")

        else:
            # For all other statuses, send a regular status update email
            send_mail(
                subject=f"Your order #{order.id} status has been updated to {new_status}",
                message=f"Dear {order.customer.full_name},\n\nYour order #{order.id} status has been updated to: {new_status}.\n\nThank you for your patience.",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[order.customer.email],
            )

            # Show a success message for other statuses
            messages.success(request, f"Order #{order.id} status updated to {new_status}. An email has been sent to the customer.")
            
            

        # Redirect back to the dashboard or wherever appropriate
       # return redirect('dashboard')  

        # Show a success message
        messages.success(request, f"Order #{order.id} status updated to {new_status}. An email has been sent to the customer.")
        
        # Redirect back to the dashboard or wherever appropriate
        return redirect('dashboard')  # Replace with your admin dashboard URL name


       # messages.success(request, f"Order #{order.id} status updated to {new_status}.")
        #return redirect('dashboard')  # Replace with your admin dashboard URL name

    # Optional fallback
    messages.error(request, "Invalid request.")
    return redirect('dashboard') # Redirect back to the dashboard# Replace 'your_template.html' with your actual template name

def admin_statistics_offline(request):
    vendor_id = request.session.get('vendor_id')
    today = datetime.now().date()

    # Fetch all completed orders for this vendor
    offline_orders = OfflineOrder.objects.filter(vendor_id=vendor_id)

    # Get first order date
    first_order_date = offline_orders.aggregate(Min('order_date'))['order_date__min']
    first_order_date = first_order_date.date() if first_order_date else today

    # Date filter
    from_date_str = request.GET.get('from_date')
    to_date_str = request.GET.get('to_date')
    show_all = request.GET.get('show_all')
    
    if show_all == '1':
        from_date = None
        to_date = None
    elif from_date_str and to_date_str:
        from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date()
        to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date()
    else:
        to_date = today
        from_date = today - timedelta(days=6)

    from_date = parse_date(from_date_str) if from_date_str else today - timedelta(days=6)  # Default last 7 days
    to_date = parse_date(to_date_str) if to_date_str else today

    # Line Chart Data (sales over time)
    delta = (to_date - from_date).days + 1
    line_labels = []
    line_data = []

    for i in range(delta):
        day = from_date + timedelta(days=i)
        total = offline_orders.filter(order_date__date=day).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        line_labels.append(day.strftime('%d %b'))
        line_data.append(float(total))

    # Bar Chart Data (top food items sold)
    bar_filtered_orders = offline_orders.filter(order_date__date__range=(from_date, to_date))
    food_stats = (
        bar_filtered_orders
        .values('food_item__food_name')
        .annotate(
            total_earned=Sum('total_amount'),
            total_quantity=Sum('quantity')
        )
        .order_by('-total_earned')
    )
    bar_labels = [item['food_item__food_name'] for item in food_stats]
    bar_data = [item['total_quantity'] for item in food_stats]

    # Summary stats
    daily_total = offline_orders.filter(order_date__date=today).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    weekly_total = offline_orders.filter(order_date__date__gte=today - timedelta(days=7)).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    monthly_total = offline_orders.filter(order_date__date__gte=today - timedelta(days=30)).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_collection = offline_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_orders = offline_orders.count()

    today_orders = OfflineOrder.objects.filter(order_date__date=today, vendor_id=vendor_id)
    #today_completed_count = today_orders.filter(order_status='Completed').count()
    #today_cancelled_count = today_orders.filter(order_status='Cancelled').count()
    today_total_count = today_orders.count()
    report_type = request.GET.get('report_type')  # Can be 'pdf' or 'excel'

    if report_type == 'pdf':
        return generate_pdf_report(from_date, to_date, completed_orders)
    elif report_type == 'excel':
        return generate_excel_report(from_date, to_date, completed_orders)
    context = {
        'daily_total': daily_total,
        'weekly_total': weekly_total,
        'monthly_total': monthly_total,
        'total_collection': total_collection,
        'total_orders': total_orders,
        'today_total_count': today_total_count,
        #'today_completed_count': today_completed_count,
        #'today_cancelled_count': today_cancelled_count,
        'food_stats': food_stats,
        # Charts
        'graph_labels': line_labels,
        'graph_data': line_data,
        'food_labels': bar_labels,
        'food_data': bar_data,

        # Form values
        'from_date': from_date.strftime('%Y-%m-%d'),
        'to_date': to_date.strftime('%Y-%m-%d'),
    }

    return render(request, 'admin_statistics_offline.html', context)

    
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.http import HttpResponse
from django.template import Context
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing, String
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.widgets.markers import makeMarker

from django.db.models import Sum
from django.http import HttpResponse
from datetime import datetime, timedelta

def download_statistics_pdf(request):
    vendor_id = request.session.get('vendor_id')
    today = datetime.now().date()
    from_date = today - timedelta(days=6)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=statistics_report_{today}.pdf'
    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # === TITLE ===
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, height - 50, f"Vendor Statistics Report - {today.strftime('%d %b %Y')}")

    # === TABLE HEADER ===
    p.setFont("Helvetica-Bold", 12)
    y = height - 100
    p.drawString(50, y, "#")
    p.drawString(80, y, "Food Item")
    p.drawString(250, y, "Qty")
    p.drawString(320, y, "Earnings (₹)")

    # === FOOD STATS ===
    food_data = (
        Order.objects
        .filter(order_status='Completed', vendor_id=vendor_id)
        .values('food_item__food_name')
        .annotate(total_quantity=Sum('quantity'), total_earned=Sum('total_amount'))
        .order_by('-total_earned')
    )

    y -= 20
    for i, item in enumerate(food_data, start=1):
        p.setFont("Helvetica", 11)
        p.drawString(50, y, str(i))
        p.drawString(80, y, str(item['food_item__food_name']))
        p.drawString(250, y, str(item['total_quantity']))
        p.drawString(320, y, f"₹ {item['total_earned']}")
        y -= 20
        if y < 200:
            p.showPage()
            y = height - 50

    # === LINE CHART: Sales over last 7 days ===
    p.showPage()
    p.setFont("Helvetica-Bold", 14)
    p.drawString(200, height - 50, "Line Chart: Daily Sales (₹)")

    sales_data = []
    line_labels = []
    for i in range(7):
        day = from_date + timedelta(days=i)
        total = (
            Order.objects
            .filter(order_status='Completed', vendor_id=vendor_id, order_date__date=day)
            .aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        )
        sales_data.append((i, float(total)))
        line_labels.append(day.strftime('%d-%b'))

    drawing = Drawing(400, 200)
    lp = LinePlot()
    lp.x = 50
    lp.y = 30
    lp.height = 150
    lp.width = 300
    lp.data = [sales_data]
    lp.lines[0].strokeColor = colors.blue
    lp.lines[0].symbol = makeMarker('Circle')
    lp.xValueAxis.valueMin = 0
    lp.xValueAxis.valueMax = 6
    lp.xValueAxis.valueSteps = list(range(7))
    lp.yValueAxis.valueMin = 0
    lp.yValueAxis.valueMax = max([val for (_, val) in sales_data] + [100])
    lp.yValueAxis.valueStep = 100

    # Add day labels
    for i, label in enumerate(line_labels):
        drawing.add(String(lp.x + i * (lp.width / 6), 15, label, fontSize=8))

    drawing.add(lp)
    renderPDF = drawing.drawOn(p, 50, height - 280)

    # === BAR CHART: Top Food Quantities ===
    p.showPage()
    p.setFont("Helvetica-Bold", 14)
    p.drawString(200, height - 50, "Bar Chart: Top Food Items by Quantity")

    bar_labels = []
    bar_values = []
    top_items = list(food_data[:5])
    for item in top_items:
        bar_labels.append(item['food_item__food_name'])
        bar_values.append(item['total_quantity'])

    drawing = Drawing(400, 200)
    bc = VerticalBarChart()
    bc.x = 50
    bc.y = 30
    bc.height = 150
    bc.width = 300
    bc.data = [bar_values]
    bc.categoryAxis.categoryNames = bar_labels
    bc.barWidth = 15
    bc.barSpacing = 10
    bc.valueAxis.valueMin = 0
    bc.valueAxis.valueMax = max(bar_values + [10])
    bc.valueAxis.valueStep = max(bar_values + [10]) // 5 or 1
    bc.bars[0].fillColor = colors.darkorange
    drawing.add(bc)

    renderPDF = drawing.drawOn(p, 50, height - 280)

    p.showPage()
    p.save()
    return response

from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from django.http import HttpResponse

def download_excel_report(request):
    vendor_id = request.session.get('vendor_id')
    today = datetime.now().date()

    # Use date filters as needed
    from_date_str = request.GET.get('from_date')
    to_date_str = request.GET.get('to_date')

    from_date = parse_date(from_date_str) if from_date_str else today - timedelta(days=6)
    to_date = parse_date(to_date_str) if to_date_str else today

    orders = Order.objects.filter(
        vendor_id=vendor_id,
        order_status='Completed',
        order_date__date__range=(from_date, to_date)
    )
    
    food_stats = (
        orders
        .values('food_item__food_name')
        .annotate(
            total_earned=Sum('total_amount'),
            total_quantity=Sum('quantity')
        )
        .order_by('-total_earned')
    )

    # Create workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Food Item Stats"

    # Headers
    headers = ['#', 'Food Item', 'Total Quantity Sold', 'Total Earnings (₹)']
    ws.append(headers)

    # Rows
    for idx, item in enumerate(food_stats, start=1):
        ws.append([
            idx,
            item['food_item__food_name'],
            item['total_quantity'],
            float(item['total_earned']),
        ])
    

    # Auto column width
    for col in ws.columns:
        max_length = max(len(str(cell.value)) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = max_length + 2

    # Response
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    filename = f"statistics_report_{from_date}_to_{to_date}.xlsx"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    wb.save(response)
    return response


from django.shortcuts import render, redirect
from .models import FoodItem, OfflineOrder
from django.contrib import messages

# def create_offline_order(request):
#     vendor_id = request.session.get('vendor_id')  # Get current vendor ID
#     food_items = FoodItem.objects.filter(vendor_id=vendor_id)  # Filter by vendor

#     if request.method == 'POST':
#         items = request.POST.getlist('food_item')
#         quantities = request.POST.getlist('quantity')
#         payment_mode = request.POST.get('payment_mode')

#         if not items or not quantities or not payment_mode:
#             messages.error(request, "Please fill all fields.")
#             return redirect('create_offline_order')

#         order = OfflineOrder.objects.create(payment_mode=payment_mode)
#         for item_id, qty in zip(items, quantities):
#             if item_id and qty:
#                 food = FoodItem.objects.get(id=item_id, vendor_id=vendor_id)
#                 OfflineOrderItem.objects.create(order=order, food_item=food, quantity=int(qty))

#         messages.success(request, f"Order Created. Token: #{order.id}")
#         return redirect('create_offline_order')

#     return render(request, 'offline_order.html', {'food_items': food_items})

from django.shortcuts import render
from .models import OfflineOrder
from .models import FoodItem
from decimal import Decimal
from django.utils import timezone

def create_offline_order(request):
    vendor_id = request.session.get('vendor_id')

    if request.method == 'POST':
        food_items = request.POST.getlist('food_item[]')
        quantities = request.POST.getlist('quantity[]')
        payment_method = request.POST.get('payment_method')

        orders = []
        grand_total = Decimal('0.00')

        for food_id, qty in zip(food_items, quantities):
            food = FoodItem.objects.get(id=food_id, vendor_id=vendor_id)
            quantity = int(qty)
            price = food.price
            total = price * quantity
            grand_total += total

            order = OfflineOrder.objects.create(
                vendor_id=vendor_id,
                food_item=food,
                price=price,
                quantity=quantity,
                total_amount=total,
                payment_method=payment_method,
                order_date=now()
            )
            orders.append(order)

        context = {
            'food_items': FoodItem.objects.filter(vendor_id=vendor_id),
            'orders': orders,
            'grand_total': grand_total,
            'show_receipt': True,
        }
        return render(request, 'offline_order.html', context)

    # For GET
    context = {
        'food_items': FoodItem.objects.filter(vendor_id=vendor_id),
        'show_receipt': False
    }
    return render(request, 'offline_order.html', context)

