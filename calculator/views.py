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
    """Enhanced calculation API with duplicate district handling."""
    try:
        data = request.data or {}

        # Helper functions
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

        # ✅ FIX: Handle duplicate districts properly
        if annual_rainfall_mm <= 0:
            # Use filter instead of get to handle duplicates
            districts = RainfallData.objects.filter(district_name__iexact=district_name)
            
            if not districts.exists():
                return Response({
                    'success': False,
                    'error': f'District "{district_name}" not found in our database. Please search and select from available districts.'
                }, status=status.HTTP_404_NOT_FOUND)
            
            elif districts.count() > 1:
                # Multiple districts found - provide helpful error message
                district_list = [f"{d.district_name} ({d.state})" for d in districts[:3]]
                district_names = ", ".join(district_list)
                return Response({
                    'success': False,
                    'error': f'Multiple districts named "{district_name}" found: {district_names}. Please be more specific or include the state name.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            else:
                # Exactly one district found - use it
                district = districts.first()
                annual_rainfall_mm = float(district.annual_rainfall_mm)
                state = district.state or 'Not specified'
        else:
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
        
        daily_requirement_liters = number_of_dwellers * 135
        annual_requirement_liters = daily_requirement_liters * 365
        
        efficiency_percent = (water_harvested_liters / annual_requirement_liters) * 100 if annual_requirement_liters > 0 else 0

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
            'user': request.user.username if request.user.is_authenticated else None,  # ✅ FIX: Include username
            'is_saved': False
        }

    

        return Response({
            'success': True,
            'data': response_data
        }, status=status.HTTP_200_OK)

    except Exception as exc:
        logger.error(f"Error in calculate_rainwater_harvest: {str(exc)}")
        return Response({
            'success': False,
            'error': 'Internal server error. Please try again later.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def generate_recommendation(efficiency_percent, harvested_liters, dwellers, roof_area, rainfall):
    """Generate expert recommendation based on calculation results."""
    harvested_liters_int = int(harvested_liters)
    
    if efficiency_percent >= 100:
        return f"🌟 Excellent! Your {roof_area}m² roof can harvest {harvested_liters_int:,}L annually, fully meeting your {dwellers}-person household's water needs. This system will provide complete water independence and significant cost savings. Consider implementing a comprehensive rainwater harvesting system with proper filtration for potable use."
    
    elif efficiency_percent >= 70:
        return f"💪 Very Good! Your roof can harvest {harvested_liters_int:,}L annually, covering {efficiency_percent:.0f}% of your household water needs. This system would significantly reduce your water bills by ₹15,000-25,000 annually and provide excellent backup during water shortages. Highly recommended investment with 3-5 year payback period."
    
    elif efficiency_percent >= 40:
        return f"👍 Good Potential! Your roof can harvest {harvested_liters_int:,}L annually, covering {efficiency_percent:.0f}% of your water needs. Perfect for non-potable uses like gardening, cleaning, and toilet flushing. Consider combining with water-efficient fixtures and conservation practices for maximum benefit."
    
    elif efficiency_percent >= 20:
        return f"⚡ Moderate Potential. Your roof can harvest {harvested_liters_int:,}L annually, covering {efficiency_percent:.0f}% of your needs. Best utilized for specific purposes like gardening, car washing, and emergency backup. Consider increasing catchment area or supplementing with other water conservation methods."
    
    else:
        return f"💡 Limited harvest potential of {harvested_liters_int:,}L annually due to {'low rainfall' if rainfall < 600 else 'small roof area'}. Consider: 1) Increasing roof area with additional structures, 2) Improving runoff coefficient with better roofing materials, 3) Using harvested water for targeted purposes like gardening, or 4) Implementing other water conservation strategies."

@api_view(['GET'])
@permission_classes([AllowAny])
def list_districts(request):
    """Enhanced district search API with intelligent filtering."""
    try:
        search = request.query_params.get('search', '').strip()
        
        queryset = RainfallData.objects.all()
        
        if search:
            # Smart filtering - prioritize exact matches, then starts-with, then contains
            queryset = queryset.filter(
                Q(district_name__icontains=search) | 
                Q(state__icontains=search)
            ).distinct()
        
        # Limit results and order by relevance
        if search:
            # Prioritize exact matches and starts-with matches
            exact_matches = queryset.filter(district_name__iexact=search)[:5]
            starts_with = queryset.filter(district_name__istartswith=search).exclude(
                id__in=[d.id for d in exact_matches]
            )[:10]
            contains = queryset.filter(district_name__icontains=search).exclude(
                id__in=[d.id for d in list(exact_matches) + list(starts_with)]
            )[:15]
            
            final_queryset = list(exact_matches) + list(starts_with) + list(contains)
        else:
            final_queryset = queryset.order_by('district_name')[:20]
        
        districts_data = []
        for district in final_queryset:
            districts_data.append({
                'district_name': district.district_name,
                'state': district.state or 'Not specified',
                'annual_rainfall_mm': round(float(district.annual_rainfall_mm), 0)
            })
        
        logger.info(f"Districts search '{search}': {len(districts_data)} results")
        
        return Response({
            'success': True,
            'count': len(districts_data),
            'districts': districts_data
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

import matplotlib
matplotlib.use('Agg')  # ✅ CRITICAL: Set non-GUI backend BEFORE importing pyplot
import matplotlib.pyplot as plt
import io
import logging

@api_view(['GET'])
@permission_classes([AllowAny])
def rainfall_chart(request, district_name):
    """Generate monthly rainfall chart for a district."""
    try:
        gp = GraphPlot.objects.get(district_name__iexact=district_name)
        monthly_rainfall = dict(gp.get_monthly_values())

        # ✅ Now matplotlib will use Agg backend (no GUI)
        fig, ax = plt.subplots(figsize=(10, 6))
        months = list(monthly_rainfall.keys())
        values = list(monthly_rainfall.values())
        
        bars = ax.bar(months, values, color='skyblue', edgecolor='navy', linewidth=1.2)
        
        # Enhance chart appearance
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

        # ✅ Use BytesIO to generate PNG in memory
        buffer = io.BytesIO()
        plt.savefig(buffer, format="png", dpi=150, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        plt.close(fig)  # ✅ IMPORTANT: Close figure to free memory
        buffer.seek(0)

        return HttpResponse(buffer.getvalue(), content_type="image/png")

    except GraphPlot.DoesNotExist:
        # Return placeholder image for districts without chart data
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
        plt.close(fig)  # ✅ Always close figures
        buffer.seek(0)
        
        return HttpResponse(buffer.getvalue(), content_type="image/png")
    except Exception as e:
        logger.error(f"Chart generation error: {str(e)}")
        return HttpResponse("Error generating chart", status=500)

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



@api_view(['POST'])
def save_calculation(request):
    """Save calculation result to database."""
    if not request.user.is_authenticated:
        return Response({
            'success': False,
            'error': 'Please log in to save calculations'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        data = request.data
        
        # Check if this calculation already exists for this user
        existing = CalculationLog.objects.filter(
            user=request.user,
            district_name=data.get('district_name'),
            roof_area_sqm=data.get('roof_area_sqm'),
            roof_type=data.get('roof_type'),
            number_of_dwellers=data.get('number_of_dwellers'),
            created_at__date=timezone.now().date()  # Same day
        ).first()
        
        if existing:
            # ✅ Update existing calculation instead of creating duplicate
            existing.annual_rainfall_mm = data.get('annual_rainfall_mm')
            existing.water_harvested_liters = data.get('water_harvested_liters')
            existing.efficiency_percent = data.get('efficiency_percent')
            existing.updated_at = timezone.now()
            existing.save()
            
            return Response({
                'success': True,
                'calculation_id': existing.id,
                'message': 'Calculation updated successfully',
                'is_saved': True
            }, status=status.HTTP_200_OK)
        else:
            # ✅ Create new calculation
            calculation = CalculationLog.objects.create(
                user=request.user,
                district_name=data.get('district_name'),
                state=data.get('state'),
                roof_area_sqm=data.get('roof_area_sqm'),
                roof_type=data.get('roof_type'),
                runoff_coefficient=data.get('runoff_coefficient'),
                annual_rainfall_mm=data.get('annual_rainfall_mm'),
                number_of_dwellers=data.get('number_of_dwellers'),
                water_harvested_liters=data.get('water_harvested_liters'),
                efficiency_percent=data.get('efficiency_percent'),
                client_ip=get_client_ip(request)
            )
            
            return Response({
                'success': True,
                'calculation_id': calculation.id,
                'message': 'Calculation saved successfully',
                'is_saved': True
            }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Save calculation error: {str(e)}")
        return Response({
            'success': False,
            'error': 'Failed to save calculation. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def home_view(request):
    """Render home page."""
    return render(request, 'home.html')
