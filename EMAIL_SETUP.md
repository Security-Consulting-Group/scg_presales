# Email Functionality Documentation

## Overview

The SCG Presales system now automatically sends survey completion emails with PDF reports when users complete cybersecurity surveys.

## Features

### ✅ Automatic Email Sending
- **When**: Automatically triggered when a survey is completed
- **To**: The prospect's email address entered during survey
- **Content**: Professional HTML email with survey results and next steps
- **Attachment**: PDF report (production only)

### ✅ Environment-Specific Behavior
- **Development**: Emails displayed in terminal console + no PDF attachment
- **Production**: Real emails sent via SMTP + PDF attached

### ✅ Professional Email Template
- Company branding with SCG colors
- Survey score display with risk level colors
- Call-to-action for scheduling consultation
- Contact information and next steps

## Email Configuration

### Development Environment
```python
# core/settings/development.py
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

### Production Environment
```python
# core/settings/production.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST')  # e.g., 'smtp.office365.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER)
```

## Required Environment Variables (Production)

Add these to your `.env/production.env` file:

```bash
# Email settings
EMAIL_HOST=smtp.office365.com
EMAIL_HOST_USER=your-email@securitygroupcr.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=SCG Presales <your-email@securitygroupcr.com>
```

## Testing Email Functionality

### Basic Email Test
```bash
python manage.py test_email --email your-test@email.com --test-basic
```

### Survey Completion Email Test
```bash
# Test with latest survey result
python manage.py test_email --email your-test@email.com --test-survey

# Test with specific ScoreResult ID
python manage.py test_email --email your-test@email.com --test-survey --score-id 1
```

### Complete Test Suite
```bash
# Run all tests
python manage.py test_email --email your-test@email.com
```

## How It Works

### Automatic Triggering
1. User completes survey on the website
2. `SurveySubmission` is marked as completed
3. Django signal `submission_completed` is triggered
4. Scoring is calculated automatically
5. **NEW**: Email is sent automatically via `SurveyEmailService`

### Email Content
The email includes:
- Personalized greeting with prospect name
- Company name
- Survey score percentage
- Risk level with appropriate color coding
- Next steps recommendations
- PDF report attachment (production only)
- Call-to-action for consultation booking
- Company contact information

### Email Service Components

#### `SurveyEmailService`
- Main service for sending survey completion emails
- Handles template rendering
- Manages PDF generation and attachment
- Environment-aware (dev vs production)

#### Email Template
- Located: `templates/emails/survey_completion.html`
- Responsive HTML design
- Spanish language content
- Professional branding

#### Development Console Output
When running in development, emails are displayed in the terminal with:
- 📧 Email headers and recipient
- 👤 Prospect and company information  
- 📊 Survey score and risk level
- 📄 HTML content preview
- 💡 Notes about production behavior

## Troubleshooting

### Email Not Sending in Production
1. Check environment variables are set correctly
2. Verify SMTP settings with your email provider
3. Check Django logs for error messages
4. Test with basic email first: `python manage.py test_email --test-basic`

### Email Template Issues
1. Check template syntax in `templates/emails/survey_completion.html`
2. Verify context variables are available
3. Test template rendering with test command

### PDF Attachment Issues
1. Check `reports/pdf_generator.py` for errors
2. Verify all required context data is available
3. Check file permissions and disk space

### Debugging
Enable detailed logging by checking:
```bash
# View Django logs
tail -f django.log

# Check email service logs specifically
python manage.py shell -c "import logging; logging.getLogger('core.email_service').setLevel(logging.DEBUG)"
```

## Integration Points

### Signal Integration
```python
# scoring/signals.py
from core.email_service import SurveyEmailService

# Automatic email sending after score calculation
email_sent = SurveyEmailService.send_survey_completion_email(score_result)
```

### PDF Integration
```python
# core/email_service.py
from reports.pdf_generator import SecurityReportGenerator

# PDF generation and attachment
generator = SecurityReportGenerator(score_result)
pdf_buffer = generator.generate_report()
```

## File Structure

```
scg_presales/
├── core/
│   ├── email_service.py              # Email service classes
│   ├── management/commands/
│   │   └── test_email.py            # Email testing command
│   └── settings/
│       ├── base.py                  # Base email settings
│       ├── development.py           # Dev email config
│       └── production.py            # Prod email config
├── templates/
│   └── emails/
│       └── survey_completion.html   # Email template
└── scoring/
    └── signals.py                   # Integration point
```

## Security Notes

- Email passwords should use app-specific passwords, not regular account passwords
- All email credentials stored in environment variables
- TLS encryption enabled for production email sending
- Email template designed to prevent spam classification
- No sensitive information exposed in email content beyond survey results

## Future Enhancements

Potential improvements:
- Email tracking and analytics
- Custom email templates per client
- Email scheduling and delays
- Bounce handling and retry logic
- A/B testing for email content
- Multi-language email support 