from django.db import models
from datetime import datetime
from django.db.models import Avg

class CanteenVendor(models.Model):
    id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=100)
    restaurant_name = models.CharField(max_length=100)
    mobile_number = models.CharField(max_length=100)
    store_description = models.TextField()
    password = models.CharField(max_length=255)  # It is recommended to hash passwords
    is_approved = models.BooleanField(default=False)  # Admin approval status
    
    def __str__(self):
        return self.restaurant_name

class FoodItem(models.Model):
    #reasturant_name = models.ForeignKey(CanteenVendor, on_delete=models.CASCADE , null=True)  # Reference restaurant ID
    vendor = models.ForeignKey(CanteenVendor, on_delete=models.CASCADE)# Reference vendor ID
    
    food_name = models.CharField(max_length=100)
    description = models.TextField()
    TYPE_CHOICES = [('Veg', 'Veg'), ('Non-Veg', 'Non-Veg')]
    food_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    CATEGORY_CHOICES = [('Breakfast', 'Breakfast'), ('Drinks', 'Drinks'),
                        ('Lunch', 'Lunch'), ('Snacks', 'Snacks'), ('Dinner', 'Dinner')]
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='images/')  # Store in media folder
    created_at = models.DateTimeField(auto_now_add=True)

    # def __str__(self):
    #     return f"{self.food_name} - {self.vendor.restaurant_name}"
    @property
    def average_rating(self):
        avg = self.ratings.aggregate(avg_rating=Avg('rating'))['avg_rating']
        return round(avg, 1) if avg else 0
    
    def __str__(self):
        return f"{self.food_name}"
    
    
# class OfflineOrder(models.Model):
#     vendor = models.ForeignKey(CanteenVendor, on_delete=models.CASCADE)
#     PAYMENT_CHOICES = (
#         ('Cash', 'Cash'),
#         ('Online', 'Online'),
#     )
#     created_at = models.DateTimeField(auto_now_add=True)
#     payment_mode = models.CharField(max_length=10, choices=PAYMENT_CHOICES)

#     def __str__(self):
#         return f"Token #{self.id} - {self.created_at.strftime('%d-%m-%Y %H:%M')}"
    
    
    
# class OfflineOrderItem(models.Model):
#     order = models.ForeignKey(OfflineOrder, on_delete=models.CASCADE, related_name='items')
#     food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
#     quantity = models.PositiveIntegerField()
#     price = models.DecimalField(max_digits=6, decimal_places=2)
#     total_amount = models.DecimalField(max_digits=8, decimal_places=2)

#     def __str__(self):
#         return f"{self.food_item.food_name} x {self.quantity}"


class OfflineOrder(models.Model):
    PAYMENT_CHOICES = (
        ('Cash', 'Cash'),
        ('Online', 'Online'),
    )

    vendor = models.ForeignKey(CanteenVendor, on_delete=models.CASCADE, null=True)
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE, null=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    quantity = models.PositiveIntegerField(default=1)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='Cash')
    order_date = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return f"{self.food_item} - {self.quantity} x ₹{self.price} = ₹{self.total_amount}"