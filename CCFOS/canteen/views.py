from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, 'home.html')

def MyCart(request):
    return render(request, 'mycart.html')

def MyOrder(request):
    return render(request, 'myorder.html')


def AboutUs(request):
    return render(request, 'aboutus.html')


def ContactUs(request):
    return render(request, 'contactus.html')




