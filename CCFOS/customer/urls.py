from django.urls import path
from . import views

urlpatterns = [
    #path('home/', views.home, name='home'),
    path('registration/', views.registration_view, name='registration'),
    path('customer_login/', views.login_view, name='customer_login'),
    path('customer_logout/', views.logout_view, name='customer_logout'),
    path('send_otp/', views.send_otp, name='send_otp'),
    path('validate_otp/', views.validate_otp, name='validate_otp'),
    path("check-email/",views.check_email_exists, name="check_email_exists"),
]