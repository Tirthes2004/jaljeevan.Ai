from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Q
import logging
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from math import sqrt, pi
import math
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from .models import RainfallData, CalculationLog, GraphPlot
import matplotlib.pyplot as plt
import io
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from .models import GraphPlot

logger = logging.getLogger(__name__)


@api_view(['POST'])
@login_required
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

        # Helpers
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

        # === Inputs ===
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

        # If annual_rainfall_mm not provided, try district lookup
        monthly_rainfall = None
        if annual_rainfall_mm is None:
            if not district_name:
                return Response(
                    {"error": "Provide 'district_name' or 'annual_rainfall_mm'."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                district = RainfallData.objects.get(district_name__iexact=district_name)
                annual_rainfall_mm = float(getattr(district, "annual_rainfall_mm", 0.0))
            except RainfallData.DoesNotExist:
                return Response(
                    {"error": f'District "{district_name}" not found and no "annual_rainfall_mm" given.'},
                    status=status.HTTP_404_NOT_FOUND,
                )

        # Try to fetch monthly rainfall (for plotting)
        try:
            gp = GraphPlot.objects.get(district_name__iexact=district_name)
            monthly_rainfall = dict(gp.get_monthly_values())  # {"JAN": 10.0, "FEB": 5.0, ...}
        except GraphPlot.DoesNotExist:
            monthly_rainfall = None

        # === Core calculations ===
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

        harvested_liters = roof_area_m2 * annual_rainfall_mm * runoff_coefficient
        daily_demand_l = number_of_dwellers * per_capita_lpd
        annual_demand_l = daily_demand_l * 365
        feasibility_pct = (harvested_liters / annual_demand_l) * 100 if annual_demand_l > 0 else 0.0

        # === Response ===
        response_data = {
            "district_name": district_name,
            "annual_rainfall_mm": round(annual_rainfall_mm, 3),
            "roof_area_m2": round(roof_area_m2, 3),
            "runoff_coefficient": round(runoff_coefficient, 3),
            "harvested_liters": round(harvested_liters, 2),
            "daily_demand_l": round(daily_demand_l, 2),
            "annual_demand_l": round(annual_demand_l, 2),
            "feasibility_percent": round(feasibility_pct, 2),
            "monthly_rainfall": monthly_rainfall,  # <-- for bar chart
        }

        return Response({"success": True, "data": response_data}, status=status.HTTP_200_OK)

    except Exception as exc:
        print("Error in calculate_rainwater_harvest:", exc)
        return Response({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["GET"])
@permission_classes([AllowAny])
def rainfall_chart(request, district_name):
    try:
        # Fetch monthly rainfall from DB
        gp = GraphPlot.objects.get(district_name__iexact=district_name)
        monthly_rainfall = dict(gp.get_monthly_values())  # {"JAN": 100.7, "FEB": 5, ...}

        # Plot bar chart
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(monthly_rainfall.keys(), monthly_rainfall.values(), color="skyblue")
        ax.set_title(f"Monthly Rainfall - {district_name}")
        ax.set_xlabel("Month")
        ax.set_ylabel("Rainfall (mm)")
        plt.xticks(rotation=45)

        # Save to memory as PNG
        buffer = io.BytesIO()
        plt.tight_layout()
        plt.savefig(buffer, format="png")
        plt.close(fig)
        buffer.seek(0)

        return HttpResponse(buffer.getvalue(), content_type="image/png")

    except GraphPlot.DoesNotExist:
        return HttpResponse("District not found", status=404)



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

def calculator_view(request):
    from django.shortcuts import render

    district_name = request.GET.get("district")  # e.g., /calculator/?district=Nadia
    monthly_rainfall = []

    if district_name:
        try:
            # Fetch RainfallData
            district = RainfallData.objects.get(district_name__iexact=district_name)

            # Fetch monthly rainfall from GraphPlot
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
            monthly_rainfall = []

    return render(request, "calculator.html", {
        "monthly_rainfall": monthly_rainfall,
        "selected_district": district_name or ""
    })


def home_view(request):
    from django.shortcuts import render
    return render(request, 'home.html')

