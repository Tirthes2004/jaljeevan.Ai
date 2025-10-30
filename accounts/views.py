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

@login_required
def profileView(request):
    """Return user profile data as JSON"""
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'message': 'User not authenticated'
        }, status=401)
    
    # Format the date user joined
    date_joined = request.user.date_joined.strftime('%B %d, %Y') if hasattr(request.user, 'date_joined') else 'N/A'
    
    return JsonResponse({
        'success': True,
        'username': request.user.username,
        'email': request.user.email,
        'date_joined': date_joined,
        'first_name': request.user.first_name if hasattr(request.user, 'first_name') else '',
        'last_name': request.user.last_name if hasattr(request.user, 'last_name') else '',
    })
