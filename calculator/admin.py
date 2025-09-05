from django.contrib import admin
from .models import RainfallData, CalculationLog

@admin.register(RainfallData)
class RainfallDataAdmin(admin.ModelAdmin):
    list_display = ['district_name', 'state', 'annual_rainfall_mm', 'updated_at']
    list_filter = ['state', 'updated_at']
    search_fields = ['district_name', 'state']
    ordering = ['district_name']
    list_per_page = 50

@admin.register(CalculationLog)
class CalculationLogAdmin(admin.ModelAdmin):
    list_display = ['get_username', 'district', 'roof_area', 'water_harvested_liters', 'calculated_at']
    list_filter = ['calculated_at', 'district__state']
    search_fields = ['district__district_name', 'user__username']
    readonly_fields = ['calculated_at']
    date_hierarchy = 'calculated_at'
    
    # ✅ Method to display username safely
    def get_username(self, obj):
        return obj.user.username if obj.user else "Anonymous"
    get_username.short_description = "User"
    get_username.admin_order_field = 'user__username'