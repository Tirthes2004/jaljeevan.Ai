from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.shortcuts import redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.models import User


# Modified Register user - API only
@require_http_methods(["POST"])
def registerUser(request):  
    username = request.POST.get('username')
    email = request.POST.get('email')
    password = request.POST.get('password')
    confirm_password = request.POST.get('confirm_password')

    # Validation
    if not username or not email or not password or not confirm_password:
        return JsonResponse({
            'success': False,
            'message': 'All fields required!'
        })
    
    if password != confirm_password:
        return JsonResponse({
            'success': False,
            'message': 'Password Mismatched'
        })
        
    if User.objects.filter(email=email).exists():
        return JsonResponse({
            'success': False,
            'message': 'Email already exist, Try with another'
        })
        
    if User.objects.filter(username=username).exists():
        return JsonResponse({
            'success': False,
            'message': 'Username already exist, Try with another'
        })
    
    # Create user
    try:
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        login(request, user)
        return JsonResponse({
            'success': True,
            'message': 'Account Created Successfully',
            'redirect_url': '/calculator/'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Error creating account. Please try again.'
        })

# Your loginUser view - keep as is
@require_http_methods(["POST"])
def loginUser(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    
    user = authenticate(username=username, password=password)
    
    if user is not None:
        login(request, user)
        return JsonResponse({
            'success': True,
            'message': 'Successfully Logged In',
            'redirect_url': '/'  # Redirect to root (calculator's demo_view)
        })
    else:
        return JsonResponse({
            'success': False,
            'message': 'Credential Mismatched!!!'
        })


def logoutUser(request):
    if request.method == "POST":
        logout(request)
        return JsonResponse({'status': 'success', 'message': 'Successfully Logged Out!!!'})
    
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)


from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

# @login_required
# def profileView(request):
#     """Return user profile data as JSON"""
#     if not request.user.is_authenticated:
#         return JsonResponse({
#             'success': False,
#             'message': 'User not authenticated'
#         }, status=401)
    
#     # Format the date user joined
#     date_joined = request.user.date_joined.strftime('%B %d, %Y') if hasattr(request.user, 'date_joined') else 'N/A'
    
#     return JsonResponse({
#         'success': True,
#         'username': request.user.username,
#         'email': request.user.email,
#         'date_joined': date_joined,
#         'first_name': request.user.first_name if hasattr(request.user, 'first_name') else '',
#         'last_name': request.user.last_name if hasattr(request.user, 'last_name') else '',
#     })


from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from .models import UserProfile


@login_required
@require_http_methods(["GET"])
def profileView(request):
    """Get user profile data"""
    user = request.user
    
    # Get or create profile
    try:
        profile = user.profile
        profile_photo_url = profile.profile_photo.url if profile.profile_photo else None
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=user)
        profile_photo_url = None
    
    return JsonResponse({
        'success': True,
        'username': user.username,
        'email': user.email,
        'date_joined': user.date_joined.strftime('%B %d, %Y'),
        'profile_photo': profile_photo_url
    })


@login_required
@require_http_methods(["POST"])
def upload_profile_photo(request):
    """Upload and save profile photo"""
    try:
        user = request.user
        profile_photo = request.FILES.get('profile_photo')
        
        if not profile_photo:
            return JsonResponse({
                'success': False,
                'error': 'No photo provided'
            })
        
        # Validate file size (max 5MB)
        if profile_photo.size > 5 * 1024 * 1024:
            return JsonResponse({
                'success': False,
                'error': 'File size must be less than 5MB'
            })
        
        # Validate file type
        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if profile_photo.content_type not in allowed_types:
            return JsonResponse({
                'success': False,
                'error': 'Only JPEG, PNG, GIF, and WebP images are allowed'
            })
        
        # Get or create profile
        profile, created = UserProfile.objects.get_or_create(user=user)
        
        # Delete old photo if exists
        if profile.profile_photo:
            profile.profile_photo.delete(save=False)
        
        # Save new photo
        profile.profile_photo = profile_photo
        profile.save()
        
        return JsonResponse({
            'success': True,
            'photo_url': profile.profile_photo.url,
            'message': 'Profile photo updated successfully!'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
