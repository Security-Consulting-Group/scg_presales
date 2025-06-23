"""
Admin configuration for Surveys app.
"""
from django.contrib import admin
from .models import (
    Survey, SurveySection, Question, QuestionOption,
    SurveySubmission, Response
)

# surveys/admin.py - Actualizar SurveyAdmin

class SurveyAdmin(admin.ModelAdmin):
    list_display = ['title', 'code', 'version', 'is_active', 'is_featured', 'created_at', 'created_by_name', 'max_score']
    list_filter = ['is_active', 'is_featured', 'created_at', 'version']
    search_fields = ['title', 'code', 'description']
    ordering = ['-created_at']
    readonly_fields = ['code', 'created_at', 'updated_at']
    
    # Permitir marcar/desmarcar featured desde la lista
    list_editable = ['is_featured']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'version', 'code')
        }),
        ('Configuration', {
            'fields': ('is_active', 'is_featured', 'max_score', 'created_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        # Si es un survey nuevo, ocultar campos que se generan automáticamente
        if obj is None:
            return ['code', 'created_by', 'created_at', 'updated_at']
        # Si ya existe, mostrar todos como solo lectura excepto los editables
        return ['code', 'created_by', 'created_at', 'updated_at']
    
    def get_fieldsets(self, request, obj=None):
        # Si es un survey nuevo, ocultar el campo code y created_by del formulario
        if obj is None:
            return (
                ('Basic Information', {
                    'fields': ('title', 'description', 'version')
                }),
                ('Configuration', {
                    'fields': ('is_active', 'is_featured', 'max_score')
                }),
            )
        # Si ya existe, mostrar todos los campos
        return super().get_fieldsets(request, obj)
    
    def save_model(self, request, obj, form, change):
        # Si es un nuevo survey, establecer created_by automáticamente
        if not change:  # change=False significa que es nuevo
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    actions = ['mark_as_featured', 'unmark_as_featured']
    
    def mark_as_featured(self, request, queryset):
        """Mark selected survey as featured (only one at a time)."""
        if queryset.count() > 1:
            self.message_user(request, 'Solo se puede marcar un survey como featured a la vez.', level='warning')
            return
        
        survey = queryset.first()
        # El método save() del modelo se encarga de desmarcar los demás
        survey.is_featured = True
        survey.save()
        
        self.message_user(request, f'Survey "{survey.title}" marcado como featured.')
    mark_as_featured.short_description = 'Mark as featured (will show on landing page)'
    
    def unmark_as_featured(self, request, queryset):
        """Remove featured status from selected surveys."""
        count = queryset.update(is_featured=False)
        self.message_user(request, f'{count} surveys ya no están marcados como featured.')
    unmark_as_featured.short_description = 'Remove featured status'
    
    def created_by_name(self, obj):
        """Display the name of the user who created the survey."""
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}".strip() or obj.created_by.email
        return "Unknown"
    created_by_name.short_description = 'Created By'


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
    fields = ['order', 'option_text', 'points', 'is_exclusive', 'is_active']
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