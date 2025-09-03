from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404, render
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal, ROUND_HALF_UP
from .models import RainfallData, CalculationLog
from .serializers import (
    RainfallCalculationRequestSerializer,
    RainfallCalculationResponseSerializer,
    RainfallDataSerializer
)
import logging
import json

logger = logging.getLogger(__name__)

# Constants for calculations
ROOF_TYPE_COEFFICIENTS = {
    'concrete': 0.80,
    'metal': 0.90,
    'tile': 0.70,
    'asphalt': 0.75,
    'green_roof': 0.30,
    'gravel': 0.60,
    'membrane': 0.85,
    'slate': 0.75
}

LITERS_TO_GALLONS = 0.264172
MAX_ROOF_DIMENSION = 1000  # meters
MAX_ROOF_AREA = 50000  # square meters (5 hectares)

# Monthly rainfall distribution (Indian average - adjust per region if needed)
MONTHLY_DISTRIBUTION = [0.05, 0.06, 0.08, 0.12, 0.15, 0.18, 0.20, 0.08, 0.04, 0.02, 0.01, 0.01]
@csrf_exempt
@api_view(['POST'])
def calculate_rainwater_harvest(request):
    """
    Enhanced rainwater harvesting calculator with comprehensive analysis.
    """
    serializer = RainfallCalculationRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({
            'error': 'Invalid input data',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Extract validated data
        district_name = serializer.validated_data['district_name']
        length = float(serializer.validated_data['length'])
        width = float(serializer.validated_data['width'])
        roof_type = serializer.validated_data.get('roof_type', 'concrete')
        has_first_flush = serializer.validated_data.get('has_first_flush', False)
        gutter_condition = serializer.validated_data.get('gutter_condition', 'good')
        
        # Validate roof dimensions
        validate_roof_dimensions(length, width)
        
        # Fetch rainfall data from database
        rainfall_data = get_object_or_404(
            RainfallData,
            district_name__iexact=district_name
        )
        
        # Perform enhanced calculations
        calculations = perform_enhanced_calculations(
            length=length,
            width=width,
            annual_rainfall_mm=float(rainfall_data.annual_rainfall_mm),
            roof_type=roof_type,
            has_first_flush=has_first_flush,
            gutter_condition=gutter_condition
        )
        
        # Generate comprehensive recommendations
        recommendations = generate_comprehensive_recommendation(
            calculations['water_harvested_liters'],
            calculations['roof_area'],
            float(rainfall_data.annual_rainfall_mm),
            roof_type
        )
        
        # Calculate cost savings
        cost_savings = calculate_cost_savings(calculations['water_harvested_liters'])
        
        # Calculate monthly harvest distribution
        monthly_harvest = calculate_monthly_harvest(
            float(rainfall_data.annual_rainfall_mm),
            calculations['roof_area'],
            calculations['effective_runoff_coefficient']
        )
        
        # Prepare enhanced response
        response_data = {
            'district_name': rainfall_data.district_name,
            'state': rainfall_data.state or 'Not specified',
            'annual_rainfall_mm': float(rainfall_data.annual_rainfall_mm),
            'roof_area_sqm': calculations['roof_area'],
            'roof_type': roof_type.replace('_', ' ').title(),
            'water_harvested_liters': calculations['water_harvested_liters'],
            'water_harvested_gallons': calculations['water_harvested_gallons'],
            'runoff_coefficient': calculations['runoff_coefficient'],
            'collection_efficiency': calculations['collection_efficiency'],
            'effective_runoff_coefficient': calculations['effective_runoff_coefficient'],
            'daily_average_liters': calculations['daily_average_liters'],
            'monthly_average_liters': calculations['monthly_average_liters'],
            'peak_monthly_harvest': max(monthly_harvest),
            'lowest_monthly_harvest': min(monthly_harvest),
            'monthly_harvest_data': monthly_harvest,
            'recommendations': recommendations,
            'cost_savings': cost_savings,
            'environmental_impact': calculate_environmental_impact(calculations['water_harvested_liters']),
            'system_specifications': generate_system_specifications(calculations['water_harvested_liters'], calculations['daily_average_liters'])
        }
        
        # Enhanced logging
        enhanced_log_calculation(
            district=rainfall_data,
            length=length,
            width=width,
            calculations=calculations,
            roof_type=roof_type,
            request=request
        )
        
        response_serializer = RainfallCalculationResponseSerializer(data=response_data)
        response_serializer.is_valid(raise_exception=True)
        
        return Response({
            'success': True,
            'data': response_serializer.validated_data,
            'calculation_timestamp': timezone.now().isoformat(),
            'api_version': '2.0'
        }, status=status.HTTP_200_OK)
        
    except ValidationError as e:
        logger.warning(f"Validation error for district {district_name}: {str(e)}")
        return Response({
            'error': 'Validation Error',
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Calculation error for district {district_name}: {str(e)}")
        return Response({
            'error': 'Internal server error',
            'message': 'Unable to process calculation request',
            'support_info': 'Please check your input data and try again'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def validate_roof_dimensions(length, width):
    """
    Validate roof dimensions are reasonable and safe.
    """
    if length <= 0 or width <= 0:
        raise ValidationError("Roof dimensions must be greater than 0.")
    
    if length > MAX_ROOF_DIMENSION or width > MAX_ROOF_DIMENSION:
        raise ValidationError(f"Individual roof dimensions cannot exceed {MAX_ROOF_DIMENSION} meters. Please check your measurements.")
    
    roof_area = length * width
    if roof_area > MAX_ROOF_AREA:
        raise ValidationError(f"Roof area ({roof_area:.2f} m²) exceeds maximum limit of {MAX_ROOF_AREA} m². Please verify your dimensions.")
    
    # Check for unreasonably small areas
    if roof_area < 1:
        raise ValidationError("Roof area seems too small. Minimum area should be at least 1 m².")
    
    return True

def get_runoff_coefficient(roof_type):
    """
    Get runoff coefficient based on roof material type.
    """
    return ROOF_TYPE_COEFFICIENTS.get(roof_type.lower(), 0.8)

def calculate_collection_efficiency(has_first_flush=False, gutter_condition='good'):
    """
    Calculate realistic collection efficiency based on system setup.
    """
    base_efficiency = 0.85  # Account for evaporation, splash losses, maintenance
    
    # First flush diverter improves water quality and reduces initial waste
    if has_first_flush:
        base_efficiency += 0.05
    
    # Gutter condition affects collection
    gutter_adjustments = {
        'excellent': 0.05,
        'good': 0.0,
        'fair': -0.05,
        'poor': -0.10
    }
    base_efficiency += gutter_adjustments.get(gutter_condition, 0.0)
    
    # Cap efficiency at realistic maximum
    return min(base_efficiency, 0.95)

def perform_enhanced_calculations(length, width, annual_rainfall_mm, roof_type='concrete', 
                                has_first_flush=False, gutter_condition='good'):
    """
    Perform comprehensive rainwater harvesting calculations.
    """
    # Calculate roof area
    roof_area = length * width
    
    # Get material-specific runoff coefficient
    runoff_coefficient = get_runoff_coefficient(roof_type)
    
    # Calculate collection efficiency
    collection_efficiency = calculate_collection_efficiency(has_first_flush, gutter_condition)
    
    # Effective runoff coefficient (combines material efficiency and collection efficiency)
    effective_runoff_coefficient = runoff_coefficient * collection_efficiency
    
    # Convert rainfall to meters
    rainfall_m = annual_rainfall_mm / 1000
    
    # Calculate harvested water volume (liters)
    water_harvested_liters = roof_area * rainfall_m * effective_runoff_coefficient * 1000
    
    # Convert to gallons
    water_harvested_gallons = water_harvested_liters * LITERS_TO_GALLONS
    
    # Calculate daily and monthly averages
    daily_average_liters = water_harvested_liters / 365
    monthly_average_liters = water_harvested_liters / 12
    
    # Round all values appropriately
    return {
        'roof_area': round(roof_area, 2),
        'runoff_coefficient': runoff_coefficient,
        'collection_efficiency': round(collection_efficiency, 3),
        'effective_runoff_coefficient': round(effective_runoff_coefficient, 3),
        'water_harvested_liters': round(water_harvested_liters, 2),
        'water_harvested_gallons': round(water_harvested_gallons, 2),
        'daily_average_liters': round(daily_average_liters, 2),
        'monthly_average_liters': round(monthly_average_liters, 2)
    }

def calculate_monthly_harvest(annual_rainfall_mm, roof_area, effective_runoff_coefficient):
    """
    Calculate month-wise harvest potential based on seasonal distribution.
    """
    monthly_harvest = []
    
    for month_factor in MONTHLY_DISTRIBUTION:
        monthly_rain = annual_rainfall_mm * month_factor
        monthly_volume = roof_area * (monthly_rain / 1000) * effective_runoff_coefficient * 1000
        monthly_harvest.append(round(monthly_volume, 2))
    
    return monthly_harvest

def generate_comprehensive_recommendation(water_harvested_liters, roof_area, rainfall_mm, roof_type):
    """
    Generate detailed recommendations with storage and usage advice.
    """
    daily_average = water_harvested_liters / 365
    
    # Calculate suggested tank size (typically 7-14 days supply for peak usage)
    suggested_tank_size = daily_average * 10
    
    recommendations = {
        'harvesting_potential': '',
        'storage_suggestion': '',
        'tank_size_liters': round(suggested_tank_size, 0),
        'usage_applications': [],
        'payback_period': '',
        'installation_priority': '',
        'maintenance_tips': []
    }
    
    # Determine harvesting potential and recommendations
    if water_harvested_liters < 1000:
        recommendations['harvesting_potential'] = "Limited potential due to low rainfall or small roof area."
        recommendations['storage_suggestion'] = f"Small tank ({int(suggested_tank_size)}L) for basic garden use."
        recommendations['usage_applications'] = ["Garden watering", "Car washing", "Emergency backup"]
        recommendations['installation_priority'] = "Low - Consider other water conservation methods first"
        recommendations['payback_period'] = "7-10 years"
        
    elif water_harvested_liters < 5000:
        recommendations['harvesting_potential'] = "Good potential for supplemental household water supply."
        recommendations['storage_suggestion'] = f"Medium tank system ({int(suggested_tank_size)}L) with basic filtration."
        recommendations['usage_applications'] = ["Garden irrigation", "Toilet flushing", "Laundry", "Floor cleaning"]
        recommendations['installation_priority'] = "Medium - Good investment for water savings"
        recommendations['payback_period'] = "4-6 years"
        
    elif water_harvested_liters < 15000:
        recommendations['harvesting_potential'] = "Excellent potential! Could significantly reduce water bills."
        recommendations['storage_suggestion'] = f"Large tank system ({int(suggested_tank_size)}L) with overflow management."
        recommendations['usage_applications'] = ["All non-potable uses", "Pool filling", "HVAC systems", "Emergency supply"]
        recommendations['installation_priority'] = "High - Excellent return on investment"
        recommendations['payback_period'] = "2-4 years"
        
    else:
        recommendations['harvesting_potential'] = "Outstanding potential! Consider comprehensive system design."
        recommendations['storage_suggestion'] = f"Multi-tank system ({int(suggested_tank_size)}L+) with advanced filtration."
        recommendations['usage_applications'] = ["Complete household supply", "Commercial applications", "Community sharing"]
        recommendations['installation_priority'] = "Very High - Exceptional water independence opportunity"
        recommendations['payback_period'] = "1-3 years"
    
    # Add maintenance tips based on roof type and system size
    recommendations['maintenance_tips'] = generate_maintenance_tips(roof_type, water_harvested_liters)
    
    return recommendations

def generate_maintenance_tips(roof_type, harvest_volume):
    """Generate maintenance tips based on system specifications."""
    tips = [
        "Clean gutters and downspouts quarterly",
        "Inspect roof surface for debris monthly",
        "Check tank water quality every 6 months"
    ]
    
    if roof_type in ['tile', 'slate']:
        tips.append("Remove moss and algae from roof tiles annually")
    
    if harvest_volume > 10000:
        tips.extend([
            "Install automatic tank cleaning system",
            "Consider UV sterilization for large volumes",
            "Professional system inspection annually"
        ])
    
    return tips

def calculate_cost_savings(water_harvested_liters):
    """
    Calculate potential cost savings based on local water rates.
    """
    # Average water cost in India (adjust based on region)
    water_cost_per_1000L = 15.0  # INR
    
    annual_savings = (water_harvested_liters / 1000) * water_cost_per_1000L
    monthly_savings = annual_savings / 12
    
    # Calculate 10-year savings
    ten_year_savings = annual_savings * 10
    
    return {
        'annual_savings_inr': round(annual_savings, 2),
        'monthly_savings_inr': round(monthly_savings, 2),
        'ten_year_savings_inr': round(ten_year_savings, 2),
        'cost_per_liter_inr': water_cost_per_1000L / 1000,
        'currency': 'INR',
        'note': 'Savings calculated based on average municipal water rates'
    }

def calculate_environmental_impact(water_harvested_liters):
    """
    Calculate environmental benefits of rainwater harvesting.
    """
    # CO2 savings (approximate values)
    co2_per_liter = 0.0003  # kg CO2 per liter (water treatment and distribution)
    annual_co2_savings = water_harvested_liters * co2_per_liter
    
    # Groundwater recharge benefit
    groundwater_benefit = water_harvested_liters * 0.8  # 80% could recharge groundwater
    
    return {
        'annual_co2_savings_kg': round(annual_co2_savings, 2),
        'groundwater_recharge_potential_liters': round(groundwater_benefit, 2),
        'equivalent_trees_planted': round(annual_co2_savings / 21.77, 1),  # 1 tree absorbs ~21.77 kg CO2/year
        'reduced_stormwater_runoff_liters': round(water_harvested_liters * 0.9, 2)
    }

def generate_system_specifications(water_harvested_liters, daily_average_liters):
    """
    Generate technical specifications for the rainwater harvesting system.
    """
    pump_capacity = max(daily_average_liters * 2, 500)  # Minimum 500L/day capacity
    pipe_diameter = 100 if daily_average_liters > 100 else 75  # mm
    
    return {
        'recommended_pump_capacity_lph': round(pump_capacity, 0),
        'main_pipe_diameter_mm': pipe_diameter,
        'filter_type': 'Multi-stage' if water_harvested_liters > 10000 else 'Basic sediment',
        'overflow_capacity_lph': round(daily_average_liters * 5, 0),
        'minimum_tank_inlet_diameter_mm': 150 if water_harvested_liters > 5000 else 100
    }

def enhanced_log_calculation(district, length, width, calculations, roof_type, request):
    """
    Enhanced logging with additional system details.
    """
    try:
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
        
        CalculationLog.objects.create(
            district=district,
            roof_length=Decimal(str(length)),
            roof_width=Decimal(str(width)),
            roof_area=Decimal(str(calculations['roof_area'])),
            water_harvested_liters=Decimal(str(calculations['water_harvested_liters'])),
            runoff_coefficient=Decimal(str(calculations['effective_runoff_coefficient'])),
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=request.session.session_key
        )
        
        logger.info(f"Calculation logged for {district.district_name}: {calculations['water_harvested_liters']}L harvest potential")
        
    except Exception as e:
        logger.warning(f"Failed to log calculation: {str(e)}")

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
    Get list of available districts with enhanced filtering.
    """
    search = request.query_params.get('search', '')
    state = request.query_params.get('state', '')
    min_rainfall = request.query_params.get('min_rainfall', 0)
    
    queryset = RainfallData.objects.filter(is_active=True)
    
    if search:
        queryset = queryset.filter(
            Q(district_name__icontains=search) | 
            Q(state__icontains=search)
        )
    
    if state:
        queryset = queryset.filter(state__icontains=state)
    
    if min_rainfall:
        try:
            min_rainfall_val = float(min_rainfall)
            queryset = queryset.filter(annual_rainfall_mm__gte=min_rainfall_val)
        except ValueError:
            pass
    
    queryset = queryset.order_by('district_name')[:50]  # Limit results
    
    serializer = RainfallDataSerializer(queryset, many=True)
    return Response({
        'success': True,
        'count': len(serializer.data),
        'districts': serializer.data,
        'filters_applied': {
            'search': search,
            'state': state,
            'min_rainfall': min_rainfall
        }
    })

@api_view(['GET'])
def get_district_info(request, district_name):
    """
    Get specific district rainfall information with additional details.
    """
    try:
        district = get_object_or_404(
            RainfallData,
            district_name__iexact=district_name.strip()
        )
        
        serializer = RainfallDataSerializer(district)
        
        # Add some additional computed information
        district_data = serializer.data
        district_data['rainfall_category'] = categorize_rainfall(district.annual_rainfall_mm)
        district_data['best_months_for_harvest'] = get_best_harvest_months(district.annual_rainfall_mm)
        
        return Response({
            'success': True,
            'data': district_data
        })
    except Exception as e:
        logger.warning(f"District lookup failed for '{district_name}': {str(e)}")
        return Response({
            'error': f"District '{district_name}' not found",
            'suggestion': 'Try searching for similar district names using the search endpoint'
        }, status=status.HTTP_404_NOT_FOUND)

def categorize_rainfall(annual_rainfall_mm):
    """Categorize rainfall levels for user understanding."""
    rainfall = float(annual_rainfall_mm)
    
    if rainfall < 600:
        return "Low (Arid/Semi-arid)"
    elif rainfall < 1200:
        return "Moderate (Suitable for harvesting)"
    elif rainfall < 2000:
        return "High (Excellent for harvesting)"
    else:
        return "Very High (Outstanding potential)"

def get_best_harvest_months(annual_rainfall_mm):
    """Determine best months for rainwater harvesting."""
    # Simplified - in reality this would use historical monthly data
    if annual_rainfall_mm > 1500:
        return ["June", "July", "August", "September"]
    else:
        return ["July", "August", "September"]

@api_view(['GET'])
def get_roof_types(request):
    """
    Get available roof types and their coefficients.
    """
    roof_types = []
    for roof_type, coefficient in ROOF_TYPE_COEFFICIENTS.items():
        roof_types.append({
            'type': roof_type,
            'display_name': roof_type.replace('_', ' ').title(),
            'runoff_coefficient': coefficient,
            'description': get_roof_type_description(roof_type)
        })
    
    return Response({
        'success': True,
        'roof_types': roof_types
    })

def get_roof_type_description(roof_type):
    """Get description for roof types."""
    descriptions = {
        'concrete': 'Flat or sloped concrete surfaces - excellent runoff',
        'metal': 'Metal sheeting or tiles - best runoff coefficient',
        'tile': 'Clay or concrete tiles - good runoff with proper maintenance',
        'asphalt': 'Asphalt shingles - moderate runoff, common in residential',
        'green_roof': 'Vegetated roofs - lower runoff but environmental benefits',
        'gravel': 'Gravel-surfaced roofs - moderate runoff',
        'membrane': 'Rubber or synthetic membrane - excellent runoff',
        'slate': 'Natural slate tiles - good runoff, durable'
    }
    return descriptions.get(roof_type, 'Standard roofing material')

@api_view(['GET'])
def health_check(request):
    """
    API health check endpoint.
    """
    try:
        # Test database connection
        district_count = RainfallData.objects.count()
        
        return Response({
            'success': True,
            'message': 'Enhanced Rainwater Harvesting Calculator API is operational',
            'version': '2.0',
            'database_status': 'Connected',
            'districts_available': district_count,
            'timestamp': timezone.now().isoformat(),
            'endpoints': {
                'calculate': '/api/v1/calculate/',
                'districts': '/api/v1/districts/',
                'district_info': '/api/v1/districts/<name>/',
                'roof_types': '/api/v1/roof-types/',
                'health': '/api/v1/health/'
            }
        })
    except Exception as e:
        return Response({
            'success': False,
            'message': 'Database connection error',
            'error': str(e)
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

def demo_view(request):
    """
    Serve the demo frontend page.
    """
    return render(request, 'demo.html')
