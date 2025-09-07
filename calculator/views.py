from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import RainfallData, CalculationLog
import logging
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


logger = logging.getLogger(__name__)


@login_required
@api_view(['POST'])
def calculate_rainwater_harvest(request):
    try:
        data = request.data
        district_name = data.get('district_name', '').strip()
        length = float(data.get('length', 0))
        width = float(data.get('width', 0))
        
        print(f"🔍 Received: {district_name}, {length}x{width}")
        print(f"👤 User: {request.user}, Authenticated: {request.user.is_authenticated}")
        
        # Validation
        if not district_name or length <= 0 or width <= 0:
            return Response({
                'error': 'Invalid input data'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Find district
        try:
            district = RainfallData.objects.get(district_name__iexact=district_name)
            print(f"✅ Found: {district.district_name}")
        except RainfallData.DoesNotExist:
            return Response({
                'error': f'District "{district_name}" not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Calculate
        roof_area = length * width
        annual_rainfall_mm = float(district.annual_rainfall_mm)
        rainfall_m = annual_rainfall_mm / 1000
        runoff_coefficient = 0.8
        
        water_harvested_liters = roof_area * rainfall_m * runoff_coefficient * 1000
        water_harvested_gallons = water_harvested_liters * 0.264172
        daily_average = water_harvested_liters / 365
        
        # Generate recommendation
        if water_harvested_liters < 1000:
            recommendation = "Consider supplementing with other water conservation methods."
        elif water_harvested_liters < 5000:
            recommendation = "Good potential for household water needs. Consider installing a rainwater harvesting system."
        elif water_harvested_liters < 15000:
            recommendation = "Excellent potential! This could significantly reduce your water bills."
        else:
            recommendation = "Outstanding harvesting potential! Consider larger storage capacity and multiple usage applications."
        
        print(f"✅ Result: {water_harvested_liters:.0f} liters")
        
        # ✅ FIXED: Save calculation to database WITH USER
        try:
            calculation_log = CalculationLog.objects.create(
                user=request.user if request.user.is_authenticated else None,  # ✅ ADD THIS LINE
                district=district,
                roof_length=length,
                roof_width=width,
                roof_area=roof_area,
                water_harvested_liters=water_harvested_liters,
                runoff_coefficient=runoff_coefficient,
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
                session_id=request.session.session_key
            )
            print(f"💾 Saved calculation log ID: {calculation_log.id}")
            print(f"👤 Saved with user: {calculation_log.user}")
            
        except Exception as e:
            print(f"⚠️ Failed to save calculation log: {str(e)}")
            import traceback
            print(traceback.format_exc())
        
        # Response data
        response_data = {
            'calculation_id': calculation_log.id if 'calculation_log' in locals() else None,  # ✅ ADD THIS
            'user': request.user.username if request.user.is_authenticated else None,  # ✅ ADD THIS
            'district_name': district.district_name,
            'state': district.state or 'Not specified',
            'annual_rainfall_mm': annual_rainfall_mm,
            'roof_area_sqm': round(roof_area, 2),
            'water_harvested_liters': round(water_harvested_liters, 2),
            'water_harvested_gallons': round(water_harvested_gallons, 2),
            'runoff_coefficient': runoff_coefficient,
            'daily_average_liters': round(daily_average, 2),
            'recommendation': recommendation
        }
        
        return Response({
            'success': True,
            'data': response_data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"❌ Calculate error: {e}")
        import traceback
        print(traceback.format_exc())
        return Response({
            'error': 'Internal server error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ⭐ NEW: Helper function to get client IP
def get_client_ip(request):
    """Get client IP address from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@api_view(['GET'])

def list_districts(request):
    """
    Get list of districts using DRF.
    """
    try:
        # ✅ Use request.query_params (DRF way)
        search = request.query_params.get('search', '')
        
        queryset = RainfallData.objects.all()
        
        if search:
            queryset = queryset.filter(
                Q(district_name__istartswith=search) 
                # Q(state__icontains=search)
            )
        
        queryset = queryset.order_by('district_name')[:50]
        
        # Simple data conversion
        districts_data = []
        for district in queryset:
            districts_data.append({
                'district_name': district.district_name,
                'state': district.state or 'Not specified',
                'annual_rainfall_mm': float(district.annual_rainfall_mm)
            })
        
        print(f"🔍 Districts found: {len(districts_data)}")
        
        return Response({
            'success': True,
            'count': len(districts_data),
            'districts': districts_data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"❌ Districts error: {str(e)}")
        return Response({
            'error': f'Failed to fetch districts: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
# def list_districts(request):
#     query = request.GET.get('search','')
#     results = []
#     if query :
#         results = RainfallData.objects.filter(Q(district_name__icontains = query) | Q(state__icontains = query))
#     return render(request,'demo.html',{'query':query,'results':results})

# def list_districts(request):
#     query = request.GET.get('search', '')
#     results = []
    
#     if query:
#         results = RainfallData.objects.filter(
#             Q(district_name__icontains=query) | 
#             Q(state__icontains=query)
#         )
    
#     return render(request, 'demo.html', {'query': query, 'results': results})


@api_view(['GET'])
def get_district_info(request, district_name):
    """
    Get specific district info using DRF.
    """
    try:
        district = get_object_or_404(RainfallData, district_name__iexact=district_name)
        
        return Response({
            'success': True,
            'data': {
                'district_name': district.district_name,
                'state': district.state or 'Not specified',
                'annual_rainfall_mm': float(district.annual_rainfall_mm)
            }
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'error': f'District "{district_name}" not found'
        }, status=status.HTTP_404_NOT_FOUND)

# ✅ Simple view for serving frontend (no DRF needed)
def calculator_view(request):
    from django.shortcuts import render
    return render(request, 'calculator.html')

def home_view(request):
    from django.shortcuts import render
    return render(request, 'home.html')

