from django.shortcuts import render,HttpResponse
from django.http import HttpResponse

def dashboard_home(request):
    return render(request , 'vendor_dashboard.html')

# Create your views here.
def home_view(request):
    return render(request , 'login.html')

def dashboard(request):
    return render(request, 'vendor_dashboard.html')

def order(request):
    return render(request, 'order.html')

def items(request):
    return render(request, 'items.html')

def account(request):
    return render(request, 'account.html')



