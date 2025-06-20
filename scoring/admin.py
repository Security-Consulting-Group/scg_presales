"""
Admin configuration for Scoring app.
"""
from django.contrib import admin
from .models import ScoreResult


@admin.register(ScoreResult)
class ScoreResultAdmin(admin.ModelAdmin):
    list_display = ['prospect_name', 'prospect_email', 'total_score', 'risk_level', 'recommended_package', 'calculated_at']
    list_filter = ['risk_level', 'recommended_package', 'calculated_at']
    search_fields = ['prospect_name', 'prospect_email']
    ordering = ['-calculated_at']
    readonly_fields = ['calculated_at']
    
    fieldsets = (
        ('Prospect Information', {
            'fields': ('prospect_name', 'prospect_email')
        }),
        ('Overall Scoring', {
            'fields': ('total_score', 'risk_level', 'recommended_package')
        }),
        ('Section Scores', {
            'fields': ('context_score', 'access_management_score', 'infrastructure_score', 'risk_management_score')
        }),
        ('Timestamps', {
            'fields': ('calculated_at',),
            'classes': ('collapse',)
        }),
    )