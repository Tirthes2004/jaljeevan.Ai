from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator


# Create your models here.

class SubsidyApplication(models.Model):
    """Rainwater Harvesting Subsidy Application"""
    
    STATUS_CHOICES = [
        ('SUBMITTED', 'Submitted'),
        ('UNDER_REVIEW', 'Under Review'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]
    
    CAPTURE_MODE_CHOICES = [
        ('device', 'Device GPS'),
        ('manual', 'Manual Entry'),
    ]
    
    # Application metadata
    application_id = models.CharField(max_length=20, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subsidy_applications')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SUBMITTED')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Applicant KYC
    full_name = models.CharField(max_length=200)
    mobile = models.CharField(max_length=10, validators=[RegexValidator(r'^\d{10}$')])
    email = models.EmailField()
    aadhaar_or_id = models.CharField(max_length=12, validators=[RegexValidator(r'^\d{12}$')])
    address = models.TextField()
    
    # Bank details
    account_holder_name = models.CharField(max_length=200)
    account_number = models.CharField(max_length=20)
    ifsc_code = models.CharField(max_length=11, validators=[RegexValidator(r'^[A-Z]{4}0[A-Z0-9]{6}$')])
    
    # Property
    property_address = models.TextField()
    district = models.CharField(max_length=100)
    pincode = models.CharField(max_length=6, validators=[RegexValidator(r'^\d{6}$')])
    
    # Location
    geo_latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    geo_longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    gps_accuracy_meters = models.FloatField(null=True, blank=True)
    location_capture_mode = models.CharField(max_length=10, choices=CAPTURE_MODE_CHOICES, default='device')
    manual_address_entry = models.TextField(blank=True)
    
    # Technical proposal
    calculation_pdf = models.FileField(upload_to='govt_applications/calculations/')
    
    # Consent
    consent_given = models.BooleanField(default=False)
    
    # Decision
    decided_by = models.ForeignKey('Officer', on_delete=models.SET_NULL, null=True, blank=True, related_name='decided_applications')
    decided_at = models.DateTimeField(null=True, blank=True)
    rejection_code = models.CharField(max_length=50, blank=True)
    rejection_reason = models.TextField(blank=True)
    admin_remarks = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.application_id} - {self.full_name}"
    
    def save(self, *args, **kwargs):
        if not self.application_id:
            from django.utils import timezone
            timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
            self.application_id = f'RWH{timestamp}'
        super().save(*args, **kwargs)


class Officer(models.Model):
    officer_name = models.CharField(max_length=50)
    officer_email = models.EmailField(unique=True)
    officer_phone = models.CharField(max_length=10, validators=[RegexValidator(r'^\d{10}$')])
    assigned_district = models.CharField(max_length=100)
    govt_id = models.CharField(max_length=10, unique=True, blank=False, null=False)
    password = models.CharField(max_length=128)

    def __str__(self):
        return f"{self.officer_name} - {self.assigned_district}"
