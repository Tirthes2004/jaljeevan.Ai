from django.db import models

# Create your models here.

class Vendor(models.Model):
    shop_name = models.CharField(max_length=100, null= False, blank=False)
    owner_name = models.CharField(max_length=100, null=False, blank=False)
    phone_number = models.CharField(max_length=10, unique=True, null=False, blank=False)
    whatsapp_number = models.CharField(max_length=10, unique=True, null=True, blank=True)
    service_type = models.TextField(max_length=300, null=False, blank=False)
    district = models.CharField(max_length=30, null=False, blank=False)
    pincode = models.CharField(max_length=6, null=False, blank=False)
    PAN_Number = models.CharField(max_length=10, unique=True, null=True, blank=True)
    GSTIN_Number = models.CharField(max_length=10, unique=True, null=True, blank=True)

    def __str__(self):
        return self.shop_name