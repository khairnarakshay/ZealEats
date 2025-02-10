from django.contrib import admin
from .models import CanteenVendor
# Register your models here.
class CanteeVendorAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'restaurant_name', 'mobile_number', 'store_description', 'password', 'confirm_password')

admin.site.register(CanteenVendor, CanteeVendorAdmin)