from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

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

    user = models.ForeignKey(
        'auth.User', 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        related_name='calculation_logs'
    )
    """Log calculations for analytics and usage tracking"""
    district = models.ForeignKey(
        RainfallData, 
        on_delete=models.CASCADE,
        related_name='calculations'
    )
    roof_length = models.DecimalField(max_digits=8, decimal_places=2)
    roof_width = models.DecimalField(max_digits=8, decimal_places=2)
    roof_area = models.DecimalField(max_digits=10, decimal_places=2)
    water_harvested_liters = models.DecimalField(max_digits=12, decimal_places=2)
    runoff_coefficient = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        default=0.80
    )
    calculated_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    session_id = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'calculation_logs'
        ordering = ['-calculated_at']
        indexes = [
            models.Index(fields=['calculated_at']),
            models.Index(fields=['district', 'calculated_at']),
            models.Index(fields=['ip_address', 'calculated_at']),
        ]

    def __str__(self):
        username = self.user.username if self.user else "Anonymous"
        return f"{username} - {self.district.district_name} - {self.water_harvested_liters}L - {self.calculated_at.strftime('%Y-%m-%d %H:%M')}"

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
