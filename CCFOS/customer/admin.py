from django.contrib import admin
from .models import Customer, Cart, CartItem, Order
# Register your models here.

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'email', 'mobile_number')

admin.site.register(Customer, CustomerAdmin)


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1  # The number of empty CartItems to display by default when creating a Cart
    fields = ('food_item', 'quantity', 'price')  # You can customize which fields to show

class CartAdmin(admin.ModelAdmin):
    list_display = ('customer', 'created_at', 'updated_at')  # Fields to display in the Cart admin list view
    inlines = [CartItemInline]  # Inline the CartItems with Cart
    search_fields = ('customer__full_name', 'customer__email')  # Allow searching by customer fields

class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'food_item', 'quantity', 'price', 'total_price')  # Display fields for CartItems
    search_fields = ('food_item__food_name', 'cart__customer__full_name')  # Allow searching by food name and customer name

# Register Cart and CartItem models with their respective admins
admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)

class  OrderAdmin(admin.ModelAdmin):
    list_display = ('customer', 'order_date', 'total_amount', 'payment_method', 'payment_status', 'is_paid', 'order_status','quantity','price','food_item','restaurant_name','vendor')  # Fields to display in the Order admin list view
    search_fields = ('customer__full_name', 'payment_method')  # Allow searching by customer name and payment method

    
admin.site.register(Order, OrderAdmin)