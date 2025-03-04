from django.db import models

# Create your models here.

class Customer(models.Model):
    id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    mobile_number = models.CharField(max_length=100)
    password = models.CharField(max_length=255)  # It is recommended to hash passwords
    
    def __str__(self):
        return self.full_name