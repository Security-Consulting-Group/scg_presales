"""
URLs for reports app
"""
from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # PDF generation - using class-based views
    path(
        'pdf/security-assessment/<int:score_result_id>/', 
        views.SecurityReportPDFView.as_view(), 
        name='generate_security_pdf'
    ),
    path(
        'pdf/security-assessment/<int:score_result_id>/preview/', 
        views.SecurityReportPreviewView.as_view(), 
        name='preview_security_pdf'
    ),
    path(
        'pdf/bulk-generate/', 
        views.BulkReportsGenerateView.as_view(), 
        name='bulk_generate_reports'
    ),
]