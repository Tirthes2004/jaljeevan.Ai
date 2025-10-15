from django.contrib import admin
from .models import Vendor

# Register your models here.
class VendorAdmin(admin.ModelAdmin):
    list_display = ('shop_name', 'owner_name', 'phone_number', 'district')
    search_fields = ('shop_name', 'owner_name', 'phone_number', 'PAN_Number', 'GSTIN_Number')
    list_filter = ('district', 'service_type')
    ordering = ('district',)
    list_per_page = 20

admin.site.register(Vendor, VendorAdmin)