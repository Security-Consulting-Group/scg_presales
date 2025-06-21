"""
Surveys models for SCG Presales system.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import datetime

class Survey(models.Model):
    """
    Main survey definition.
    
    Allows for multiple surveys over time (current + future versions).
    """
    # Código único para URLs (YYYYMMDDHHMMSS)
    code = models.CharField(
        max_length=14,
        unique=True,
        help_text="Unique code for survey URL (YYYYMMDDHHMMSS format)"
    )
    
    title = models.CharField(
        max_length=200,
        help_text="Survey title (e.g., 'Diagnóstico Ejecutivo de Ciberseguridad v1.0')"
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Description of what this survey measures"
    )
    
    version = models.CharField(
        max_length=20,
        default="1.0",
        help_text="Survey version (e.g., '1.0', '2.0')"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Is this survey currently active for new submissions?"
    )
    
    # NUEVO CAMPO:
    is_featured = models.BooleanField(
        default=False,
        help_text="Show this survey on the landing page (only one can be featured)"
    )
    
    max_score = models.PositiveIntegerField(
        default=100,
        help_text="Maximum possible score for this survey"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # CAMPO ACTUALIZADO:
    created_by = models.ForeignKey(
        'core.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="User who created this survey"
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Survey'
        verbose_name_plural = 'Surveys'
        unique_together = ['title', 'version']
    
    def __str__(self):
        return f"{self.title} v{self.version} ({self.code})"
    
    def save(self, *args, **kwargs):
        # Generar código automáticamente si es un nuevo survey
        if not self.code:
            self.code = self.generate_code()
            
            # Asegurar que el código sea único (por si hay colisión de tiempo)
            while Survey.objects.filter(code=self.code).exists():
                import time
                time.sleep(1)  # Esperar 1 segundo
                self.code = self.generate_code()
        
        # Si se marca como featured, desmarcar todos los demás
        if self.is_featured:
            Survey.objects.filter(is_featured=True).exclude(pk=self.pk).update(is_featured=False)
            
        super().save(*args, **kwargs)
    
    @classmethod
    def generate_code(cls):
        """Generate a new unique code in YYYYMMDDHHMMSS format."""
        import datetime
        now = datetime.datetime.now()
        return now.strftime("%Y%m%d%H%M%S")
    
    @classmethod
    def get_featured_survey(cls):
        """Get the survey that should be displayed on landing page."""
        # Primero buscar el marcado como featured
        featured = cls.objects.filter(is_active=True, is_featured=True).first()
        if featured:
            return featured
        
        # Si no hay ninguno featured, usar el más reciente activo
        return cls.objects.filter(is_active=True).order_by('-created_at').first()
    
    def get_active_questions(self):
        """Get all active questions for this survey, ordered by section and order."""
        return self.questions.filter(is_active=True).order_by('section__order', 'order')
    
    def get_absolute_url(self):
        """Get the URL for this survey."""
        from django.urls import reverse
        return reverse('surveys:survey_detail', kwargs={'code': self.code})

class SurveySection(models.Model):
    """
    Sections within a survey (A, B, C, D, E from the questionnaire).
    """
    survey = models.ForeignKey(
        Survey,
        on_delete=models.CASCADE,
        related_name='sections'
    )
    
    title = models.CharField(
        max_length=200,
        help_text="Section title (e.g., 'Contexto de Negocio')"
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Section description"
    )
    
    order = models.PositiveIntegerField(
        help_text="Order of this section in the survey"
    )
    
    # Scoring weight for this section
    max_points = models.PositiveIntegerField(
        help_text="Maximum points possible for this section"
    )
    
    class Meta:
        ordering = ['order']
        verbose_name = 'Survey Section'
        verbose_name_plural = 'Survey Sections'
        unique_together = ['survey', 'order']
    
    def __str__(self):
        return f"{self.survey.title} - Section {self.order}: {self.title}"


class QuestionType(models.TextChoices):
    """Types of questions supported."""
    SINGLE_CHOICE = 'SINGLE_CHOICE', 'Single Choice (Radio)'
    MULTIPLE_CHOICE = 'MULTIPLE_CHOICE', 'Multiple Choice (Checkbox)'
    TEXT = 'TEXT', 'Text Input'
    EMAIL = 'EMAIL', 'Email Input'


class Question(models.Model):
    """
    Individual questions within a survey.
    """
    survey = models.ForeignKey(
        Survey,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    
    section = models.ForeignKey(
        SurveySection,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    
    question_text = models.TextField(
        help_text="The actual question text"
    )
    
    question_type = models.CharField(
        max_length=20,
        choices=QuestionType.choices,
        default=QuestionType.SINGLE_CHOICE
    )
    
    order = models.PositiveIntegerField(
        help_text="Order of this question within the section"
    )
    
    is_required = models.BooleanField(
        default=True,
        help_text="Is this question required?"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Is this question currently active?"
    )
    
    # Scoring
    max_points = models.PositiveIntegerField(
        help_text="Maximum points possible for this question"
    )
    
    # Help text for the question
    help_text = models.TextField(
        blank=True,
        null=True,
        help_text="Additional help text for this question"
    )
    
    class Meta:
        ordering = ['section__order', 'order']
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'
        unique_together = ['section', 'order']
    
    def __str__(self):
        return f"Q{self.section.order}.{self.order}: {self.question_text[:50]}..."


class QuestionOption(models.Model):
    """
    Answer options for single/multiple choice questions.
    """
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='options'
    )
    
    option_text = models.CharField(
        max_length=500,
        help_text="The text for this answer option"
    )
    
    order = models.PositiveIntegerField(
        help_text="Order of this option within the question"
    )
    
    # Scoring for this option
    points = models.IntegerField(
        default=0,
        help_text="Points awarded for selecting this option"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Is this option currently active?"
    )
    
    class Meta:
        ordering = ['order']
        verbose_name = 'Question Option'
        verbose_name_plural = 'Question Options'
        unique_together = ['question', 'order']
    
    def __str__(self):
        return f"{self.question.question_text[:30]}... - {self.option_text[:30]}..."


class SurveySubmissionStatus(models.TextChoices):
    """Status of survey submissions."""
    ACTIVE = 'ACTIVE', 'Active (counts for statistics)'
    DISABLED = 'DISABLED', 'Disabled (hidden from statistics)'
    DELETED = 'DELETED', 'Deleted'


class SurveySubmission(models.Model):
    """
    A completed survey by a prospect.
    
    Business rules:
    - One prospect can have multiple submissions
    - Only ACTIVE submissions count for statistics
    - DISABLED submissions are kept for audit but hidden
    """
    prospect = models.ForeignKey(
        'prospects.Prospect',
        on_delete=models.CASCADE,
        related_name='survey_submissions'
    )
    
    survey = models.ForeignKey(
        Survey,
        on_delete=models.CASCADE,
        related_name='submissions'
    )
    
    # Submission status for data quality management
    status = models.CharField(
        max_length=20,
        choices=SurveySubmissionStatus.choices,
        default=SurveySubmissionStatus.ACTIVE,
        help_text="Status for managing data quality"
    )
    
    # Optional notes about why submission was disabled/deleted
    admin_notes = models.TextField(
        blank=True,
        null=True,
        help_text="Admin notes about status changes"
    )
    
    # Timestamps
    started_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the prospect started the survey"
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the prospect completed the survey"
    )
    
    # IP address for detecting suspicious patterns
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address of the submitter"
    )
    
    class Meta:
        ordering = ['-started_at']
        verbose_name = 'Survey Submission'
        verbose_name_plural = 'Survey Submissions'
    
    def __str__(self):
        return f"{self.prospect.name} - {self.survey.title} ({self.started_at.strftime('%Y-%m-%d')})"
    
    def is_completed(self):
        """Check if this submission is completed."""
        return self.completed_at is not None
    
    def disable_submission(self, reason=None, admin_user=None):
        """Disable this submission (remove from statistics)."""
        self.status = SurveySubmissionStatus.DISABLED
        if reason:
            admin_note = f"Disabled by {admin_user or 'admin'}: {reason}"
            if self.admin_notes:
                self.admin_notes += f"\n{admin_note}"
            else:
                self.admin_notes = admin_note
        self.save(update_fields=['status', 'admin_notes'])
    
    def get_total_score(self):
        """Calculate total score for this submission."""
        if hasattr(self, 'score_result'):
            return self.score_result.total_score
        return 0


class Response(models.Model):
    """
    Individual responses to questions within a survey submission.
    """
    submission = models.ForeignKey(
        SurveySubmission,
        on_delete=models.CASCADE,
        related_name='responses'
    )
    
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='responses'
    )
    
    # For single choice questions
    selected_option = models.ForeignKey(
        QuestionOption,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Selected option for single choice questions"
    )
    
    # For multiple choice questions
    selected_options = models.ManyToManyField(
        QuestionOption,
        blank=True,
        related_name='multi_responses',
        help_text="Selected options for multiple choice questions"
    )
    
    # For text/email questions
    text_response = models.TextField(
        blank=True,
        null=True,
        help_text="Text response for text/email questions"
    )
    
    # Calculated points for this response
    points_earned = models.PositiveIntegerField(
        default=0,
        help_text="Points earned for this response"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Response'
        verbose_name_plural = 'Responses'
        unique_together = ['submission', 'question']
    
    def __str__(self):
        return f"{self.submission.prospect.name} - Q{self.question.order}"
    
    def calculate_points(self):
            """Calculate and save points for this response."""
            total_points = 0
            
            if self.selected_option:
                # Single choice question
                total_points = self.selected_option.points
            elif self.selected_options.exists():
                # Multiple choice question - sumar todos los puntos
                total_points = sum(opt.points for opt in self.selected_options.all())
            
            self.points_earned = total_points
            self.save(update_fields=['points_earned'])
            return total_points