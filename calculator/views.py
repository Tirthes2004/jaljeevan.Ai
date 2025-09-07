from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import RainfallData, CalculationLog
import logging
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from math import sqrt, pi



logger = logging.getLogger(__name__)


@login_required
@api_view(['POST'])
# def calculate_rainwater_harvest(request):
#     try:
#         data = request.data
#         district_name = data.get('district_name', '').strip()
#         length = float(data.get('length', 0))
#         width = float(data.get('width', 0))
#         roof_type = data.get('roof_type',"TERRACE")
#         number_of_dwellers = data.get('number_of_dwellers',5)
        
#         print(f"🔍 Received: {district_name}, {length}x{width}")
#         print(f"👤 User: {request.user}, Authenticated: {request.user.is_authenticated}")
        
#         # Validation
#         if not district_name or length <= 0 or width <= 0:
#             return Response({
#                 'error': 'Invalid input data'
#             }, status=status.HTTP_400_BAD_REQUEST)
        
#         # Find district
#         try:
#             district = RainfallData.objects.get(district_name__iexact=district_name)
#             print(f"✅ Found: {district.district_name}")
#         except RainfallData.DoesNotExist:
#             return Response({
#                 'error': f'District "{district_name}" not found'
#             }, status=status.HTTP_404_NOT_FOUND)
        
#         # Calculate
#         roof_area = length * width
#         annual_rainfall_mm = float(district.annual_rainfall_mm)
#         rainfall_m = annual_rainfall_mm / 1000
        
#         if (roof_type.upper() == "RCC" or roof_type.upper() == "TERRACE" or roof_type.upper() == "METAL SHEET") :
#             runoff_coefficient = 0.85
#         elif (roof_type.upper() == "TILE ROOF") :
#             runoff_coefficient = 0.75
#         elif (roof_type.upper() == "ASBESTOS" or roof_type.upper() == "ROUGH SURFACE"):
#             runoff_coefficient = 0.6
#         elif (roof_type.upper() == "GREEN ROOF" or roof_type.upper() == "SOIL"):
#             runoff_coefficient = 0.4
#         else:
#             runoff_coefficient = 0.8

#         perCapita_LPD = 135
#         water_harvested_liters = roof_area * rainfall_m * runoff_coefficient * 1000

#         annual_demand_liters = number_of_dwellers * perCapita_LPD * 365

#         feasibility = (water_harvested_liters / annual_demand_liters) * 100 

#         water_harvested_gallons = water_harvested_liters * 0.264172
#         daily_average = water_harvested_liters / 365
        
#         # Generate recommendation
#         if water_harvested_liters < 1000:
#             recommendation = "Consider supplementing with other water conservation methods."
#         elif water_harvested_liters < 5000:
#             recommendation = "Good potential for household water needs. Consider installing a rainwater harvesting system."
#         elif water_harvested_liters < 15000:
#             recommendation = "Excellent potential! This could significantly reduce your water bills."
#         else:
#             recommendation = "Outstanding harvesting potential! Consider larger storage capacity and multiple usage applications."
        
#         print(f"✅ Result: {water_harvested_liters:.0f} liters")
        
#         # ✅ FIXED: Save calculation to database WITH USER
#         try:
#             calculation_log = CalculationLog.objects.create(
#                 user=request.user if request.user.is_authenticated else None,  # ✅ ADD THIS LINE
#                 district=district,
#                 roof_length=length,
#                 roof_width=width,
#                 roof_area=roof_area,
#                 water_harvested_liters=water_harvested_liters,
#                 runoff_coefficient=runoff_coefficient,
#                 ip_address=get_client_ip(request),
#                 user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
#                 session_id=request.session.session_key
#             )
#             print(f"💾 Saved calculation log ID: {calculation_log.id}")
#             print(f"👤 Saved with user: {calculation_log.user}")
            
#         except Exception as e:
#             print(f"⚠️ Failed to save calculation log: {str(e)}")
#             import traceback
#             print(traceback.format_exc())
        
#         # Response data
#         response_data = {
#             'calculation_id': calculation_log.id if 'calculation_log' in locals() else None,  # ✅ ADD THIS
#             'user': request.user.username if request.user.is_authenticated else None,  # ✅ ADD THIS
#             'district_name': district.district_name,
#             'state': district.state or 'Not specified',
#             'annual_rainfall_mm': annual_rainfall_mm,
#             'roof_area_sqm': round(roof_area, 2),
#             'water_harvested_liters': round(water_harvested_liters, 2),
#             'water_harvested_gallons': round(water_harvested_gallons, 2),
#             'runoff_coefficient': runoff_coefficient,
#             'daily_average_liters': round(daily_average, 2),
#             'recommendation': recommendation
#         }
        
#         return Response({
#             'success': True,
#             'data': response_data
#         }, status=status.HTTP_200_OK)
        
