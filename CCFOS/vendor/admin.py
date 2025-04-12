from django.contrib import admin
from .models import CanteenVendor,FoodItem, OfflineOrder
# Register your models here.
class CanteeVendorAdmin(admin.ModelAdmin):
    list_display = ('id','full_name', 'restaurant_name', 'mobile_number', 'store_description', 'is_approved','restaurant_name', 'password')
    list_filter = ("is_approved",)  # Filter to show approved/unapproved vendors
    search_fields = ("full_name",  "mobile_number")
    actions = ["approve_vendors"]

    def approve_vendors(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, "Selected vendors have been approved.")
    
    approve_vendors.short_description = "Approve selected vendors"
admin.site.register(CanteenVendor, CanteeVendorAdmin)


class FoodItemAdmin(admin.ModelAdmin):
    list_display = ('id','get_vendor_name', 'food_name', 'description', 'food_type', 'category', 'price', 'image', 'created_at')

    def get_vendor_name(self, obj):
        return obj.vendor.restaurant_name
    
    get_vendor_name.admin_order_field = 'vendor'  # Allows column order sorting
    get_vendor_name.short_description = 'Vendor Name' # Renames column heading to 'Vendor Name'


admin.site.register(FoodItem, FoodItemAdmin)

class OfflineOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'vendor', 'order_date','food_item','price','quantity','total_amount' ,'payment_method')
    # Allows searching by vendor name

admin.site.register(OfflineOrder, OfflineOrderAdmin)

# class OfflineOrderItemAdmin(admin.ModelAdmin):
#     list_display = ('id', 'order', 'food_item', 'quantity', 'price')
#     list_filter = ('order__vendor',)  # Filter to show orders by vendor
# admin.site.register(OfflineOrderItem, OfflineOrderItemAdmin)
