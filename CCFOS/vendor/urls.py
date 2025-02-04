from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.dashboard_home, name='vendor_home'),
    path('login/', views.home_view, name='vendor_login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('order/', views.order, name='order'),
    path('items/', views.items, name='items'),
    path('account/', views.account, name='account'),
]
