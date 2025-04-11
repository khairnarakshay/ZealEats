from django.shortcuts import render
from vendor.models import FoodItem , CanteenVendor
from customer.models import Customer 
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


def ContactUs(request):
    return render(request, 'contactus.html')




