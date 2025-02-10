from django.db import models

class CanteenVendor(models.Model):
    full_name = models.CharField(max_length=100)
    restaurant_name = models.CharField(max_length=100)
    mobile_number = models.CharField(max_length=15)
    store_description = models.TextField()
    password = models.CharField(max_length=255)  # It is recommended to hash passwords
    confirm_password = models.CharField(max_length=255)
    
    def __str__(self):
        return self.restaurant_name
