import os
import django
import json

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "yourproject.settings")  # change to your project
django.setup()

from yourapp.models import Vendor  # change 'yourapp' to your app name

# Load JSON file
with open('vendors.json', 'r') as f:
    vendors_data = json.load(f)

# Insert data into database
for v in vendors_data:
    Vendor.objects.get_or_create(
        shop_name=v['shop_name'],
        owner_name=v['owner_name'],
        phone_number=v['phone_number'],
        whatsapp_number=v.get('whatsapp_number', ''),
        service_type=v['service_type'],
        district=v['district'],
        pincode=v['pincode'],
        PAN_Number=v.get('PAN_Number', ''),
        GSTIN_Number=v.get('GSTIN_Number', '')
    )

print("All vendors have been inserted successfully!")
