from django.http import JsonResponse
from .models import PremiumFeature


def subscribe_premium(request):
    # Get existing or create new PremiumFeature for user
    user_premium, created = PremiumFeature.objects.get_or_create(
        user=request.user,
        defaults={'is_premium': True}
    )
    
    # If it already existed, update is_premium to True
    if not created:
        user_premium.is_premium = True
        user_premium.save()
    
    return JsonResponse({
        'is_premium': user_premium.is_premium,
        'created': created
    })