#     except Exception as e:
#         print(f"❌ Calculate error: {e}")
#         import traceback
#         print(traceback.format_exc())
#         return Response({
#             'error': 'Internal server error'
#         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@login_required
def calculate_rainwater_harvest(request):
    try:
        data = request.data
        district_name = data.get('district_name', '').strip()
        length = float(data.get('length', 0))
        width = float(data.get('width', 0))
        roof_type = data.get('roof_type', "TERRACE")
        number_of_dwellers = int(data.get('number_of_dwellers', 5))
        
        # Optional inputs with defaults
        per_capita_lpd = int(data.get('per_capita_lpd', 135))
        first_flush_mm = float(data.get('first_flush_mm', 2))        # mm
        tank_fraction = float(data.get('tank_fraction', 0.10))       # fraction of annual harvest
        percolation_efficiency = float(data.get('percolation_efficiency', 0.5))
        num_pits = int(data.get('num_pits', 2))
        pit_depth_m = float(data.get('pit_depth_m', 2.0))
        
        # Validation
        if not district_name or length <= 0 or width <= 0:
            return Response({'error': 'Invalid input data'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Find district rainfall
        try:
            district = RainfallData.objects.get(district_name__iexact=district_name)
        except RainfallData.DoesNotExist:
            return Response({'error': f'District "{district_name}" not found'}, status=status.HTTP_404_NOT_FOUND)
        
        roof_area = length * width
        annual_rainfall_mm = float(district.annual_rainfall_mm)
        
        # Runoff coefficient mapping
        if roof_type.upper() in ["RCC", "TERRACE", "METAL SHEET"]:
            runoff_coefficient = 0.85
        elif roof_type.upper() == "TILE ROOF":
            runoff_coefficient = 0.75
        elif roof_type.upper() in ["ASBESTOS", "ROUGH SURFACE"]:
            runoff_coefficient = 0.6
        elif roof_type.upper() in ["GREEN ROOF", "SOIL"]:
            runoff_coefficient = 0.4
        else:
            runoff_coefficient = 0.8  # fallback
        
        # Core calculations
        harvested_liters = roof_area * annual_rainfall_mm * runoff_coefficient  # L
        annual_demand_liters = number_of_dwellers * per_capita_lpd * 365
        feasibility_pct = (harvested_liters / annual_demand_liters) * 100 if annual_demand_liters > 0 else 0
        
        # First flush
        first_flush_liters = roof_area * first_flush_mm
        
        # Tank sizing (fraction method)
        tank_volume_liters = tank_fraction * harvested_liters
        
        # Recharge available
        available_recharge_liters = harvested_liters - first_flush_liters - tank_volume_liters
        
        # Required pit volume (accounting percolation efficiency)
        required_pit_volume_liters = available_recharge_liters / percolation_efficiency if percolation_efficiency > 0 else 0
        each_pit_volume_liters = required_pit_volume_liters / num_pits if num_pits > 0 else 0
        each_pit_volume_m3 = each_pit_volume_liters / 1000
        
        # Pit dimensions (circular, depth = pit_depth_m)
        pit_area_m2 = each_pit_volume_m3 / pit_depth_m if pit_depth_m > 0 else 0
        pit_diameter_m = 2 * sqrt(pit_area_m2 / pi) if pit_area_m2 > 0 else 0
        
        # Recommendation (basic)
        if feasibility_pct < 40:
            recommendation = "Low coverage. Consider supplementing with other water conservation methods."
        elif feasibility_pct < 80:
            recommendation = "Moderate coverage. Good potential for household needs."
        else:
            recommendation = "High coverage! Excellent potential to meet most of your needs."
        
        # Save log
        try:
            calculation_log = CalculationLog.objects.create(
                user=request.user if request.user.is_authenticated else None,
                district=district,
                roof_length=length,
                roof_width=width,
                roof_area=roof_area,
                water_harvested_liters=harvested_liters,
                runoff_coefficient=runoff_coefficient,
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
                session_id=request.session.session_key
            )
        except Exception as e:
            print(f"⚠️ Log save failed: {e}")
            calculation_log = None
        
        # Response data
        response_data = {
            'calculation_id': calculation_log.id if calculation_log else None,
            'district_name': district.district_name,
            'annual_rainfall_mm': annual_rainfall_mm,
            'roof_area_m2': roof_area,
            'harvested_liters': round(harvested_liters, 2),
            'annual_demand_liters': annual_demand_liters,
            'feasibility_percent': round(feasibility_pct, 2),
            'first_flush_liters': round(first_flush_liters, 2),
            'tank_volume_liters': round(tank_volume_liters, 2),
            'available_recharge_liters': round(available_recharge_liters, 2),
            'required_pit_volume_liters': round(required_pit_volume_liters, 2),
            'each_pit_volume_liters': round(each_pit_volume_liters, 2),
            'each_pit_volume_m3': round(each_pit_volume_m3, 2),
            'pit_diameter_m': round(pit_diameter_m, 2),
            'runoff_coefficient': runoff_coefficient,
            'recommendation': recommendation
        }
        
        return Response({'success': True, 'data': response_data}, status=status.HTTP_200_OK)
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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

