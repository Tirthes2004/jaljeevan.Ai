from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import *


@login_required
def application_form(request):
    return render(request, 'application_form.html')


@login_required
def application_dashboard(request):
    # Get officer's district
    officer = Officer.objects.filter(officer_email=request.user.email).first()
    officer_district = officer.assigned_district if officer else None
    
    # Get applications for officer's district
    data = []
    if officer_district:
        applications = SubsidyApplication.objects.filter(
            status='SUBMITTED',
            district=officer_district
        )
        
        data = [{
            'application_id': app.application_id,
            'full_name': app.full_name,
            'email': app.email,
            'mobile': app.mobile,
            'aadhar_or_id': app.aadhaar_or_id,
            'district': app.district,
            'pincode': app.pincode,
            'property_address': app.property_address,
            'created_at': app.created_at.strftime('%d %b %Y, %H:%M'),
            'geo_latitude': app.geo_latitude,
            'geo_longitude': app.geo_longitude,
            'gps_accuracy_meters': app.gps_accuracy_meters,
            'calculation_pdf_url': app.calculation_pdf.url if app.calculation_pdf else None
        } for app in applications]
    
    return render(request, 'application_dashboard.html', {'data': data, 'officer': officer})


@csrf_exempt
@require_http_methods(["POST"])
def registerOfficer(request):
    officer_name = request.POST.get('officer_name')
    govt_id = request.POST.get('govt_id')
    officer_email = request.POST.get('officer_email')
    officer_phone = request.POST.get('officer_phone')  # Fixed typo
    assigned_district = request.POST.get('assigned_district')
    password = request.POST.get('password')
    confirm_password = request.POST.get('confirm_password')
    
    # Validation
    if not all([officer_name, officer_email, govt_id, officer_phone, assigned_district, password, confirm_password]):
        return JsonResponse({
            'success': False,
            'message': 'All fields are required!'
        })
    
    if password != confirm_password:
        return JsonResponse({
            'success': False,
            'message': 'Passwords do not match!'
        })
    
    # Check if email exists
    if Officer.objects.filter(officer_email=officer_email).exists():
        return JsonResponse({
            'success': False,
            'message': 'Email already exists. Try another.'
        })
    
    # Check if govt_id exists
    if Officer.objects.filter(govt_id=govt_id).exists():
        return JsonResponse({
            'success': False,
            'message': 'Government ID already exists. Try another.'
        })
    
    try:
        # Create officer
        officer = Officer.objects.create(
            officer_name=officer_name,
            officer_email=officer_email,
            govt_id=govt_id,
            officer_phone=officer_phone,
            assigned_district=assigned_district,
            password=password
        )
        
        # Note: Officers can't use Django's default login system
        # You need custom session handling or redirect to login
        return JsonResponse({
            'success': True,
            'message': 'Officer account created successfully! Please login.',
            'redirect_url': '/'  # Redirect to home to open login modal
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error creating account: {str(e)}'
        })


@csrf_exempt
@require_http_methods(["POST"])
def loginOfficer(request):
    officer_name = request.POST.get('officer_name')
    govt_id = request.POST.get('govt_id')
    password = request.POST.get('password')
    
    if not all([officer_name, govt_id, password]):
        return JsonResponse({
            'success': False,
            'message': 'All fields are required!'
        })
    
    try:
        # Find officer
        officer = Officer.objects.get(officer_name=officer_name, govt_id=govt_id)
        
        # Check password
        if officer.check_password(password):
            # Store officer info in session
            request.session['officer_id'] = officer.id
            request.session['officer_name'] = officer.officer_name
            request.session['officer_email'] = officer.officer_email
            request.session['is_officer'] = True
            
            return JsonResponse({
                'success': True,
                'message': 'Successfully logged in!',
                'redirect_url': '/officer/'  # Redirect to dashboard
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Invalid credentials!'
            })
    except Officer.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Invalid credentials!'
        })


@csrf_exempt
@login_required
def submit_application(request):
    """API endpoint - handles form submission"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'}, status=400)
    
    try:
        application = SubsidyApplication.objects.create(
            user=request.user,
            full_name=request.POST.get('full_name'),
            mobile=request.POST.get('mobile'),
            email=request.POST.get('email'),
            aadhaar_or_id=request.POST.get('aadhaar_or_id'),
            address=request.POST.get('address'),
            account_holder_name=request.POST.get('account_holder_name'),
            account_number=request.POST.get('account_number'),
            ifsc_code=request.POST.get('ifsc_code'),
            property_address=request.POST.get('property_address'),
            district=request.POST.get('district'),
            pincode=request.POST.get('pincode'),
            geo_latitude=request.POST.get('geo_latitude') or None,
            geo_longitude=request.POST.get('geo_longitude') or None,
            gps_accuracy_meters=request.POST.get('gps_accuracy_meters') or None,
            location_capture_mode=request.POST.get('location_capture_mode', 'manual'),
            manual_address_entry=request.POST.get('manual_address_entry', ''),
            calculation_pdf=request.FILES.get('calculation_pdf'),
            consent_given=request.POST.get('consent_given') == 'true'
        )
        
        return JsonResponse({
            'success': True,
            'application_id': application.application_id,
            'status': application.status,
            'created_at': application.created_at.strftime('%Y-%m-%d %H:%M')
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def track_applications(request):
    """API endpoint to get all user's applications"""
    applications = SubsidyApplication.objects.filter(user=request.user).order_by('-created_at')
    
    data = [{
        'application_id': app.application_id,
        'full_name': app.full_name,
        'district': app.district,
        'property_address': app.property_address,
        'status': app.status,
        'status_display': app.get_status_display(),
        'created_at': app.created_at.strftime('%d %b %Y, %H:%M'),
        'updated_at': app.updated_at.strftime('%d %b %Y, %H:%M'),
        'rejection_reason': app.rejection_reason if app.status == 'REJECTED' else None,
        'rejection_code': app.rejection_code if app.status == 'REJECTED' else None,
        'admin_remarks': app.admin_remarks if app.admin_remarks else None,
        'decided_at': app.decided_at.strftime('%d %b %Y, %H:%M') if app.decided_at else None,
    } for app in applications]
    
    return JsonResponse({
        'success': True,
        'applications': data,
        'count': len(data)
    })