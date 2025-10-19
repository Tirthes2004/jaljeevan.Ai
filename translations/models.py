from django.db import models

# Create your models here.

class TranslationCache(models.Model):
    original_text = models.TextField()
    target_language = models.CharField(max_length=10)
    translated_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('original_text', 'target_language')
    
    def __str__(self):
        return f"{self.original_text[:30]} -> {self.target_language}"
