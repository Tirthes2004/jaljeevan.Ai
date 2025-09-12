from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User

class RainfallData(models.Model):
    district_name = models.CharField(
        max_length=100, 
        db_index=True,  # Add database index for faster queries
        help_text="Name of the district"
    )
    
    state = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        db_index=True,  # Add index for state filtering
        help_text="State where district is located"
    )
    country = models.CharField(
        max_length=100,
        default='India',
        help_text="Country where district is located"
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Whether this district is active/visible in the system"
    )
    latitude = models.DecimalField(
        max_digits=10, 
        decimal_places=8, 
        blank=True, 
        null=True,
        help_text="Latitude coordinate"
    )
    longitude = models.DecimalField(
        max_digits=11, 
        decimal_places=8, 
        blank=True, 
        null=True,
        help_text="Longitude coordinate"
    )
    annual_rainfall_mm = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Annual rainfall in millimeters"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'rainfall_data'
        verbose_name = 'Rainfall Data'
        verbose_name_plural = 'Rainfall Data'
        ordering = ['district_name']
        indexes = [
            models.Index(fields=['district_name', 'state']),
            models.Index(fields=['state', 'is_active']),
        ]

    def __str__(self):
        return f"{self.district_name}, {self.state} - {self.annual_rainfall_mm}mm"

class CalculationLog(models.Model):
    """Store rainwater harvesting calculations"""
    
    # User information
    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="User who performed the calculation"
    )
    
    # Location data
    district_name = models.CharField(max_length=100, help_text="District name")  # ✅ Fixed: was 'district'
    state = models.CharField(max_length=100, blank=True, help_text="State name")
    
    # Roof specifications
    roof_area_sqm = models.FloatField(  # ✅ Fixed: was 'roof_area'
        validators=[MinValueValidator(0.1)],
        help_text="Roof area in square meters"
    )
    roof_type = models.CharField(max_length=50, help_text="Type of roof")
    runoff_coefficient = models.FloatField(
        validators=[MinValueValidator(0.1)],
        help_text="Runoff coefficient based on roof type"
    )
    
    # Weather data
    annual_rainfall_mm = models.FloatField(
        validators=[MinValueValidator(0)],
        help_text="Annual rainfall in millimeters"
    )
    
    # Household data
    number_of_dwellers = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Number of people in household"
    )
    
    # Calculation results
    water_harvested_liters = models.FloatField(
        validators=[MinValueValidator(0)],
        help_text="Annual water harvest in liters"
    )
    efficiency_percent = models.FloatField(
        blank=True,
        null=True,
        help_text="System efficiency percentage"
    )
    
    # Metadata
    client_ip = models.GenericIPAddressField(
        null=True, 
        blank=True,
        help_text="IP address of client"
    )
    created_at = models.DateTimeField(auto_now_add=True)  # ✅ Fixed: was 'calculated_at'
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'calculation_log'
        ordering = ['-created_at']
        verbose_name = 'Calculation Log'
        verbose_name_plural = 'Calculation Logs'
    
    def __str__(self):
        user_name = self.user.username if self.user else 'Anonymous'
        return f"{user_name} - {self.district_name} - {self.water_harvested_liters:.0f}L"

class SystemConfiguration(models.Model):
    """System-wide configuration settings"""
    ROOF_TYPES = [
        ('concrete', 'Concrete Roof'),
        ('metal', 'Metal Roof'),
        ('tile', 'Tile Roof'),
        ('asphalt', 'Asphalt Shingle'),
    ]
    
    roof_type = models.CharField(
        max_length=20,
        choices=ROOF_TYPES,
        default='concrete'
    )
    runoff_coefficient = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.80,
        validators=[MinValueValidator(0.1), MaxValueValidator(1.0)]
    )
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'system_configuration'
        verbose_name = 'System Configuration'
        verbose_name_plural = 'System Configurations'

    def save(self, *args, **kwargs):
        if self.is_default:
            # Ensure only one default configuration
            SystemConfiguration.objects.filter(is_default=True).update(is_default=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_roof_type_display()} - {self.runoff_coefficient}"
    



# class GraphPlot(models.Model):
#     """Monthly rainfall data for a district"""

#     district_name = models.CharField(max_length=100, db_index=True)
#     state = models.CharField(max_length=100, db_index=True)

