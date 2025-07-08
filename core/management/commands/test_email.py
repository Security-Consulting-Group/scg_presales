"""
Django management command to test email functionality
"""
from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_mail
from django.conf import settings
from scoring.models import ScoreResult
from core.email_service import SurveyEmailService, EmailTestService


class Command(BaseCommand):
    """Management command to test email functionality"""
    
    help = 'Test email functionality for the SCG Presales system'

    def add_arguments(self, parser):
        """Add command arguments"""
        parser.add_argument(
            '--test-basic',
            action='store_true',
            help='Send a basic test email',
        )
        parser.add_argument(
            '--test-survey',
            action='store_true',
            help='Send a survey completion email using the latest ScoreResult',
        )
        parser.add_argument(
            '--email',
            type=str,
            help='Email address to send test emails to',
        )
        parser.add_argument(
            '--score-id',
            type=int,
            help='Specific ScoreResult ID to use for survey email test',
        )

    def handle(self, *args, **options):
        """Handle the command execution"""
        try:
            # Check if email is provided
            if not options['email']:
                raise CommandError('Email address is required. Use --email your@email.com')
            
            test_email = options['email']
            
            self.stdout.write(
                self.style.SUCCESS(f'🧪 Testing email functionality...')
            )
            self.stdout.write(f'📧 Test email: {test_email}')
            self.stdout.write(f'🔧 Environment: {"Development" if settings.DEBUG else "Production"}')
            self.stdout.write(f'📤 Email backend: {settings.EMAIL_BACKEND}')
            self.stdout.write('-' * 60)
            
            # Test basic email functionality
            if options['test_basic']:
                self.test_basic_email(test_email)
            
            # Test survey completion email
            if options['test_survey']:
                self.test_survey_email(test_email, options.get('score_id'))
            
            # If no specific test is chosen, run all tests
            if not options['test_basic'] and not options['test_survey']:
                self.test_basic_email(test_email)
                self.test_survey_email(test_email, options.get('score_id'))
                
        except Exception as e:
            raise CommandError(f'Error during email testing: {str(e)}')

    def test_basic_email(self, test_email):
        """Test basic email sending functionality"""
        self.stdout.write('\n🔍 Testing basic email functionality...')
        
        try:
            success = EmailTestService.send_test_email(test_email)
            
            if success:
                self.stdout.write(
                    self.style.SUCCESS('✅ Basic email test passed!')
                )
            else:
                self.stdout.write(
                    self.style.ERROR('❌ Basic email test failed!')
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Basic email test error: {str(e)}')
            )

    def test_survey_email(self, test_email, score_id=None):
        """Test survey completion email functionality"""
        self.stdout.write('\n🔍 Testing survey completion email...')
        
        try:
            # Get a ScoreResult for testing
            if score_id:
                score_result = ScoreResult.objects.get(id=score_id)
                self.stdout.write(f'📊 Using ScoreResult ID: {score_id}')
            else:
                score_result = ScoreResult.objects.order_by('-calculated_at').first()
                if not score_result:
                    self.stdout.write(
                        self.style.ERROR('❌ No ScoreResult found. Complete a survey first.')
                    )
                    return
                self.stdout.write(f'📊 Using latest ScoreResult ID: {score_result.id}')
            
            # Temporarily override the prospect email for testing
            original_email = score_result.submission.prospect.email
            score_result.submission.prospect.email = test_email
            
            self.stdout.write(f'👤 Prospect: {score_result.submission.prospect.name}')
            self.stdout.write(f'🏢 Company: {score_result.submission.prospect.company_name or "N/A"}')
            self.stdout.write(f'📊 Score: {score_result.score_percentage}% ({score_result.risk_level})')
            
            # Send the test email
            success = SurveyEmailService.send_survey_completion_email(score_result)
            
            # Restore original email
            score_result.submission.prospect.email = original_email
            
            if success:
                self.stdout.write(
                    self.style.SUCCESS('✅ Survey completion email test passed!')
                )
                if settings.DEBUG:
                    self.stdout.write(
                        self.style.WARNING('💡 Check your terminal output above for the email content preview')
                    )
            else:
                self.stdout.write(
                    self.style.ERROR('❌ Survey completion email test failed!')
                )
                
        except ScoreResult.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'❌ ScoreResult with ID {score_id} not found.')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Survey email test error: {str(e)}')
            ) 