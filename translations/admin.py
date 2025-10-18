from django.contrib import admin
from .models import TranslationCache

@admin.register(TranslationCache)
class TranslationCacheAdmin(admin.ModelAdmin):
    list_display = ('original_preview', 'target_language', 'translated_preview', 'created_at')
    list_filter = ('target_language', 'created_at')
    search_fields = ('original_text', 'translated_text')
    readonly_fields = ('created_at',)
    
    def original_preview(self, obj):
        return obj.original_text[:50] + '...' if len(obj.original_text) > 50 else obj.original_text
    original_preview.short_description = 'Original Text'
    
    def translated_preview(self, obj):
        return obj.translated_text[:50] + '...' if len(obj.translated_text) > 50 else obj.translated_text
    translated_preview.short_description = 'Translated Text'
    
    # Optional: Add action to clear cache
    actions = ['clear_cache']
    
    def clear_cache(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f'Successfully deleted {count} translation(s) from cache.')
    clear_cache.short_description = 'Clear selected translations from cache'
