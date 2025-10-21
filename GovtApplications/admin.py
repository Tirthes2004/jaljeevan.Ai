from django.contrib import admin
from .models import *

# Register your models here.


@admin.register(SubsidyApplication)
class SubsidyApplicationAdmin(admin.ModelAdmin):
    list_display = ('application_id', 'full_name', 'district', 'status', 'created_at')
    list_filter = ('status', 'district', 'created_at')
    search_fields = ('application_id', 'full_name', 'mobile', 'email')
    readonly_fields = ('application_id', 'created_at', 'updated_at')
    
    actions = ['approve_applications', 'reject_applications']
    
    def approve_applications(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='APPROVED', decided_by=request.user, decided_at=timezone.now())
        self.message_user(request, f'{queryset.count()} applications approved')
    approve_applications.short_description = 'Approve selected'
    
    def reject_applications(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='REJECTED', decided_by=request.user, decided_at=timezone.now())
        self.message_user(request, f'{queryset.count()} applications rejected')
    reject_applications.short_description = 'Reject selected'


@admin.register(Officer)
class OfficerAdmin(admin.ModelAdmin):
    list_display = ('officer_name', 'officer_email', 'assigned_district', 'govt_id')
    search_fields = ('officer_name', 'officer_email', 'govt_id')
    list_filter = ('assigned_district',)
