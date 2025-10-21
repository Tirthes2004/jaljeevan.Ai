from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import SubsidyApplication

@login_required
def application_form(request):
    return render(request, 'application_form.html')


def application_dashboard(request):
    return render(request, 'application_dashboard.html')


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
