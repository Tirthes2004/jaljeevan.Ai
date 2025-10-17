from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Vendor
from django.http import JsonResponse
from django.db.models import Q
from .models import Vendor

# vendorRegistration/views.py
from django.http import JsonResponse
from django.db.models import Q
from .models import Vendor

# Create your views here.

def vendorRegistration(request):
    return render(request, 'vendorRegistration.html')


def vendor_register(request):
    """
    Handle vendor registration form submission
    - Validates all fields
    - Prevents duplicate registrations
    - Saves vendor to database
    """
    if request.method == 'POST':
        try:
            # ====== Get Form Data ======
            shop_name = request.POST.get('shop_name', '').strip()
            owner_name = request.POST.get('owner_name', '').strip()
            phone_number = request.POST.get('phone_number', '').strip()
            whatsapp_number = request.POST.get('whatsapp_number', '').strip()
            district = request.POST.get('district', '').strip()
            pincode = request.POST.get('pincode', '').strip()
            pan_number = request.POST.get('pan_number', '').strip().upper()
            gstin_number = request.POST.get('gstin_number', '').strip().upper()
            
            # Get multiple selected services and combine into string
            services_list = request.POST.getlist('services')
            service_type = ', '.join(services_list)  # ✅ Changed to match your model field name
            
            # ====== Basic Validation ======
            if not shop_name or not owner_name or not phone_number or not district or not pincode:
                messages.error(request, 'Please fill all required fields marked with *')
                return redirect('vendorRegistration:vendorRegistration')
            
            # Validate at least one service is selected
            if not service_type:
                messages.error(request, 'Please select at least one service category')
                return redirect('vendorRegistration:vendorRegistration')
            
            # Validate either PAN or GSTIN is provided
            if not pan_number and not gstin_number:
                messages.error(request, 'Please provide either PAN Number or GSTIN Number for verification')
                return redirect('vendorRegistration:vendorRegistration')
            
            # Validate phone number format (10 digits)
            if len(phone_number) != 10 or not phone_number.isdigit():
                messages.error(request, 'Please enter a valid 10-digit phone number')
                return redirect('vendorRegistration:vendorRegistration')
            
            # Validate pincode format (6 digits)
            if len(pincode) != 6 or not pincode.isdigit():
                messages.error(request, 'Please enter a valid 6-digit pincode')
                return redirect('vendorRegistration:vendorRegistration')
            
            # ====== Check for Duplicates ======
            duplicate_checks = []
            
            # Check 1: Phone number already exists
            if Vendor.objects.filter(phone_number=phone_number).exists():
                duplicate_checks.append('phone number')
            
            # Check 2: WhatsApp number already exists (if provided and not same as phone)
            if whatsapp_number and whatsapp_number != phone_number:
                if Vendor.objects.filter(whatsapp_number=whatsapp_number).exists():
                    duplicate_checks.append('WhatsApp number')
            
            # Check 3: PAN number already exists (if provided)
            if pan_number and Vendor.objects.filter(PAN_Number=pan_number).exists():
                duplicate_checks.append('PAN number')
            
            # Check 4: GSTIN already exists (if provided)
            if gstin_number and Vendor.objects.filter(GSTIN_Number=gstin_number).exists():
                duplicate_checks.append('GSTIN number')
            
            # Check 5: Same shop name in same pincode
            if Vendor.objects.filter(shop_name__iexact=shop_name, pincode=pincode).exists():
                duplicate_checks.append('shop name in this area')
            
            # If any duplicate found, prevent registration
            if duplicate_checks:
                error_msg = f'⚠ This vendor is already registered with the same {" and ".join(duplicate_checks)}. '
                error_msg += 'If you need to update your details, please contact support.'
                messages.error(request, error_msg)
                return redirect('vendorRegistration:vendorRegistration')
            
            # ====== Create Vendor Record ======
            vendor = Vendor.objects.create(
                shop_name=shop_name,
                owner_name=owner_name,
                phone_number=phone_number,
                whatsapp_number=whatsapp_number if whatsapp_number else None,  # ✅ None if empty (allows null)
                service_type=service_type,  # ✅ Changed from 'services' to 'service_type'
                district=district,
                pincode=pincode,
                PAN_Number=pan_number if pan_number else None,  # ✅ Match exact field name with underscore
                GSTIN_Number=gstin_number if gstin_number else None  # ✅ Match exact field name
            )
            
            # Success message
            messages.success(request, 
                f'🎉 Registration Successful! Your Vendor ID is #{vendor.id}. '
                f'Shop: {shop_name} | Contact: {phone_number}. '
                'Your application is pending admin approval. You will be notified once verified.')
            
            # ✅ Redirect back to registration page (not success page)
            return redirect('vendorRegistration:vendorRegistration')
            
        except Exception as e:
            messages.error(request, f'❌ Registration failed: {str(e)}. Please try again or contact support.')
            return redirect('vendorRegistration:vendorRegistration')
    
    return redirect('vendorRegistration:vendorRegistration')



# ... your existing views ...

def search_vendors(request):
    """
    API endpoint to search vendors by district or pincode
    Returns JSON response with vendor data
    """
    query = request.GET.get('query', '').strip()
    
    if not query:
        return JsonResponse({
            'success': False, 
            'error': 'No search query provided',
            'vendors': []
        })
    
    try:
        # Search by district OR pincode (case-insensitive)
        vendors = Vendor.objects.filter(
            Q(district__icontains=query) | Q(pincode__icontains=query)
        ).values(
            'id', 
            'shop_name', 
            'owner_name', 
            'phone_number', 
            'whatsapp_number', 
            'service_type', 
            'district', 
            'pincode'
        )
        
        vendors_list = list(vendors)
        
        return JsonResponse({
            'success': True,
            'vendors': vendors_list,
            'count': len(vendors_list)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'vendors': []
        })