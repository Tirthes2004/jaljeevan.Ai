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

# def logoutUser(request):
#     logout(request)
#     messages.success(request, "Successfully Logged Out!!!")
#     return redirect('home')  # Redirect to home (calculator's demo_view)



# def logoutUser(request):
#     if request.method == "POST":
#         logout(request)
#         return JsonResponse({'status': 'success', 'message': 'Successfully Logged Out!!!'})
    
#     return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)


def logoutUser(request):
    if request.method == "POST":
        # Save officer session data before clearing user data
        officer_auth_id = request.session.get('officer_auth_id')
        officer_backend = request.session.get('officer_backend')
        officer_hash = request.session.get('officer_auth_hash')
        
        # Manually delete only user authentication keys
        # These are Django's default auth session keys
        keys_to_delete = ['_auth_user_id', '_auth_user_backend', '_auth_user_hash']
        
        for key in keys_to_delete:
            if key in request.session:
                del request.session[key]
        
        # Also delete any custom user-specific keys if you're using them
        if 'user_auth_id' in request.session:
            del request.session['user_auth_id']
        if 'user_backend' in request.session:
            del request.session['user_backend']
        
        # Restore officer session data
        if officer_auth_id:
            request.session['officer_auth_id'] = officer_auth_id
        if officer_backend:
            request.session['officer_backend'] = officer_backend
        if officer_hash:
            request.session['officer_auth_hash'] = officer_hash
        
        # Mark session as modified to ensure changes are saved
        request.session.modified = True
        
        return JsonResponse({'status': 'success', 'message': 'Successfully Logged Out!!!'})
    
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
