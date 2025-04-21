from django.contrib import admin
from .models import ContactUs, FoodRating
# Register your models he

class AdminContactUs(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'message', 'created_at')
    search_fields = ('name', 'email', 'subject')
    list_filter = ('created_at',)
    ordering = ('-created_at',)
admin.site.register(ContactUs, AdminContactUs)

class AdminFoodRating(admin.ModelAdmin):
    list_display = ('food_item', 'customer', 'rating', 'created_at')
    search_fields = ('food_item__name', 'customer__name')
    list_filter = ('created_at',)

admin.site.register(FoodRating, AdminFoodRating)