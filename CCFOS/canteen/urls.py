# 
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('mycart/', views.MyCart, name='mycart'),
   # path('view_order/', views.view_order, name='view_order'),
    path('aboutus/', views.AboutUs, name='aboutus'),
    path('contactus/', views.Contactus, name='contactus'),
]