#     # Monthly rainfall (mm)
#     jan = models.DecimalField(max_digits=6, decimal_places=1, validators=[MinValueValidator(0)])
#     feb = models.DecimalField(max_digits=6, decimal_places=1, validators=[MinValueValidator(0)])
#     mar = models.DecimalField(max_digits=6, decimal_places=1, validators=[MinValueValidator(0)])
#     apr = models.DecimalField(max_digits=6, decimal_places=1, validators=[MinValueValidator(0)])
#     may = models.DecimalField(max_digits=6, decimal_places=1, validators=[MinValueValidator(0)])
#     jun = models.DecimalField(max_digits=6, decimal_places=1, validators=[MinValueValidator(0)])
#     jul = models.DecimalField(max_digits=6, decimal_places=1, validators=[MinValueValidator(0)])
#     aug = models.DecimalField(max_digits=6, decimal_places=1, validators=[MinValueValidator(0)])
#     sep = models.DecimalField(max_digits=6, decimal_places=1, validators=[MinValueValidator(0)])
#     oct = models.DecimalField(max_digits=6, decimal_places=1, validators=[MinValueValidator(0)])
#     nov = models.DecimalField(max_digits=6, decimal_places=1, validators=[MinValueValidator(0)])
#     dec = models.DecimalField(max_digits=6, decimal_places=1, validators=[MinValueValidator(0)])

#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         db_table = "graph_plot"
#         verbose_name = "Graph Plot"
#         verbose_name_plural = "Graph Plots"
#         ordering = ["state", "district_name"]
#         unique_together = ("state", "district_name")

#     def __str__(self):
#         return f"{self.district_name}, {self.state}"

#     def get_monthly_values(self):
#         """Return rainfall values as (month, value) for plotting"""
#         return [
#             ("JAN", float(self.jan)),
#             ("FEB", float(self.feb)),
#             ("MAR", float(self.mar)),
#             ("APR", float(self.apr)),
#             ("MAY", float(self.may)),
#             ("JUN", float(self.jun)),
#             ("JUL", float(self.jul)),
#             ("AUG", float(self.aug)),
#             ("SEP", float(self.sep)),
#             ("OCT", float(self.oct)),
#             ("NOV", float(self.nov)),
#             ("DEC", float(self.dec)),
#         ]




class GraphPlot(models.Model):
    """Monthly rainfall data for a district"""

    LABEL_CHOICES = [
        ("RURAL", "Rural"),
        ("URBAN", "Urban"),
        ("SEMI-URBAN", "Semi-Urban"),
    ]

    district_name = models.CharField(max_length=100, db_index=True)
    state = models.CharField(max_length=100, db_index=True)
    label = models.CharField(
        max_length=20,
        choices=LABEL_CHOICES,
        default="URBAN",   # you can set "RURAL" or "SEMI-URBAN" as default if you prefer
    )

    # Monthly rainfall (mm)
    jan = models.DecimalField(max_digits=6, decimal_places=1, validators=[MinValueValidator(0)])
    feb = models.DecimalField(max_digits=6, decimal_places=1, validators=[MinValueValidator(0)])
    mar = models.DecimalField(max_digits=6, decimal_places=1, validators=[MinValueValidator(0)])
    apr = models.DecimalField(max_digits=6, decimal_places=1, validators=[MinValueValidator(0)])
    may = models.DecimalField(max_digits=6, decimal_places=1, validators=[MinValueValidator(0)])
    jun = models.DecimalField(max_digits=6, decimal_places=1, validators=[MinValueValidator(0)])
    jul = models.DecimalField(max_digits=6, decimal_places=1, validators=[MinValueValidator(0)])
    aug = models.DecimalField(max_digits=6, decimal_places=1, validators=[MinValueValidator(0)])
    sep = models.DecimalField(max_digits=6, decimal_places=1, validators=[MinValueValidator(0)])
    oct = models.DecimalField(max_digits=6, decimal_places=1, validators=[MinValueValidator(0)])
    nov = models.DecimalField(max_digits=6, decimal_places=1, validators=[MinValueValidator(0)])
    dec = models.DecimalField(max_digits=6, decimal_places=1, validators=[MinValueValidator(0)])

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "graph_plot"
        verbose_name = "Graph Plot"
        verbose_name_plural = "Graph Plots"
        ordering = ["state", "district_name"]
        unique_together = ("state", "district_name")

    def __str__(self):
        return f"{self.district_name}, {self.state} ({self.label})"

    def get_monthly_values(self):
        """Return rainfall values as (month, value) for plotting"""
        return [
            ("JAN", float(self.jan)),
            ("FEB", float(self.feb)),
            ("MAR", float(self.mar)),
            ("APR", float(self.apr)),
            ("MAY", float(self.may)),
            ("JUN", float(self.jun)),
            ("JUL", float(self.jul)),
            ("AUG", float(self.aug)),
            ("SEP", float(self.sep)),
            ("OCT", float(self.oct)),
            ("NOV", float(self.nov)),
            ("DEC", float(self.dec)),
        ]
