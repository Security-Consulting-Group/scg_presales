"""
URLs for reports app
"""
from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # PDF generation
    path(
        'pdf/security-assessment/<int:score_result_id>/', 
        views.generate_security_report_pdf, 
        name='generate_security_pdf'
    ),
    path(
        'pdf/security-assessment/<int:score_result_id>/preview/', 
        views.preview_security_report_pdf, 
        name='preview_security_pdf'
    ),
    path(
        'pdf/bulk-generate/', 
        views.bulk_generate_reports, 
        name='bulk_generate_reports'
    ),
]