from django.contrib import admin
from .models import Customer
# Register your models here.

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'email', 'mobile_number')

admin.site.register(Customer, CustomerAdmin)