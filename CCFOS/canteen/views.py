from django.shortcuts import render
from vendor.models import FoodItem , CanteenVendor
# Create your views here.
def home(request):
    food_items = FoodItem.objects.all()
    print(food_items)
    return render(request, 'home.html', {'food_items': food_items})


def MyCart(request):
    return render(request, 'mycart.html')

def MyOrder(request):
    return render(request, 'myorder.html')


def AboutUs(request):
    return render(request, 'aboutus.html')


def ContactUs(request):
    return render(request, 'contactus.html')




