"""
Admin configuration for Surveys app.
"""
from django.contrib import admin
from .models import (
    Survey, SurveySection, Question, QuestionOption,
    SurveySubmission, Response
)


class SurveyAdmin(admin.ModelAdmin):
    list_display = ['title', 'code', 'version', 'is_active', 'created_at', 'max_score']
    list_filter = ['is_active', 'created_at', 'version']
    search_fields = ['title', 'code', 'description']
    ordering = ['-created_at']
    readonly_fields = ['code', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'version', 'code')
        }),
        ('Configuration', {
            'fields': ('is_active', 'max_score', 'created_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        # Si es un survey nuevo, permitir editar created_by
        if obj is None:
            return ['code', 'created_at', 'updated_at']
        return ['code', 'created_at', 'updated_at', 'created_by']


class SurveySectionAdmin(admin.ModelAdmin):
    list_display = ['survey', 'order', 'title', 'max_points']
    list_filter = ['survey']
    search_fields = ['title', 'description']
    ordering = ['survey', 'order']
    
    fieldsets = (
        ('Section Information', {
            'fields': ('survey', 'title', 'description', 'order')
        }),
        ('Scoring', {
            'fields': ('max_points',)
        }),
    )


class QuestionOptionInline(admin.TabularInline):
    model = QuestionOption
    extra = 1
    fields = ['order', 'option_text', 'points', 'is_active']
    ordering = ['order']


class QuestionAdmin(admin.ModelAdmin):
    list_display = ['survey', 'section_order', 'order', 'question_text_short', 'question_type', 'is_required', 'max_points']
    list_filter = ['survey', 'section', 'question_type', 'is_required', 'is_active']
    search_fields = ['question_text']
    ordering = ['survey', 'section__order', 'order']
    inlines = [QuestionOptionInline]
    
    fieldsets = (
        ('Question Details', {
            'fields': ('survey', 'section', 'question_text', 'question_type')
        }),
        ('Configuration', {
            'fields': ('order', 'is_required', 'is_active', 'max_points')
        }),
        ('Help', {
            'fields': ('help_text',),
            'classes': ('collapse',)
        }),
    )
    
    def question_text_short(self, obj):
        return f"{obj.question_text[:50]}..." if len(obj.question_text) > 50 else obj.question_text
    question_text_short.short_description = 'Question Text'
    
    def section_order(self, obj):
        return f"Section {obj.section.order}"
    section_order.short_description = 'Section'


class ResponseInline(admin.TabularInline):
    model = Response
    extra = 0
    readonly_fields = ['question', 'selected_option', 'text_response', 'points_earned']
    fields = ['question', 'selected_option', 'text_response', 'points_earned']
    
    def has_add_permission(self, request, obj=None):
        return False


class SurveySubmissionAdmin(admin.ModelAdmin):
    list_display = ['prospect', 'survey', 'status', 'started_at', 'completed_at', 'total_score']
    list_filter = ['status', 'survey', 'started_at', 'completed_at']
    search_fields = ['prospect__name', 'prospect__email', 'prospect__company_name']
    ordering = ['-started_at']
    readonly_fields = ['started_at', 'ip_address']
    inlines = [ResponseInline]
    
    fieldsets = (
        ('Submission Info', {
            'fields': ('prospect', 'survey', 'status')
        }),
        ('Timestamps', {
            'fields': ('started_at', 'completed_at')
        }),
        ('Management', {
            'fields': ('admin_notes', 'ip_address'),
            'classes': ('collapse',)
        }),
    )
    
    def total_score(self, obj):
        return obj.get_total_score()
    total_score.short_description = 'Total Score'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('prospect', 'survey')
    
    actions = ['disable_submissions', 'enable_submissions']
    
    def disable_submissions(self, request, queryset):
        count = queryset.update(status='DISABLED')
        self.message_user(request, f'{count} submissions disabled.')
    disable_submissions.short_description = 'Disable selected submissions'
    
    def enable_submissions(self, request, queryset):
        count = queryset.update(status='ACTIVE')
        self.message_user(request, f'{count} submissions enabled.')
    enable_submissions.short_description = 'Enable selected submissions'


class ResponseAdmin(admin.ModelAdmin):
    list_display = ['submission_prospect', 'submission_survey', 'question_text_short', 'selected_option', 'points_earned']
    list_filter = ['submission__survey', 'question__question_type', 'submission__status']
    search_fields = ['submission__prospect__name', 'question__question_text']
    ordering = ['-submission__started_at', 'question__section__order', 'question__order']
    readonly_fields = ['submission', 'question', 'selected_option', 'text_response', 'points_earned', 'created_at']
    
    def submission_prospect(self, obj):
        return obj.submission.prospect.name
    submission_prospect.short_description = 'Prospect'
    
    def submission_survey(self, obj):
        return obj.submission.survey.title
    submission_survey.short_description = 'Survey'
    
    def question_text_short(self, obj):
        return f"{obj.question.question_text[:40]}..." if len(obj.question.question_text) > 40 else obj.question.question_text
    question_text_short.short_description = 'Question'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'submission__prospect', 'submission__survey', 'question', 'selected_option'
        )
    
    def has_add_permission(self, request):
        return False


# Register all models
admin.site.register(Survey, SurveyAdmin)
admin.site.register(SurveySection, SurveySectionAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(SurveySubmission, SurveySubmissionAdmin)
admin.site.register(Response, ResponseAdmin)

# Customize admin site headers
admin.site.site_header = 'SCG Presales Administration'
admin.site.site_title = 'SCG Admin'
admin.site.index_title = 'Security Consulting Group - Presales System'