"""
Prospects models for SCG Presales system.
"""
from django.db import models
from django.core.validators import EmailValidator
from django.utils import timezone


class ProspectStatus(models.TextChoices):
    """Status choices for prospects in the sales pipeline."""
    LEAD = 'LEAD', 'Lead'
    QUALIFIED = 'QUALIFIED', 'Qualified'
    IN_PROCESS = 'IN_PROCESS', 'In Process'
    CLOSED_WON = 'CLOSED_WON', 'Closed Won'
    CLOSED_LOST = 'CLOSED_LOST', 'Closed Lost'


class IndustryChoices(models.TextChoices):
    """Industry choices based on the survey question."""
    FINANCIAL_SERVICES = 'FINANCIAL_SERVICES', 'Servicios financieros'
    RETAIL_ECOMMERCE = 'RETAIL_ECOMMERCE', 'Retail/E-commerce'
    MANUFACTURING = 'MANUFACTURING', 'Manufactura'
    HEALTHCARE = 'HEALTHCARE', 'Servicios de salud'
    LOGISTICS_TRANSPORT = 'LOGISTICS_TRANSPORT', 'Logística y transporte'
    TECHNOLOGY = 'TECHNOLOGY', 'Tecnología'
    OTHER = 'OTHER', 'Otros'


class CompanySizeChoices(models.TextChoices):
    """Company size choices based on the survey question."""
    SMALL = '10-50', '10-50 empleados'
    MEDIUM = '51-200', '51-200 empleados'
    LARGE = '201-500', '201-500 empleados'
    ENTERPRISE = '500+', 'Más de 500 empleados'


class Prospect(models.Model):
    """
    Main prospect model - represents a potential customer.
    
    Key business rule: Email is the unique identifier.
    If someone fills multiple forms with the same email, we update the existing record.
    """
    # Core identification
    email = models.EmailField(
        unique=True,
        validators=[EmailValidator()],
        help_text="Email is the unique identifier for prospects"
    )
    name = models.CharField(
        max_length=100,
        help_text="Prospect's full name"
    )
    
    # Company information (may be filled progressively)
    company_name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Company name - may be filled later"
    )
    company_industry = models.CharField(
        max_length=50,
        choices=IndustryChoices.choices,
        blank=True,
        null=True,
        help_text="Industry sector from survey"
    )
    company_size = models.CharField(
        max_length=20,
        choices=CompanySizeChoices.choices,
        blank=True,
        null=True,
        help_text="Company size from survey"
    )
    
    # Sales pipeline
    status = models.CharField(
        max_length=20,
        choices=ProspectStatus.choices,
        default=ProspectStatus.LEAD,
        help_text="Current status in sales pipeline"
    )
    
    # Source tracking
    initial_source = models.CharField(
        max_length=50,
        choices=[
            ('CONTACT_FORM', 'Contact Form'),
            ('SURVEY', 'Diagnostic Survey'),
            ('REFERRAL', 'Referral'),
            ('OTHER', 'Other'),
        ],
        help_text="How this prospect first contacted us"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_contact_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last time we contacted this prospect"
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Prospect'
        verbose_name_plural = 'Prospects'
    
    def __str__(self):
        return f"{self.name} ({self.email}) - {self.status}"
    
    def get_latest_score(self):
        """Get the most recent survey score for this prospect."""
        from scoring.models import SurveySubmission
        latest_submission = self.survey_submissions.filter(
            status='ACTIVE'
        ).order_by('-created_at').first()
        
        if latest_submission and hasattr(latest_submission, 'score_result'):
            return latest_submission.score_result
        return None
    
    def has_completed_survey(self):
        """Check if prospect has completed at least one survey."""
        return self.survey_submissions.filter(status='ACTIVE').exists()
    
    def update_status_to_qualified(self):
        """Auto-update status when prospect completes survey."""
        if self.status == ProspectStatus.LEAD and self.has_completed_survey():
            self.status = ProspectStatus.QUALIFIED
            self.save(update_fields=['status', 'updated_at'])


class ProspectInquiry(models.Model):
    """
    Multiple inquiries/questions from the same prospect.
    
    Business rule: A prospect can submit multiple contact forms over time.
    Each submission creates a new inquiry record.
    """
    prospect = models.ForeignKey(
        Prospect,
        on_delete=models.CASCADE,
        related_name='inquiries',
        help_text="The prospect who made this inquiry"
    )
    
    message = models.TextField(
        help_text="The prospect's question or message"
    )
    
    source = models.CharField(
        max_length=50,
        choices=[
            ('CONTACT_FORM', 'Contact Form'),
            ('PHONE_CALL', 'Phone Call'),
            ('EMAIL', 'Email'),
            ('MEETING', 'Meeting'),
            ('OTHER', 'Other'),
        ],
        default='CONTACT_FORM',
        help_text="How this inquiry was received"
    )
    
    # Response tracking
    is_responded = models.BooleanField(
        default=False,
        help_text="Has this inquiry been responded to?"
    )
    responded_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this inquiry was responded to"
    )
    responded_by = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Who responded to this inquiry"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Prospect Inquiry'
        verbose_name_plural = 'Prospect Inquiries'
    
    def __str__(self):
        return f"{self.prospect.name} - {self.source} ({self.created_at.strftime('%Y-%m-%d')})"
    
    def mark_as_responded(self, responded_by=None):
        """Mark this inquiry as responded."""
        self.is_responded = True
        self.responded_at = timezone.now()
        if responded_by:
            self.responded_by = responded_by
        self.save(update_fields=['is_responded', 'responded_at', 'responded_by'])


class InteractionNote(models.Model):
    """
    Notes about interactions with prospects - meetings, calls, etc.
    
    This is where sales team tracks their conversations and next steps.
    """
    prospect = models.ForeignKey(
        Prospect,
        on_delete=models.CASCADE,
        related_name='interaction_notes',
        help_text="The prospect this note is about"
    )
    
    note_type = models.CharField(
        max_length=50,
        choices=[
            ('PHONE_CALL', 'Phone Call'),
            ('MEETING', 'Meeting'),
            ('EMAIL', 'Email'),
            ('DEMO', 'Demo'),
            ('PROPOSAL', 'Proposal'),
            ('FOLLOW_UP', 'Follow-up'),
            ('OTHER', 'Other'),
        ],
        help_text="Type of interaction"
    )
    
    title = models.CharField(
        max_length=200,
        help_text="Brief title for this interaction"
    )
    
    content = models.TextField(
        help_text="Detailed notes about the interaction"
    )
    
    next_steps = models.TextField(
        blank=True,
        null=True,
        help_text="What are the next steps?"
    )
    
    follow_up_date = models.DateField(
        null=True,
        blank=True,
        help_text="When to follow up next"
    )
    
    created_by = models.CharField(
        max_length=100,
        help_text="Who created this note"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Interaction Note'
        verbose_name_plural = 'Interaction Notes'
    
    def __str__(self):
        return f"{self.prospect.name} - {self.title} ({self.created_at.strftime('%Y-%m-%d')})"