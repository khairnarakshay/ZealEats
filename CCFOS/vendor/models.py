from django.db import models

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
    def __str__(self):
        return f"{self.food_name}"