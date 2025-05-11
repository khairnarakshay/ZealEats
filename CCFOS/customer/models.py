from django.db import models
from vendor.models import FoodItem, CanteenVendor
from datetime import datetime

# Create your models here.

class Customer(models.Model):
    id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    mobile_number = models.CharField(max_length=100)
    password = models.CharField(max_length=255)  # It is recommended to hash passwords
    
    def __str__(self):
        return self.full_name

# Cart Model


# CartItem Model
class Cart(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE , null=False,default="")  # Link to Customer
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart for {self.customer.full_name}"


class CartItem(models.Model):
    #order = models.ForeignKey('Order',  related_name="cart_items", on_delete=models.CASCADE, null=True, blank=True)  
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=6, decimal_places=2 , default=0.00)
    

    def __str__(self):
        return f"{self.food_item.food_name} - {self.quantity}"

    def total_price(self):
        return self.quantity * self.price
    
    
class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Processing', 'Processing'),
       # ('Shipped', 'Shipped'),
        ('Completed ', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE , null=False,default="")  # Link to Customer
    order_date = models.DateTimeField(default=datetime.now)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2 , default=0.00)
    payment_method = models.CharField(max_length=20)
    payment_status = models.CharField(max_length=20, default="Pending")
    is_paid = models.BooleanField(default=False)
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='Pending')
    
    # These fields will store the details of the ordered items
    quantity = models.PositiveIntegerField(default=1)
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE , null=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    restaurant_name = models.CharField(max_length=100 , default="")
    vendor = models.ForeignKey(CanteenVendor, on_delete=models.CASCADE, null= True)  # Link to the restaurant
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order for {self.customer.full_name} on {self.order_date}"
