from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .services import translation_service

@csrf_exempt
def translate_batch(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            texts = data.get('texts', [])
            target_lang = data.get('target_language', 'bn')
            
            translations = translation_service.translate_batch(texts, target_lang)
            
            return JsonResponse({
                'success': True,
                'translations': translations,
                'count': len(translations)
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    return JsonResponse({'success': False, 'error': 'POST required'}, status=400)
