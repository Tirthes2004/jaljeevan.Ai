from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse
from .models import RainfallData, CalculationLog, GraphPlot
import logging
import io
import matplotlib
matplotlib.use('Agg')  # Set backend before importing pyplot
import matplotlib.pyplot as plt
import math
from django.utils import timezone

logger = logging.getLogger(__name__)

def get_client_ip(request):
    """Get client IP address from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@api_view(['POST'])
@permission_classes([AllowAny])
def calculate_rainwater_harvest(request):
    """Enhanced calculation API with corrected formulas and realistic costs."""
    try:
        data = request.data or {}
        
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
        
        # Extract inputs
        district_name = (data.get("district_name") or "").strip()
        length = to_float(data.get("length", 0))
        width = to_float(data.get("width", 0))
        roof_area_sqm = to_float(data.get("roof_area_sqm", 0))
        per_capita_lpd = 135
        
        if roof_area_sqm <= 0 and length > 0 and width > 0:
            roof_area_sqm = length * width
            
        roof_type = (data.get("roof_type") or "RCC").strip().upper()
        number_of_dwellers = to_int(data.get("number_of_dwellers", 1), 1)
        annual_rainfall_mm = to_float(data.get("annual_rainfall_mm", 0))
        
        # Validation
        if not district_name:
            return Response({
                'success': False,
                'error': 'District name is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if roof_area_sqm <= 0:
            return Response({
                'success': False,
                'error': 'Valid roof area is required'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        if number_of_dwellers <= 0:
            return Response({
                'success': False,
                'error': 'Number of dwellers must be at least 1'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Handle district lookup and duplicates
        if annual_rainfall_mm <= 0:
            districts = RainfallData.objects.filter(district_name__iexact=district_name)
        
            if not districts.exists():
                return Response({
                    'success': False,
                    'error': f'District "{district_name}" not found in our database. Please search and select from available districts.'
                }, status=status.HTTP_404_NOT_FOUND)
            
            elif districts.count() > 1:
                district_list = [f"{d.district_name} ({d.state})" for d in districts[:3]]
                district_names = ", ".join(district_list)
                return Response({
                    'success': False,
                    'error': f'Multiple districts named "{district_name}" found: {district_names}. Please be more specific or include the state name.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            else:
                district = districts.first()
                annual_rainfall_mm = float(district.annual_rainfall_mm)
                state = district.state or 'Not specified'
        else:
            district = None
            state = 'Custom'
        
        # Runoff coefficients mapping
        runoff_coefficients = {
            'RCC': 0.85,
            'TERRACE': 0.85, 
            'METAL SHEET': 0.85,
            'TILE ROOF': 0.75,
            'TILE': 0.75,
            'ASBESTOS': 0.6,
            'ROUGH SURFACE': 0.6,
            'GREEN ROOF': 0.4,
            'SOIL': 0.4,
        }
        
        runoff_coefficient = runoff_coefficients.get(roof_type, 0.8)
        
        # Core calculations
        water_harvested_liters = roof_area_sqm * annual_rainfall_mm * runoff_coefficient
        water_harvested_gallons = water_harvested_liters * 0.264172
        
        daily_requirement_liters = number_of_dwellers * per_capita_lpd
        annual_requirement_liters = daily_requirement_liters * 365
        
        efficiency_percent = (water_harvested_liters / annual_requirement_liters) * 100 if annual_requirement_liters > 0 else 0
        
        # CORRECTED COST PARAMETERS
        unit_cost_per_m3_structure = 2500.0  # Realistic pit construction cost
        tank_cost_per_l = 8.0  # CORRECTED: Market-realistic tank cost
        installation_fixed_costs = 15000.0  # Slightly higher for quality
        cost_per_kl = 100.0  # CORRECTED: Realistic tanker replacement cost
        
        # PRACTICAL SIZING APPROACH - FIXED: Use GraphPlot instead of RainfallData
        if district:
            try:
                gp = GraphPlot.objects.get(district_name__iexact=district_name)
                months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
                month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                
                rainfall_values = [float(getattr(gp, month, 0)) for month in months]
                max_index = rainfall_values.index(max(rainfall_values))
                
                peak_month = month_names[max_index]
                peak_rainfall = rainfall_values[max_index]
                    
                # Extract the coefficient value first
                runoff_coefficient = runoff_coefficients.get(roof_type, 0.8)  # Get float value
                filtration_efficiency = 0.95  # Account for first flush and filtration losses
                max_monthly_harvest = float(peak_rainfall) * roof_area_sqm * runoff_coefficient * filtration_efficiency
                
                # Storage factor based on household size (practical sizing)
                if number_of_dwellers >= 6:
                    storage_factor = 0.25  # 25% for large families
                elif number_of_dwellers >= 4:
                    storage_factor = 0.20  # 20% for medium families  
                elif number_of_dwellers >= 2:
                    storage_factor = 0.15  # 15% for small families
                else:
                    storage_factor = 0.10  # 10% for single person
                
                # Calculate practical tank size
                practical_tank_liters = max_monthly_harvest * storage_factor
                
                # Apply practical limits (2K-50K liter range)
                practical_tank_liters = max(2000, min(practical_tank_liters, 50000))
            except GraphPlot.DoesNotExist:
                # Fallback if no GraphPlot data
                practical_tank_liters = water_harvested_liters * 0.15
        else:
            # Fallback for custom rainfall input
            practical_tank_liters = water_harvested_liters * 0.15

        tank_volume_liters = practical_tank_liters
        tank_volume_m3 = tank_volume_liters / 1000.0
        
        # First flush calculation
        first_flush_liters = roof_area_sqm * 2
        
        # Practical recharge pit sizing
        if roof_area_sqm >= 200:
            practical_pit_volume_m3 = 25  # Large pit
            pit_diameter_m = 4.0
        elif roof_area_sqm >= 100: 
            practical_pit_volume_m3 = 15  # Medium pit
            pit_diameter_m = 3.5
        else:
            practical_pit_volume_m3 = 10  # Small pit
            pit_diameter_m = 3.0

        pit_depth_m = 2.0
        pit_area_m2 = math.pi * (pit_diameter_m / 2) ** 2
        
        # Available recharge calculation
        available_recharge_liters = max(0, water_harvested_liters - first_flush_liters - tank_volume_liters)
        required_pit_volume_liters = practical_pit_volume_m3 * 1000
        
        # CORRECTED COST CALCULATIONS
        pit_construction_cost = practical_pit_volume_m3 * unit_cost_per_m3_structure
        tank_construction_cost = tank_volume_liters * tank_cost_per_l
        total_install_cost = pit_construction_cost + tank_construction_cost + installation_fixed_costs
        
        # CORRECTED BENEFITS CALCULATION
        utilization_factor = 0.6  # 60% of harvest is actually used
        annual_usage_liters = min(water_harvested_liters * utilization_factor, annual_requirement_liters)
        
        # Multi-source benefits
        municipal_substitution_rate = 0.30  # 30% substitutes municipal water
        municipal_rate_per_kL = 25  # Municipal water rate
        tanker_avoidance_events = 3  # Shortage events avoided per year
        tanker_cost_per_event = 2000  # Cost per tanker delivery
        
        # Calculate realistic annual savings
        municipal_savings = (annual_usage_liters * municipal_substitution_rate / 1000) * municipal_rate_per_kL
        tanker_savings = tanker_avoidance_events * tanker_cost_per_event
        annual_water_savings = municipal_savings + tanker_savings
        
        # CORRECTED MAINTENANCE & PAYBACK
        annual_maintenance_cost = total_install_cost * 0.01  # 1% instead of 2%
        net_annual_savings = annual_water_savings - annual_maintenance_cost
        
        # Payback calculation
        payback_years = total_install_cost / net_annual_savings if net_annual_savings > 0 else None
        roi_percentage = (net_annual_savings * 30 - total_install_cost) / total_install_cost * 100 if total_install_cost > 0 else 0
        
        # Enhanced recommendations
        enhanced_recommendations = [
            f"💰 Total system cost: ₹{total_install_cost:,.0f}",
            f"💧 Annual water savings: ₹{net_annual_savings:,.0f}",
            f"⏱️ Payback period: {payback_years:.1f} years" if payback_years else "⏱️ Long-term investment benefits",
            f"🔧 Recommended tank capacity: {tank_volume_liters:,.0f}L",
            f"🕳️ Pit specifications: {pit_diameter_m:.1f}m diameter, {pit_depth_m}m depth"
        ]
        
        # Generate recommendation
        if efficiency_percent >= 100:
            recommendation = f"🌟 Excellent! Your {roof_area_sqm}m² roof can harvest {water_harvested_liters:,.0f}L annually, fully meeting your {number_of_dwellers}-person household's water needs."
        elif efficiency_percent >= 70:
            recommendation = f"💪 Very Good! Your roof can harvest {water_harvested_liters:,.0f}L annually, covering {efficiency_percent:.0f}% of your household water needs."
        elif efficiency_percent >= 40:
            recommendation = f"👍 Good Potential! Your roof can harvest {water_harvested_liters:,.0f}L annually, covering {efficiency_percent:.0f}% of your water needs."
        elif efficiency_percent >= 20:
            recommendation = f"⚡ Moderate Potential. Your roof can harvest {water_harvested_liters:,.0f}L annually, covering {efficiency_percent:.0f}% of your needs."
        else:
            recommendation = f"💡 Limited harvest potential of {water_harvested_liters:,.0f}L annually. Consider increasing roof area or improving runoff efficiency."
        
        # Prepare response data
        response_data = {
            'district_name': district_name,
            'state': state,
            'annual_rainfall_mm': round(annual_rainfall_mm, 2),
            'roof_area_sqm': round(roof_area_sqm, 2),
            'roof_type': roof_type,
            'runoff_coefficient': round(runoff_coefficient, 2),
            'number_of_dwellers': number_of_dwellers,
            'water_harvested_liters': round(water_harvested_liters, 0),
            'water_harvested_gallons': round(water_harvested_gallons, 0),
            'daily_requirement_liters': daily_requirement_liters,
            'annual_requirement_liters': annual_requirement_liters,
            'efficiency_percent': round(efficiency_percent, 1),
            'recommendation': recommendation,
            'calculation_id': None,
            'user': request.user.username if request.user.is_authenticated else None,
            'is_saved': False,
            
            # Technical specifications
            'tank_volume_liters': round(tank_volume_liters, 0),
            'tank_volume_m3': round(tank_volume_m3, 1),
            'first_flush_liters': round(first_flush_liters, 0),
            'available_recharge_liters': round(available_recharge_liters, 0),
            'required_pit_volume_liters': round(required_pit_volume_liters, 0),
            'pit_diameter_m': round(pit_diameter_m, 1),
            'pit_depth_m': round(pit_depth_m, 1),
            'pit_area_m2': round(pit_area_m2, 1),
            
            # Cost analysis
            'costs': {
                'pit_construction_cost': round(pit_construction_cost, 0),
                'tank_construction_cost': round(tank_construction_cost, 0),
                'installation_fixed_costs': round(installation_fixed_costs, 0),
                'total_install_cost': round(total_install_cost, 0),
                'annual_water_savings': round(annual_water_savings, 0),
                'annual_maintenance_cost': round(annual_maintenance_cost, 0),
                'net_annual_savings': round(net_annual_savings, 0),
                'payback_years': round(payback_years, 1) if payback_years else None,
                'roi_percentage': round(roi_percentage, 1)
            },
            
            'enhanced_recommendations': enhanced_recommendations
        }
    
        return Response({
            'success': True,
            'data': response_data
        }, status=status.HTTP_200_OK)
        
    except Exception as exc:
        logger.error(f"Error in calculate_rainwater_harvest: {str(exc)}", exc_info=True)
        return Response({
            'success': False,
            'error': 'Internal server error. Please try again later.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def list_districts(request):
    """Enhanced district search API with intelligent filtering."""
    try:
        search = request.query_params.get('search', '').strip()
        
        queryset = RainfallData.objects.all()
        
        if search:
            queryset = queryset.filter(
                Q(district_name__icontains=search) | 
                Q(state__icontains=search)
            ).distinct()
        
        data = [{
            'district_name': d.district_name,
            'state': d.state or 'Not specified',
            'annual_rainfall_mm': round(float(d.annual_rainfall_mm), 0)
        } for d in queryset[:20]]
        
        return Response({
            'success': True,
            'count': len(data),
            'districts': data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Districts search error: {str(e)}")
        return Response({
            'success': False,
            'error': 'Failed to search districts. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_district_info(request, district_name):
    """Get specific district information."""
    try:
        district = get_object_or_404(RainfallData, district_name__iexact=district_name)
        
        return Response({
            'success': True,
            'data': {
                'district_name': district.district_name,
                'state': district.state or 'Not specified',
                'annual_rainfall_mm': round(float(district.annual_rainfall_mm), 0)
            }
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'error': f'District "{district_name}" not found'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def save_calculation_manual(request):
    """Manually save calculation for authenticated users."""
    if not request.user.is_authenticated:
        return Response({
            'success': False,
            'error': 'Please log in to save calculations'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        data = request.data
        
        calculation = CalculationLog.objects.create(
            user=request.user,
            district_name=data.get('district_name'),
            roof_area_sqm=data.get('roof_area_sqm'),
            roof_type=data.get('roof_type'),
            runoff_coefficient=data.get('runoff_coefficient'),
            annual_rainfall_mm=data.get('annual_rainfall_mm'),
            water_harvested_liters=data.get('water_harvested_liters'),
            number_of_dwellers=data.get('number_of_dwellers'),
            client_ip=get_client_ip(request)
        )
        
        return Response({
            'success': True,
            'calculation_id': calculation.id,
            'message': 'Calculation saved successfully'
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Manual save calculation error: {str(e)}")
        return Response({
            'success': False,
            'error': 'Failed to save calculation. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def rainfall_chart(request, district_name):
    """Generate monthly rainfall chart for a district."""
    try:
        gp = GraphPlot.objects.get(district_name__iexact=district_name)
        monthly_rainfall = dict(gp.get_monthly_values())

        fig, ax = plt.subplots(figsize=(10, 6))
        months = list(monthly_rainfall.keys())
        values = list(monthly_rainfall.values())
        
        bars = ax.bar(months, values, color='skyblue', edgecolor='navy', linewidth=1.2)
        
        ax.set_title(f"Monthly Rainfall - {district_name.title()}", 
                     fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel("Month", fontsize=12)
        ax.set_ylabel("Rainfall (mm)", fontsize=12)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Add value labels on bars
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + max(values)*0.01,
                    f'{value:.0f}mm', ha='center', va='bottom', fontsize=9)
        
        plt.xticks(rotation=45)
        plt.tight_layout()

        buffer = io.BytesIO()
        plt.savefig(buffer, format="png", dpi=150, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        plt.close(fig)
        buffer.seek(0)

        return HttpResponse(buffer.getvalue(), content_type="image/png")

    except GraphPlot.DoesNotExist:
        # Return placeholder image
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, f'Monthly rainfall data\nnot available for\n{district_name}', 
                ha='center', va='center', fontsize=14, 
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        
        buffer = io.BytesIO()
        plt.tight_layout()
        plt.savefig(buffer, format="png", dpi=150, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        plt.close(fig)
        buffer.seek(0)
        
        return HttpResponse(buffer.getvalue(), content_type="image/png")
    except Exception as e:
        logger.error(f"Chart generation error: {str(e)}")
        return HttpResponse("Error generating chart", status=500)

def rainfall_line_chart(request, district_name):
    """Generate monthly water harvested vs. water consumption comparison chart."""
    try:
        logger.info(f"Attempting to load chart for district: {district_name}")
        gp = GraphPlot.objects.get(district_name__iexact=district_name)
        logger.info(f"Found GraphPlot data for: {gp.district_name}")
        
        monthly_rainfall = dict(gp.get_monthly_values())
        
        # Debug: Print the keys to see the format
        logger.info(f"Monthly rainfall keys: {list(monthly_rainfall.keys())}")
        
        # Parameters from request
        roof_area_sqm = float(request.GET.get("area", 100))
        roof_type = (request.GET.get("roof_type", "RCC")).upper()
        number_of_people = int(request.GET.get("people", 1))
        
        # Runoff coefficients
        runoff_coefficients = {
            'RCC': 0.85, 'TERRACE': 0.85, 'METAL SHEET': 0.85,
            'TILE ROOF': 0.75, 'TILE': 0.75, 'ASBESTOS': 0.6,
            'ROUGH SURFACE': 0.6, 'GREEN ROOF': 0.4, 'SOIL': 0.4,
        }
        runoff_coefficient = runoff_coefficients.get(roof_type, 0.8)
        
        # Calculate harvested water
        monthly_harvest = {
            month: float(rainfall_mm) * roof_area_sqm * runoff_coefficient
            for month, rainfall_mm in monthly_rainfall.items()
        }
        
        # Consumption data - FIXED: Use UPPERCASE to match GraphPlot format
        consumption_data = {
            "JAN": 1767, "FEB": 1596, "MAR": 1897, "APR": 2070,
            "MAY": 2139, "JUN": 2070, "JUL": 1860, "AUG": 1860,
            "SEP": 1800, "OCT": 1897, "NOV": 1836, "DEC": 1767
        }
        
        # Scale by number of people
        months = list(monthly_harvest.keys())
        harvested_vals = list(monthly_harvest.values())
        consumption_vals = [consumption_data[m] * number_of_people for m in months]
        
        # Plotting
        fig, ax = plt.subplots(figsize=(12, 8))
        
        ax.plot(months, harvested_vals, marker='o', color='blue', linewidth=2, markersize=6,
                label=f"Harvested ({roof_area_sqm}m² {roof_type})")
        ax.plot(months, consumption_vals, marker='s', color='red', linestyle='--', linewidth=2, markersize=6,
                label=f"Consumption ({number_of_people} person{'s' if number_of_people > 1 else ''})")
        
        ax.set_title(f"Monthly Water Harvest vs Consumption - {district_name.title()}", 
                     fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel("Month", fontsize=12)
        ax.set_ylabel("Liters", fontsize=12)
        ax.grid(alpha=0.3, linestyle='--')
        ax.legend(fontsize=10)
        
        # Add labels
        for x, y in zip(months, harvested_vals):
            ax.text(x, y + max(harvested_vals) * 0.01, f"{y:,.0f}", ha='center', fontsize=8)
        for x, y in zip(months, consumption_vals):
            ax.text(x, y - max(consumption_vals) * 0.01, f"{y:,.0f}", ha='center', fontsize=8, color="red")
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        buffer = io.BytesIO()
        plt.savefig(buffer, format="png", dpi=150, bbox_inches='tight', facecolor='white')
        plt.close(fig)
        buffer.seek(0)
        
        return HttpResponse(buffer.getvalue(), content_type="image/png")
        
    except GraphPlot.DoesNotExist:
        logger.error(f"No GraphPlot data found for district: {district_name}")
        return HttpResponse(f"No rainfall data for {district_name}", status=404)
    except Exception as e:
        logger.error(f"Chart generation error for {district_name}: {str(e)}", exc_info=True)
        return HttpResponse(f"Error generating chart: {str(e)}", status=500)

def calculator_view(request):
    """Render calculator page with optional pre-filled district data."""
    district_name = request.GET.get("district")
    monthly_rainfall = []
    selected_district_data = None

    if district_name:
        try:
            district = RainfallData.objects.get(district_name__iexact=district_name)
            selected_district_data = {
                'name': district.district_name,
                'state': district.state,
                'annual_rainfall': district.annual_rainfall_mm
            }

            # Get monthly rainfall data if available
            graph = GraphPlot.objects.filter(district_name__iexact=district.district_name).first()
            if graph:
                monthly_rainfall = [
                    {"month": "Jan", "rainfall_mm": graph.jan},
                    {"month": "Feb", "rainfall_mm": graph.feb},
                    {"month": "Mar", "rainfall_mm": graph.mar},
                    {"month": "Apr", "rainfall_mm": graph.apr},
                    {"month": "May", "rainfall_mm": graph.may},
                    {"month": "Jun", "rainfall_mm": graph.jun},
                    {"month": "Jul", "rainfall_mm": graph.jul},
                    {"month": "Aug", "rainfall_mm": graph.aug},
                    {"month": "Sep", "rainfall_mm": graph.sep},
                    {"month": "Oct", "rainfall_mm": graph.oct},
                    {"month": "Nov", "rainfall_mm": graph.nov},
                    {"month": "Dec", "rainfall_mm": graph.dec},
                ]
        except RainfallData.DoesNotExist:
            pass

    return render(request, "calculator.html", {
        "monthly_rainfall": monthly_rainfall,
        "selected_district": district_name or "",
        "selected_district_data": selected_district_data
    })

def home_view(request):
    """Render home page."""
    return render(request, 'home.html')
