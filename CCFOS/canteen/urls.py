# 
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('mycart/', views.MyCart, name='mycart'),
    path('myorder/', views.MyOrder, name='myorder'),
    path('aboutus/', views.AboutUs, name='aboutus'),
    path('contactus/', views.ContactUs, name='contactus'),
]
