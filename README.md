# SCG Presales - Cybersecurity Assessment Platform

SCG Presales is a Django-based platform for conducting cybersecurity assessments and managing the sales pipeline for security services. The system allows prospects to take diagnostic surveys, generates risk assessments, and provides automated PDF reports with security recommendations.

## Features

### Core Functionality
- **Prospect Management**: Track leads through the sales pipeline with contact information, company details, and interaction history
- **Survey System**: Configurable cybersecurity diagnostic surveys with multiple question types (single choice, multiple choice, text input)
- **Risk Assessment**: Automated scoring system that calculates risk levels based on survey responses
- **PDF Report Generation**: Customizable security assessment reports with recommendations
- **Landing Page**: Public-facing interface for prospects to access surveys
- **Admin Panel**: Internal dashboard for managing prospects, surveys, and scoring configurations

### Technical Features
- **Multi-environment Support**: Separate settings for development and production
- **Email Integration**: Automated email notifications for survey completion
- **Logging System**: Comprehensive logging for audit and debugging
- **Media Management**: File upload and storage for reports and assets
- **Responsive Design**: Bootstrap-based UI for all user interfaces

## Project Structure

```
scg_presales/
├── admin_panel/          # Internal admin interface
├── communications/       # Email and messaging functionality
├── core/                 # Django project core settings
│   ├── settings/         # Environment-specific configurations
│   └── management/       # Custom Django commands
├── landing/              # Public landing page
├── prospects/            # Prospect and lead management
├── reports/              # PDF report generation
├── scoring/              # Risk assessment and scoring engine
├── surveys/              # Survey creation and management
├── static/               # CSS, JavaScript, and image assets
├── templates/            # HTML templates
└── media/                # User-uploaded files and generated reports
```

## Installation

### Prerequisites
- Python 3.8+
- Django 5.1.4
- WeasyPrint for PDF generation

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd scg_presales
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Database setup**
   ```bash
   python manage.py migrate
   ```

5. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Load initial data (optional)**
   ```bash
   python manage.py load_survey_data
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

## Configuration

### Environment Settings

The project uses environment-specific settings:

- **Development**: `core/settings/development.py`
- **Production**: `core/settings/production.py`

Set the `DJANGO_SETTINGS_MODULE` environment variable to select the appropriate configuration.

### Survey Configuration

1. **Create Survey**: Use the admin panel to create new surveys with sections and questions
2. **Risk Configuration**: Configure risk level thresholds for each survey
3. **Package Recommendations**: Set up service package recommendations for each risk level

## Usage

### For Prospects (Public Interface)

1. **Landing Page**: Visit the homepage to access featured surveys
2. **Survey Completion**: Complete the cybersecurity diagnostic survey
3. **Report Generation**: Receive automated PDF report with security recommendations

### For Administrators

1. **Admin Panel**: Access `/admin-panel/` for prospect management
2. **Survey Management**: Create and configure surveys, questions, and scoring
3. **Report Downloads**: Generate and download prospect assessment reports
4. **Pipeline Management**: Track prospects through the sales pipeline

## Key Models

### Prospects
- **Prospect**: Core prospect information with contact details and company info
- **ProspectInquiry**: Multiple inquiries from the same prospect
- **InteractionNote**: Sales team interaction tracking

### Surveys
- **Survey**: Main survey configuration with versions and status
- **SurveySection**: Organized sections within surveys
- **Question**: Individual questions with multiple types supported
- **SurveySubmission**: Completed surveys by prospects

### Scoring
- **ScoreResult**: Calculated risk assessment results
- **SurveyRiskConfiguration**: Configurable risk level thresholds
- **RiskLevelPackageRecommendation**: Service package recommendations

## API Endpoints

- `/` - Landing page
- `/survey/<survey_code>/` - Public survey interface
- `/admin-panel/` - Administrative dashboard
- `/reports/` - Report generation and download
- `/admin/` - Django admin interface

## Development

### Running Tests
```bash
python manage.py test
```

### Creating Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Static Files
```bash
python manage.py collectstatic
```

## Logging

The system includes comprehensive logging configuration:
- **Console Output**: Development debugging
- **File Logging**: Production audit trails
- **Application Logs**: Stored in `logs/` directory

## Security Features

- **CSRF Protection**: Django's built-in CSRF middleware
- **User Authentication**: Django's authentication system
- **IP Tracking**: Survey submission IP logging
- **Input Validation**: Form validation and sanitization
- **Secure Media Handling**: Proper file upload restrictions

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is proprietary software developed for SCG's cybersecurity assessment services.