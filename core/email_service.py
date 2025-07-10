"""
core/email_service.py - Email service for sending survey completion notifications
"""
import logging
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
from django.utils import timezone
from reports.pdf_generator import SecurityReportGenerator

logger = logging.getLogger(__name__)


class SurveyEmailService:
    """Service for sending survey completion emails with PDF attachments"""
    
    @staticmethod
    def send_survey_completion_email(score_result):
        """
        Send survey completion email with PDF attachment

        Args:
            score_result: ScoreResult instance

        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        try:
            # Get data from score_result
            submission = score_result.submission
            prospect = submission.prospect
            survey = submission.survey
            
            # Prepare email context
            context = SurveyEmailService._prepare_email_context(score_result)
            
            # Render email content
            html_content = render_to_string('emails/survey_completion.html', context)
            text_content = strip_tags(html_content)  # Fallback plain text
            
            # Email details
            subject = (
                f"Su Evaluación de Ciberseguridad - "
                f"{prospect.company_name or prospect.name}"
            )
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = [prospect.email]
            
            # Create email message
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=from_email,
                to=to_email
            )
            
            # Attach HTML content
            email.attach_alternative(html_content, "text/html")
            
            # Generate and attach PDF in production
            if not settings.DEBUG:
                try:
                    pdf_attachment = SurveyEmailService._generate_pdf_attachment(
                        score_result
                    )
                    if pdf_attachment:
                        email.attach(*pdf_attachment)
                        logger.info(f"PDF attachment added for {prospect.email}")
                except Exception as e:
                    logger.error(
                        f"Error generating PDF attachment for {prospect.email}: {str(e)}"
                    )
                    # Continue without attachment rather than failing completely
            
            # Send email
            if settings.DEBUG:
                # In development, log email to console instead of sending
                SurveyEmailService._log_email_to_console(email, context)
                return True
            else:
                # In production, send real email
                email.send()
                logger.info(
                    f"Survey completion email sent to {prospect.email}"
                )
                return True
                
        except Exception as e:
            logger.error(
                f"Error sending survey completion email: {str(e)}", exc_info=True
            )
            return False
    
    @staticmethod
    def _prepare_email_context(score_result):
        """Prepare context data for email template"""
        submission = score_result.submission
        prospect = submission.prospect
        
        # Map risk levels to CSS classes
        risk_level_classes = {
            'CRITICAL': 'critical',
            'HIGH': 'high', 
            'MODERATE': 'moderate',
            'GOOD': 'good',
            'EXCELLENT': 'excellent'
        }
        
        # Map risk levels to display names
        risk_level_displays = {
            'CRITICAL': 'CRÍTICO',
            'HIGH': 'ALTO',
            'MODERATE': 'MEDIO',
            'GOOD': 'BAJO',
            'EXCELLENT': 'EXCELENTE'
        }
        
        return {
            'prospect_name': prospect.name,
            'company_name': (
                prospect.company_name or
                f"{prospect.name.split()[0].upper()} EMPRESA"
            ),
            'prospect_email': prospect.email,
            'score_percentage': int(score_result.score_percentage),
            'risk_level_display': risk_level_displays.get(
                score_result.risk_level, score_result.risk_level
            ),
            'risk_level_class': risk_level_classes.get(
                score_result.risk_level, 'moderate'
            ),
            'survey_title': submission.survey.title,
            'completion_date': submission.completed_at.strftime('%d de %B de %Y'),
        }
    
    @staticmethod
    def _generate_pdf_attachment(score_result):
        """Generate PDF attachment for email"""
        try:
            # Generate PDF
            generator = SecurityReportGenerator(score_result)
            pdf_buffer = generator.generate_report()
            
            # Get filename info
            filename_info = generator.get_filename_info()
            filename = filename_info['full_name']
            
            # Return attachment tuple (filename, content, mimetype)
            return (filename, pdf_buffer.getvalue(), 'application/pdf')
            
        except Exception as e:
            logger.error(f"Error generating PDF attachment: {str(e)}")
            return None
    
    @staticmethod
    def _log_email_to_console(email, context):
        """Log email details to console for development"""
        print("\n" + "="*80)
        print("DEVELOPMENT EMAIL - Survey Completion Notification")
        print("="*80)
        print(f"To: {', '.join(email.to)}")
        print(f"Subject: {email.subject}")
        print(f"Prospect: {context['prospect_name']} ({context['prospect_email']})")
        print(f"Company: {context['company_name']}")
        print(f"Score: {context['score_percentage']}% ({context['risk_level_display']})")
        print(f"Completion: {context['completion_date']}")
        print("-"*80)
        print("HTML CONTENT PREVIEW:")
        print("-"*80)
        # Show a preview of the HTML content (first 500 chars)
        html_preview = email.alternatives[0][0][:500] + "..." if len(email.alternatives[0][0]) > 500 else email.alternatives[0][0]
        print(html_preview)
        print("-"*80)
        print("PDF Attachment: Not generated in development mode")
        print("In production, this email would be sent with PDF attached")
        print("="*80 + "\n")


class EmailTestService:
    """Service for testing email functionality"""
    
    @staticmethod
    def send_test_email(to_email):
        """Send a test email to verify email configuration"""
        try:
            subject = "Test Email - SCG Presales System"
            message = """
            This is a test email from the SCG Presales system.
            
            If you receive this email, the email configuration is working correctly.
            
            Time sent: {}
            Environment: {}
            """.format(
                timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
                'Development' if settings.DEBUG else 'Production'
            )
            
            from django.core.mail import send_mail
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[to_email],
                fail_silently=False
            )
            
            logger.info(f"Test email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending test email: {str(e)}")
            return False 