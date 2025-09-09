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
import math
from math import sqrt, pi
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status




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
# views.py (Django REST Framework)

# Import your models (adjust paths as needed)
# from .models import RainfallData, CalculationLog

def get_client_ip(request):
    """Simple helper — adapt as needed for proxy headers."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


@api_view(["POST"])
@permission_classes([AllowAny])
def calculate_rainwater_harvest(request):
    

    try:
        data = request.data or {}

        # Helpers to parse numeric values safely
        def to_float(x, default=0.0):
            try:
                return float(x)
            except Exception:
                return default

        def to_int(x, default=0):
            try:
                return int(float(x))
            except Exception:
                return default

        # === Inputs & defaults ===
        district_name = (data.get("district_name") or "").strip()
        annual_rainfall_mm = data.get("annual_rainfall_mm")
        if annual_rainfall_mm is not None:
            annual_rainfall_mm = to_float(annual_rainfall_mm, None)

        length = to_float(data.get("length", 0))
        width = to_float(data.get("width", 0))
        roof_area_m2 = to_float(data.get("roof_area_m2", 0))

        # allow area from length*width
        if roof_area_m2 <= 0 and length > 0 and width > 0:
            roof_area_m2 = length * width

        roof_type = (data.get("roof_type") or "TERRACE").strip()

        number_of_dwellers = to_int(data.get("number_of_dwellers", 1), 1)
        per_capita_lpd = to_float(data.get("per_capita_lpd", 135))
        first_flush_mm = to_float(data.get("first_flush_mm", 2))
        tank_fraction = to_float(data.get("tank_fraction", 0.10))
        percolation_efficiency = to_float(data.get("percolation_efficiency", 0.5))
        num_pits = max(1, to_int(data.get("num_pits", 1)))
        pit_depth_m = max(0.1, to_float(data.get("pit_depth_m", 2.0)))

        percolation_rate_mm_per_hr = data.get("percolation_rate_mm_per_hr")
        if percolation_rate_mm_per_hr is not None:
            percolation_rate_mm_per_hr = to_float(percolation_rate_mm_per_hr, None)

        peak_intensity_mm_per_hr = data.get("peak_intensity_mm_per_hr")
        if peak_intensity_mm_per_hr is not None:
            peak_intensity_mm_per_hr = to_float(peak_intensity_mm_per_hr, None)

        # Optional costs
        unit_cost_per_m3_structure = data.get("unit_cost_per_m3_structure")
        if unit_cost_per_m3_structure is not None:
            unit_cost_per_m3_structure = to_float(unit_cost_per_m3_structure, 2500.0)

        tank_cost_per_l = data.get("tank_cost_per_l")
        if tank_cost_per_l is not None:
            tank_cost_per_l = to_float(tank_cost_per_l, 1.5)

        installation_fixed_costs = data.get("installation_fixed_costs")
        if installation_fixed_costs is not None:
            installation_fixed_costs = to_float(installation_fixed_costs, 10000.0)

        cost_per_kl = data.get("cost_per_kl")
        if cost_per_kl is not None:
            cost_per_kl = to_float(cost_per_kl, 35.0)

        # Basic input validation
        if roof_area_m2 <= 0:
            return Response(
                {"error": "Invalid roof area. Provide 'roof_area_m2' or 'length' and 'width'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # If annual_rainfall_mm not provided, try district lookup
        if annual_rainfall_mm is None:
            if not district_name:
                return Response(
                    {"error": "Provide 'district_name' or 'annual_rainfall_mm'."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # Fetch district from DB
            try:
                district = RainfallData.objects.get(district_name__iexact=district_name)
                annual_rainfall_mm = float(getattr(district, "annual_rainfall_mm", 0.0))
            except RainfallData.DoesNotExist:
                return Response(
                    {"error": f'District "{district_name}" not found and no "annual_rainfall_mm" given.'},
                    status=status.HTTP_404_NOT_FOUND,
                )

        # Runoff coefficient mapping
        rc_map = {
            "RCC": 0.85,
            "TERRACE": 0.85,
            "METAL SHEET": 0.85,
            "TILE": 0.75,
            "TILE ROOF": 0.75,
            "ASBESTOS": 0.6,
            "ROUGH SURFACE": 0.6,
            "GREEN ROOF": 0.4,
            "SOIL": 0.4,
        }
        runoff_coefficient = rc_map.get(roof_type.upper(), 0.8)

        # Validate percolation efficiency
        if percolation_efficiency <= 0 or percolation_efficiency > 1:
            return Response(
                {"error": "percolation_efficiency must be between 0 (exclusive) and 1 (inclusive)."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # === Core calculations ===
        harvested_liters = roof_area_m2 * annual_rainfall_mm * runoff_coefficient  # 1 mm over 1 m2 = 1 L
        daily_demand_l = number_of_dwellers * per_capita_lpd
        annual_demand_l = daily_demand_l * 365
        feasibility_pct = (harvested_liters / annual_demand_l) * 100 if annual_demand_l > 0 else 0.0

        first_flush_liters = roof_area_m2 * first_flush_mm
        tank_volume_liters = max(0.0, tank_fraction * harvested_liters)

        available_recharge_liters = harvested_liters - first_flush_liters - tank_volume_liters
        if available_recharge_liters < 0:
            # Nothing available for recharge after first flush & tank (cap at 0)
            available_recharge_liters = 0.0

        required_pit_volume_liters = available_recharge_liters / percolation_efficiency if percolation_efficiency > 0 else 0.0
        each_pit_volume_liters = required_pit_volume_liters / num_pits if num_pits > 0 else required_pit_volume_liters
        each_pit_volume_m3 = each_pit_volume_liters / 1000.0

        pit_area_m2 = each_pit_volume_m3 / pit_depth_m if pit_depth_m > 0 else 0.0
        pit_diameter_m = 2.0 * math.sqrt(pit_area_m2 / math.pi) if pit_area_m2 > 0 else 0.0

        # Percolation/infiltration daily estimate (if rate provided)
        days_to_infiltrate = None
        daily_infiltration_l = None
        if percolation_rate_mm_per_hr is not None and pit_area_m2 > 0:
            daily_infiltration_l = percolation_rate_mm_per_hr * 24.0 * pit_area_m2
            if daily_infiltration_l > 0:
                days_to_infiltrate = each_pit_volume_liters / daily_infiltration_l

        # Overflow estimate if peak intensity provided
        overflow_rate_l_per_hr = None
        if peak_intensity_mm_per_hr is not None:
            overflow_rate_l_per_hr = peak_intensity_mm_per_hr * roof_area_m2 * runoff_coefficient

        # Optional cost & payback (only calculated if costs supplied)
        total_install_cost = None
        annual_savings = None
        payback_years = None
        if unit_cost_per_m3_structure is not None or tank_cost_per_l is not None or installation_fixed_costs is not None:
            total_install_cost = 0.0
            if unit_cost_per_m3_structure is not None:
                total_install_cost += (required_pit_volume_liters / 1000.0) * unit_cost_per_m3_structure
            if tank_cost_per_l is not None:
                total_install_cost += tank_volume_liters * tank_cost_per_l
            if installation_fixed_costs is not None:
                total_install_cost += installation_fixed_costs

            # Simple savings: assume only tank volume replaces bought water (conservative).
            if cost_per_kl is not None:
                saved_kL = tank_volume_liters / 1000.0
                annual_savings = saved_kL * cost_per_kl
                if annual_savings > 0:
                    payback_years = total_install_cost / annual_savings

        # Recommendation text
        if feasibility_pct >= 80:
            recommendation = "High coverage: RWH can meet most annual demand."
        elif feasibility_pct >= 40:
            recommendation = "Moderate coverage: RWH will contribute significantly; consider storage tuning."
        else:
            recommendation = "Low coverage: RWH will supplement demand; consider demand reduction & other sources."

        # Try saving calculation log (non-blocking)
        calculation_log_id = None
        try:
            calculation_log = CalculationLog.objects.create(
                # adapt fields to your CalculationLog model
                user=request.user if getattr(request, "user", None) and request.user.is_authenticated else None,
                district=district_name if district_name else None,
                roof_length=length if length > 0 else None,
                roof_width=width if width > 0 else None,
                roof_area=roof_area_m2,
                water_harvested_liters=harvested_liters,
                runoff_coefficient=runoff_coefficient,
                ip_address=get_client_ip(request),
                user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
                session_id=getattr(request.session, "session_key", None),
            )
            calculation_log_id = calculation_log.id
        except Exception:
            # Logging must not break the response; ignore if log model differs
            calculation_log_id = None

        # Build response
        response_data = {
            "calculation_id": calculation_log_id,
            "district_name": district_name,
            "annual_rainfall_mm": round(annual_rainfall_mm, 3),
            "roof_area_m2": round(roof_area_m2, 3),
            "runoff_coefficient": round(runoff_coefficient, 3),
            "harvested_liters": round(harvested_liters, 2),
            "daily_demand_l": round(daily_demand_l, 2),
            "annual_demand_l": round(annual_demand_l, 2),
            "feasibility_percent": round(feasibility_pct, 2),
            "first_flush_liters": round(first_flush_liters, 2),
            "tank_volume_liters": round(tank_volume_liters, 2),
            "available_recharge_liters": round(available_recharge_liters, 2),
            "required_pit_volume_liters": round(required_pit_volume_liters, 2),
            "each_pit_volume_liters": round(each_pit_volume_liters, 2),
            "each_pit_volume_m3": round(each_pit_volume_m3, 3),
            "pit_depth_m": round(pit_depth_m, 3),
            "pit_area_m2": round(pit_area_m2, 3),
            "pit_diameter_m": round(pit_diameter_m, 3),
            "percolation_rate_mm_per_hr": percolation_rate_mm_per_hr,
            "daily_infiltration_l": round(daily_infiltration_l, 2) if daily_infiltration_l is not None else None,
            "days_to_infiltrate": round(days_to_infiltrate, 2) if days_to_infiltrate is not None else None,
            "peak_intensity_mm_per_hr": peak_intensity_mm_per_hr,
            "overflow_rate_l_per_hr": round(overflow_rate_l_per_hr, 2) if overflow_rate_l_per_hr is not None else None,
            "costs": {
                "total_install_cost": round(total_install_cost, 2) if total_install_cost is not None else None,
                "annual_savings": round(annual_savings, 2) if annual_savings is not None else None,
                "payback_years": round(payback_years, 2) if payback_years is not None else None,
            },
            "recommendation": recommendation,
        }

        return Response({"success": True, "data": response_data}, status=status.HTTP_200_OK)

    except Exception as exc:
        # avoid leaking internals
        print("Error in calculate_rainwater_harvest:", exc)
        return Response({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



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

