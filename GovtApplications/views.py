# GovtApplications/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth import logout
from functools import wraps
from .models import *
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone

# ============================================
# CUSTOM DECORATOR FOR OFFICER AUTHENTICATION
# ============================================

def officer_login_required(view_func):
    """Custom decorator to check if officer is logged in via session"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('is_officer'):
            return redirect('/officer/login/')
        return view_func(request, *args, **kwargs)
    return wrapper

# ============================================
# PUBLIC APPLICATION VIEWS (For regular users)
# ============================================

def application_form(request):
    """Public users - Apply for subsidy (no login required)"""
    return render(request, 'application_form.html')

@csrf_exempt
@login_required  # Regular user authentication
def submit_application(request):
    """Public users - Submit subsidy application"""
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
            district=request.POST.get('district').upper(),
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

@login_required  # Regular user authentication
def track_applications(request):
    """Public users - Track their own applications"""
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

# ============================================
# OFFICER PORTAL - AUTHENTICATION
# ============================================

@csrf_exempt
def loginOfficer(request):
    """Officer Login - Fixed for plain text passwords"""
    if request.method == 'GET':
        return redirect('/')
    
    if request.method == 'POST':
        try:
            # Get form data
            officer_name = request.POST.get('officer_name')
            govt_id = request.POST.get('govt_id')
            password = request.POST.get('password')
            
            # Debug log
            print(f"Login attempt - Name: {officer_name}, ID: {govt_id}")
            
            # Validate all fields provided
            if not all([officer_name, govt_id, password]):
                return JsonResponse({
                    'success': False,
                    'message': 'All fields are required!'
                })
            
            # Find officer by name and govt_id
            try:
                officer = Officer.objects.get(
                    officer_name=officer_name,
                    govt_id=govt_id
                )
            except Officer.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid credentials! Officer not found.'
                })
            
            # Check password (plain text comparison since no hashing)
            if officer.password == password:
                # Create session
                request.session['officer_id'] = officer.id
                request.session['officer_name'] = officer.officer_name
                request.session['officer_email'] = officer.officer_email
                request.session['is_officer'] = True
                
                print(f"Login successful for: {officer.officer_name}")
                
                return JsonResponse({
                    'success': True,
                    'message': 'Successfully logged in!',
                    'redirect_url': '/officer/'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid password!'
                })
                
        except Exception as e:
            # Log the actual error
            import traceback
            print(f"Login error: {str(e)}")
            print(traceback.format_exc())
            
            return JsonResponse({
                'success': False,
                'message': f'Server error: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    }, status=405)

@csrf_exempt
@require_http_methods(["POST"])
def registerOfficer(request):
    """Officer Registration - POST only"""
    officer_name = request.POST.get('officer_name')
    govt_id = request.POST.get('govt_id')
    officer_email = request.POST.get('officer_email')
    officer_phone = request.POST.get('officer_phone')
    assigned_district = request.POST.get('assigned_district').upper()
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
        
        return JsonResponse({
            'success': True,
            'message': 'Officer account created successfully! Please login.',
            'redirect_url': '/officer/'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error creating account: {str(e)}'
        })

def logoutOfficer(request):
    """Officer Logout"""
    if request.method == "POST":
        # Clear session data
        request.session.flush()
        return JsonResponse({
            'success': True,
            'message': 'Successfully logged out!',
            'redirect_url': '/officer/'
        })
    
    # For GET request (direct access)
    request.session.flush()
    return redirect('/')


# ============================================
# OFFICER PORTAL - DASHBOARD (Protected by JavaScript, not decorator)
# ============================================

def application_dashboard(request):
    """
    Officers - View dashboard with applications in their district
    Page loads for everyone, but JavaScript auto-opens login modal if not logged in
    """
    
    # Get officer from session (not from request.user)
    officer_email = request.session.get('officer_email')
    officer = Officer.objects.filter(officer_email=officer_email).first()
    
    # Initialize empty data (for non-logged-in users)
    data = []
    
    # Only populate data if officer is logged in
    if officer:
        officer_district = officer.assigned_district
        
        # Get applications for officer's district
        applications = SubsidyApplication.objects.filter(
            status__in=['SUBMITTED', 'UNDER_REVIEW'],
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
            'property_type': getattr(app, 'property_type', 'N/A'),
            'system_type': getattr(app, 'system_type', 'N/A'),
            'estimated_cost': str(getattr(app, 'estimated_cost', '0')),
            'status': app.status,
            'created_at': app.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'geo_latitude': app.geo_latitude,
            'geo_longitude': app.geo_longitude,
            'gps_accuracy_meters': app.gps_accuracy_meters,
            'calculation_pdf_url': app.calculation_pdf.url if app.calculation_pdf else None
        } for app in applications]
    
    context = {
        'officer': officer,
        'data': data
    }
    return render(request, 'application_dashboard.html', context)

# ============================================
# OFFICER PORTAL - APPLICATION ACTIONS
# ============================================

# ============================================
# OFFICER PORTAL - APPLICATION ACTIONS
# ============================================

@csrf_exempt
@require_POST
def approve_application(request):
    """Officers - Approve an application"""
    
    # Check if officer is logged in
    if not request.session.get('is_officer'):
        return JsonResponse({
            'success': False,
            'message': 'You must be logged in as an officer'
        }, status=403)
    
    # Get application_id from POST data (not URL parameter)
    application_id = request.POST.get('application_id')
    
    if not application_id:
        return JsonResponse({
            'success': False,
            'message': 'Application ID is required'
        }, status=400)
    
    try:
        application = SubsidyApplication.objects.get(application_id=application_id)
        application.status = 'APPROVED'
        application.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Application approved successfully!'
        })
    except SubsidyApplication.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Application not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_POST
def reject_application(request):
    """Officers - Reject an application"""
    
    # Check if officer is logged in
    if not request.session.get('is_officer'):
        return JsonResponse({
            'success': False,
            'message': 'You must be logged in as an officer'
        }, status=403)
    
    # Get data from POST body
    application_id = request.POST.get('application_id')
    reason = request.POST.get('reason', '')
    
    if not application_id:
        return JsonResponse({
            'success': False,
            'message': 'Application ID is required'
        }, status=400)
    
    if not reason:
        return JsonResponse({
            'success': False,
            'message': 'Rejection reason is required'
        }, status=400)
    
    try:
        application = SubsidyApplication.objects.get(application_id=application_id)
        application.status = 'REJECTED'
        application.rejection_reason = reason
        application.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Application rejected!'
        })
    except SubsidyApplication.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Application not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_POST
def under_review_application(request):
    """Officers - Mark application as under review"""
    
    # Check if officer is logged in
    if not request.session.get('is_officer'):
        return JsonResponse({
            'success': False,
            'message': 'You must be logged in as an officer'
        }, status=403)
    
    # Get application_id from POST data
    application_id = request.POST.get('application_id')
    
    if not application_id:
        return JsonResponse({
            'success': False,
            'message': 'Application ID is required'
        }, status=400)
    
    try:
        application = SubsidyApplication.objects.get(application_id=application_id)
        application.status = 'UNDER_REVIEW'  # or whatever status you use
        application.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Application marked as under review!'
        })
    except SubsidyApplication.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Application not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)
