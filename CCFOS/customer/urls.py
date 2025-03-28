from django.urls import path
from . import views

urlpatterns = [
    #path('home/', views.home, name='home'),
    path('registration/', views.registration_view, name='registration'),
    path('customer_login/', views.login_view, name='customer_login'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('reset_password/', views.reset_password, name='reset_password'),
    path('customer_logout/', views.logout_view, name='customer_logout'),

    path('send_otp/', views.send_otp, name='send_otp'),
    
    path('validate_otp/', views.validate_otp, name='validate_otp'),
    path("check-email/",views.check_email_exists, name="check_email_exists"),
 
    path('update_profile/',views.update_profile,name='update_profile'),
    
    # path('cart/', views.view_cart, name='view_cart'),
    # path('add_to_cart/<int:food_id>/', views.add_to_cart, name='add_to_cart'),
    # path('update-cart/', views.update_cart, name='update_cart'),
    # path('remove-item/', views.remove_item, name='remove_item'),
    # path('view-cart/',views.view_cart,name= 'view_cart'),
    path('add_to_cart/<int:food_id>/',views. add_to_cart, name='add_to_cart'),
    path('view_cart/', views.view_cart, name='view_cart'),
    path('update_cart/<int:cart_item_id>/', views.update_cart, name='update_cart'),
    path('remove_from_cart/<int:cart_item_id>/',views. remove_from_cart, name='remove_from_cart'),
]