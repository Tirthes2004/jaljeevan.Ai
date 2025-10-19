from deep_translator import GoogleTranslator
from .models import TranslationCache
import logging

logger = logging.getLogger(__name__)

class TranslationService:
    def translate(self, text, target_lang='bn'):
        if not text or not text.strip():
            return text
        
        try:
            cached = TranslationCache.objects.get(
                original_text=text, target_language=target_lang
            )
            return cached.translated_text
        except TranslationCache.DoesNotExist:
            pass
        
        try:
            translated = GoogleTranslator(source='en', target=target_lang).translate(text)
            
            TranslationCache.objects.create(
                original_text=text,
                target_language=target_lang,
                translated_text=translated
            )
            return translated
        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            return text
    
    def translate_batch(self, texts, target_lang='bn'):
        return [self.translate(text, target_lang) for text in texts]

translation_service = TranslationService()