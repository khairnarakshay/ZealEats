from django.db import models
from customer.models import Customer
from vendor.models import FoodItem
from django.db.models import Avg

# Create your models here.
class ContactUs(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    subject = models.CharField(max_length=100)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class FoodRating(models.Model):
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE, related_name='ratings')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(default=0)  # 1 to 5
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('food_item', 'customer') 
        
    # @property
    # def average_rating(self):
    #     return self.ratings.aggregate(Avg('rating'))['rating__avg'] or 0
