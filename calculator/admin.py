from django.contrib import admin
from .models import RainfallData, CalculationLog, GraphPlot, SystemConfiguration

@admin.register(RainfallData)
class RainfallDataAdmin(admin.ModelAdmin):
    list_display = ['district_name', 'state', 'annual_rainfall_mm', 'is_active', 'updated_at']
    list_filter = ['state', 'is_active', 'country', 'updated_at']
    search_fields = ['district_name', 'state']
    ordering = ['district_name']
    list_per_page = 50
    readonly_fields = ['created_at', 'updated_at']

@admin.register(CalculationLog)
class CalculationLogAdmin(admin.ModelAdmin):
    list_display = [
        'get_username', 
        'district_name', 
        'roof_area_sqm', 
        'water_harvested_liters', 
        'created_at'
    ]
    list_filter = ['created_at', 'state', 'roof_type']
    search_fields = ['district_name', 'user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at', 'client_ip']
    date_hierarchy = 'created_at'
    list_per_page = 25
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'client_ip')
        }),
        ('Location', {
            'fields': ('district_name', 'state')
        }),
        ('Roof Specifications', {
            'fields': ('roof_area_sqm', 'roof_type', 'runoff_coefficient')
        }),
        ('Weather & Household', {
            'fields': ('annual_rainfall_mm', 'number_of_dwellers')
        }),
        ('Results', {
            'fields': ('water_harvested_liters', 'efficiency_percent')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_username(self, obj):
        return obj.user.username if obj.user else 'Anonymous'
    get_username.short_description = 'User'
    get_username.admin_order_field = 'user__username'

@admin.register(SystemConfiguration)
class SystemConfigurationAdmin(admin.ModelAdmin):
    list_display = ['roof_type', 'runoff_coefficient', 'is_default', 'updated_at']
    list_filter = ['roof_type', 'is_default']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(GraphPlot)
class GraphPlotAdmin(admin.ModelAdmin):
    list_display = [
        'district_name', 
        'state', 
        'get_annual_total',
        'jan', 'feb', 'mar', 'apr', 'may', 'jun',
        'jul', 'aug', 'sep', 'oct', 'nov', 'dec',
        'updated_at'
    ]
    list_filter = ['state', 'created_at', 'updated_at']
    search_fields = ['district_name', 'state']
    ordering = ['state', 'district_name']
    readonly_fields = ['created_at', 'updated_at', 'get_annual_total']
    list_per_page = 30
    
    def get_annual_total(self, obj):
        """Calculate and display annual rainfall total."""
        monthly_values = [
            float(obj.jan), float(obj.feb), float(obj.mar), float(obj.apr),
            float(obj.may), float(obj.jun), float(obj.jul), float(obj.aug),
            float(obj.sep), float(obj.oct), float(obj.nov), float(obj.dec)
        ]
        total = sum(monthly_values)
        return f"{total:.1f} mm/year"
    get_annual_total.short_description = 'Annual Total'

# Customize admin site headers
admin.site.site_header = "JalJeevan.AI Administration"
admin.site.site_title = "JalJeevan.AI Admin"
admin.site.index_title = "Rainwater Harvesting Management"
