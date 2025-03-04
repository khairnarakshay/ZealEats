from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages
from .models import CanteenVendor, FoodItem
from django.contrib.auth import logout as auth_logout  # Keep logout for admin
from django.contrib.auth.decorators import login_required

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

    
    return render(request, "vendor_dashboard.html", {"vendor_name": request.session["vendor_name"]})

def vendor_logout(request):
    request.session.pop("vendor_id", None)
    request.session.pop("vendor_name", None)

    messages.success(request, "Vendor logged out successfully.")
    return redirect("login")


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
def order(request):
    return render(request, 'order.html')

def account(request):
    return render(request, 'vendor_account.html')