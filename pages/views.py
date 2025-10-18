from django.shortcuts import render

# Create your views here.


def home_view(request):
    """Home/Landing page"""
    return render(request, 'home.html')

def about_view(request):
    """About/Features page"""
    return render(request, 'about.html')

def contact_view(request):
    """Contact page"""
    return render(request, 'contact.html')

def leaderboard_view(request):
    """Contact page"""
    return render(request, 'leaderboard.html')

def vendor_view(request):
    """Vendor page"""
    return render(request, 'vendor.html')

# def leaderboard_view(request):
#     """LeaderBoard page"""
#     return render(request, 'pages/leaderboard.html')
