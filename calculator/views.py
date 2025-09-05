from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import RainfallData, CalculationLog
import logging
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User



logger = logging.getLogger(__name__)

def demo(request):
    return render(request,'demo.html')


@api_view(['POST'])
def calculate_rainwater_harvest(request):
    """
    Calculate rainwater harvesting potential and save to database.
    """
    # if not request.user.is_authenticated:
    #     return redirect('loginUser') 

    try:
        # ✅ Use request.data (DRF parsed data)
        data = request.data
        district_name = data.get('district_name', '').strip()
        length = float(data.get('length', 0))
        width = float(data.get('width', 0))
        
        print(f"🔍 Received: {district_name}, {length}x{width}")
        
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
        
        # ⭐ NEW: Save calculation to database
        try:
            calculation_log = CalculationLog.objects.create(
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
        except Exception as e:
            print(f"⚠️ Failed to save calculation log: {str(e)}")
            # Don't fail the response if logging fails
        
        # Response data
        response_data = {
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
        
    except ValueError as e:
        return Response({
            'error': f'Invalid number format: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(f"❌ Calculate error: {e}")
        logger.error(f"Calculation error: {str(e)}")
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
                Q(district_name__icontains=search) | 
                Q(state__icontains=search)
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
def demo_view(request):
    from django.shortcuts import render
    return render(request, 'demo.html')


# Register user
def registerUser(request):  
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if not username or not email or not password or not confirm_password:
            messages.error(request,"All fields required!")
            return redirect('registerUser')
        
        elif(password == confirm_password):
            if(User.objects.filter(email=email).exists()):
                messages.info(request,"Email already exist, Try with another")
                return redirect('registerUser')
            elif(User.objects.filter(username=username).exists()):
                messages.info(request,'Username already exist, Try with another')
                return redirect('registerUser')
            else:
                user = User.objects.create_user(username=username,email=email,password=password)
                user.save()
                login(request,user)
                messages.info(request,'Account Created')
                return redirect('loginUser')
        else:
            messages.info(request,"Password Mismatched")
            return redirect('registerUser')

    else:
        return render(request,'registerUser.html')

#  Login
def loginUser(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username,password=password)
        if user is not None:
            messages.success(request,"Succesfully Logged In")
            login(request,user)
            return redirect('demo')
        else:
            messages.error(request,"Credential Mismatched!!!")
            return redirect('loginUser')
        
    return render(request,'loginUser.html')

#  LogOut
def logoutUser(request):
    logout(request)
    messages.error(request,"Successfully Logged Out!!!")
    return redirect('demo')



