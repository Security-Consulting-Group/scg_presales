"""
Admin configuration for Prospects app.
"""
from django.contrib import admin
from .models import Prospect, ProspectInquiry, InteractionNote


@admin.register(Prospect)
class ProspectAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'company_name', 'status', 'created_at', 'last_contact_at']
    list_filter = ['status', 'company_industry', 'company_size', 'initial_source', 'created_at']
    search_fields = ['name', 'email', 'phone', 'company_name']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'email', 'phone', 'status', 'initial_source')
        }),
        ('Company Information', {
            'fields': ('company_name', 'company_industry', 'company_size')
        }),
        ('Contact History', {
            'fields': ('last_contact_at',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ProspectInquiry)
class ProspectInquiryAdmin(admin.ModelAdmin):
    list_display = ['prospect', 'source', 'is_responded', 'created_at', 'responded_by']
    list_filter = ['source', 'is_responded', 'created_at']
    search_fields = ['prospect__name', 'prospect__email', 'message']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Inquiry Details', {
            'fields': ('prospect', 'message', 'source')
        }),
        ('Response Tracking', {
            'fields': ('is_responded', 'responded_at', 'responded_by')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(InteractionNote)
class InteractionNoteAdmin(admin.ModelAdmin):
    list_display = ['prospect', 'title', 'note_type', 'created_by', 'follow_up_date', 'created_at']
    list_filter = ['note_type', 'created_by', 'follow_up_date', 'created_at']
    search_fields = ['prospect__name', 'prospect__email', 'title', 'content']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Interaction Details', {
            'fields': ('prospect', 'note_type', 'title', 'created_by')
        }),
        ('Content', {
            'fields': ('content', 'next_steps', 'follow_up_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )