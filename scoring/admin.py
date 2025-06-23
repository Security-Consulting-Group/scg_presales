"""
Admin configuration for Scoring app.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Avg
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import SurveyRiskConfiguration, RiskLevelPackageRecommendation, ScoreResult


@admin.register(SurveyRiskConfiguration)
class SurveyRiskConfigurationAdmin(admin.ModelAdmin):
    list_display = ['survey', 'critical_max', 'high_max', 'moderate_max', 'good_max', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['survey__title', 'survey__code']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at', 'risk_ranges_preview']
    
    fieldsets = (
        ('Survey Information', {
            'fields': ('survey', 'is_active')
        }),
        ('Risk Level Ranges (Percentages)', {
            'fields': ('critical_max', 'high_max', 'moderate_max', 'good_max'),
            'description': 'Define the percentage ranges for each risk level. Excellent is always 81-100%.'
        }),
        ('Preview', {
            'fields': ('risk_ranges_preview',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def risk_ranges_preview(self, obj):
        """Show a visual preview of the risk ranges."""
        if not obj:
            return "Save to see preview"
            
        html = """
        <div style="margin: 10px 0;">
            <div style="display: flex; margin-bottom: 10px; font-family: monospace;">
                <div style="width: 150px; background: #dc3545; color: white; padding: 5px; text-align: center;">
                    CRITICAL<br>0% - {}%
                </div>
                <div style="width: 150px; background: #fd7e14; color: white; padding: 5px; text-align: center;">
                    HIGH<br>{}% - {}%
                </div>
                <div style="width: 150px; background: #ffc107; color: black; padding: 5px; text-align: center;">
                    MODERATE<br>{}% - {}%
                </div>
                <div style="width: 150px; background: #20c997; color: white; padding: 5px; text-align: center;">
                    GOOD<br>{}% - {}%
                </div>
                <div style="width: 150px; background: #28a745; color: white; padding: 5px; text-align: center;">
                    EXCELLENT<br>{}% - 100%
                </div>
            </div>
        </div>
        """.format(
            obj.critical_max,
            obj.critical_max + 1, obj.high_max,
            obj.high_max + 1, obj.moderate_max,
            obj.moderate_max + 1, obj.good_max,
            obj.good_max + 1
        )
        return mark_safe(html)
    risk_ranges_preview.short_description = 'Risk Ranges Preview'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('survey')


class RiskLevelPackageRecommendationInline(admin.TabularInline):
    model = RiskLevelPackageRecommendation
    extra = 0
    fields = ['risk_level', 'primary_package', 'secondary_package']
    verbose_name = "Package Recommendation"
    verbose_name_plural = "Package Recommendations"


@admin.register(RiskLevelPackageRecommendation)
class RiskLevelPackageRecommendationAdmin(admin.ModelAdmin):
    list_display = ['survey', 'risk_level_display', 'primary_package', 'secondary_package']
    list_filter = ['risk_level', 'primary_package', 'secondary_package']
    search_fields = ['survey__title', 'survey__code']
    ordering = ['survey', 'risk_level']
    
    fieldsets = (
        ('Configuration', {
            'fields': ('survey', 'risk_level')
        }),
        ('Package Recommendations', {
            'fields': ('primary_package', 'secondary_package'),
            'description': 'Select primary (mandatory) and secondary (optional) packages for this risk level.'
        }),
    )
    
    def risk_level_display(self, obj):
        colors = {
            'CRITICAL': '#dc3545',
            'HIGH': '#fd7e14',
            'MODERATE': '#ffc107',
            'GOOD': '#20c997',
            'EXCELLENT': '#28a745'
        }
        color = colors.get(obj.risk_level, '#6c757d')
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_risk_level_display()
        )
    risk_level_display.short_description = 'Risk Level'
    risk_level_display.admin_order_field = 'risk_level'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('survey')


@admin.register(ScoreResult)
class ScoreResultAdmin(admin.ModelAdmin):
    list_display = [
        'prospect_name', 'survey_title', 'score_display', 'risk_level_display', 
        'primary_package', 'calculated_at'
    ]
    list_filter = ['risk_level', 'primary_package', 'calculated_at', 'submission__survey']
    search_fields = [
        'submission__prospect__name', 'submission__prospect__email', 
        'submission__prospect__company_name', 'submission__survey__title'
    ]
    ordering = ['-calculated_at']
    readonly_fields = [
        'submission', 'total_points', 'score_percentage', 'risk_level',
        'primary_package', 'secondary_package', 'section_scores',
        'calculated_at', 'recalculated_at', 'section_scores_display'
    ]
    
    fieldsets = (
        ('Submission Info', {
            'fields': ('submission',)
        }),
        ('Score Results', {
            'fields': ('total_points', 'score_percentage', 'risk_level'),
            'description': 'Automatically calculated based on survey responses.'
        }),
        ('Recommendations', {
            'fields': ('primary_package', 'secondary_package')
        }),
        ('Section Breakdown', {
            'fields': ('section_scores_display',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('calculated_at', 'recalculated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def prospect_name(self, obj):
        return obj.submission.prospect.name
    prospect_name.short_description = 'Prospect'
    prospect_name.admin_order_field = 'submission__prospect__name'
    
    def survey_title(self, obj):
        return obj.submission.survey.title
    survey_title.short_description = 'Survey'
    survey_title.admin_order_field = 'submission__survey__title'
    
    def score_display(self, obj):
        return format_html(
            '<strong>{}%</strong><br><small>({}/{})</small>',
            obj.score_percentage,
            obj.total_points,
            obj.submission.survey.max_score
        )
    score_display.short_description = 'Score'
    score_display.admin_order_field = 'score_percentage'
    
    def risk_level_display(self, obj):
        colors = {
            'CRITICAL': '#dc3545',    # Red
            'HIGH': '#fd7e14',        # Orange  
            'MODERATE': '#ffc107',    # Yellow
            'GOOD': '#20c997',        # Teal
            'EXCELLENT': '#28a745'    # Green
        }
        color = colors.get(obj.risk_level, '#6c757d')
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_risk_level_display()
        )
    risk_level_display.short_description = 'Risk Level'
    risk_level_display.admin_order_field = 'risk_level'
    
    def section_scores_display(self, obj):
        if not obj.section_scores:
            return "No section data available"
        
        html = "<table style='width: 100%; border-collapse: collapse;'>"
        html += "<tr style='background: #f8f9fa;'><th style='padding: 8px; border: 1px solid #dee2e6;'>Section</th><th style='padding: 8px; border: 1px solid #dee2e6;'>Points</th><th style='padding: 8px; border: 1px solid #dee2e6;'>Percentage</th></tr>"
        
        for section_key, data in obj.section_scores.items():
            html += f"<tr><td style='padding: 8px; border: 1px solid #dee2e6;'>{data.get('title', section_key)}</td>"
            html += f"<td style='padding: 8px; border: 1px solid #dee2e6; text-align: center;'>{data.get('points', 0)}/{data.get('max_points', 0)}</td>"
            html += f"<td style='padding: 8px; border: 1px solid #dee2e6; text-align: center;'>{data.get('percentage', 0)}%</td></tr>"
        
        html += "</table>"
        return format_html(html)
    section_scores_display.short_description = 'Section Breakdown'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'submission__prospect', 'submission__survey'
        )
    
    def has_add_permission(self, request):
        return False  # ScoreResults are calculated automatically
    
    def has_delete_permission(self, request, obj=None):
        return True  # Allow deletion for data cleanup
    
    actions = ['recalculate_scores']
    
    def recalculate_scores(self, request, queryset):
        """Action to recalculate selected score results."""
        updated_count = 0
        for score_result in queryset:
            ScoreResult.calculate_for_submission(score_result.submission)
            updated_count += 1
        
        self.message_user(
            request, 
            f'{updated_count} score result(s) have been recalculated.'
        )
    recalculate_scores.short_description = 'Recalculate selected scores'


# Customize admin site headers
admin.site.site_header = 'SCG Presales Administration'
admin.site.site_title = 'SCG Admin'
admin.site.index_title = 'Security Consulting Group - Presales System'