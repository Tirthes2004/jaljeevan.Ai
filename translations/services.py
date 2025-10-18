from googletrans import Translator
from django.conf import settings
from .models import TranslationCache
import logging

logger = logging.getLogger(__name__)

class TranslationService:
    def __init__(self):
        self.translator = Translator()
    
    def translate(self, text, target_lang='bn'):
        if not text or not text.strip():
            return text
        
        # Check cache first
        try:
            cached = TranslationCache.objects.get(
                original_text=text,
                target_language=target_lang
            )
            logger.info(f"✅ Cache hit: {text[:30]}")
            return cached.translated_text
        except TranslationCache.DoesNotExist:
            pass
        
        # Translate using googletrans
        try:
            result = self.translator.translate(text, dest=target_lang, src='en')
            translated = result.text
            
            # Save to cache
            TranslationCache.objects.create(
                original_text=text,
                target_language=target_lang,
                translated_text=translated
            )
            logger.info(f"🌐 Translated: {text[:30]} -> {translated[:30]}")
            return translated
            
        except Exception as e:
            logger.error(f"❌ Translation error: {str(e)}")
            return text
    
    def translate_batch(self, texts, target_lang='bn'):
        return [self.translate(text, target_lang) for text in texts]

translation_service = TranslationService()
