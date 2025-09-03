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
    # Use the actual model field name for harvested water
    list_display = ['district', 'roof_area', 'water_harvested_liters', 'calculated_at']
    list_filter = ['calculated_at', 'district__state']
    search_fields = ['district__district_name']
    readonly_fields = ['calculated_at']
    date_hierarchy = 'calculated_at'
