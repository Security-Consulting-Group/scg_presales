"""
reports/views.py - Views for generating security assessment reports
"""
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views import View
from django.utils import timezone
import zipfile
from io import BytesIO

from scoring.models import ScoreResult
from .pdf_generator import SecurityReportGenerator

import logging
logger = logging.getLogger(__name__)


class SecurityReportPDFView(LoginRequiredMixin, View):
    """
    Generate and download security assessment PDF report.
    """
    
    def get(self, request, score_result_id):
        """Generate and return PDF report for download."""
        try:
            # Get the score result
            score_result = get_object_or_404(
                ScoreResult.objects.select_related(
                    'submission__prospect',
                    'submission__survey'
                ),
                id=score_result_id
            )
            
            # Verify it's complete
            if not score_result.submission.completed_at:
                return HttpResponse(
                    "No se puede generar reporte para una evaluación incompleta",
                    status=400
                )
            
            # Generate PDF
            generator = SecurityReportGenerator(score_result)
            pdf_buffer = generator.generate_report()
            
            # Configure download
            filename_info = generator.get_filename_info()
            
            response = HttpResponse(
                pdf_buffer.getvalue(),
                content_type='application/pdf'
            )
            response['Content-Disposition'] = f'attachment; filename="{filename_info["full_name"]}"'
            response['Content-Length'] = len(pdf_buffer.getvalue())
            
            # Log
            logger.info(f"PDF generated for ScoreResult {score_result_id} by {request.user.email}")
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating PDF for ScoreResult {score_result_id}: {str(e)}")
            return HttpResponse("Error generando el reporte PDF.", status=500)


class SecurityReportPreviewView(LoginRequiredMixin, View):
    """
    Generate PDF report preview (inline display).
    """
    
    def get(self, request, score_result_id):
        """Generate and return PDF report for preview."""
        try:
            score_result = get_object_or_404(
                ScoreResult.objects.select_related(
                    'submission__prospect',
                    'submission__survey'
                ),
                id=score_result_id
            )
            
            if not score_result.submission.completed_at:
                return HttpResponse(
                    "No se puede generar vista previa para evaluación incompleta", 
                    status=400
                )
            
            # Generate PDF
            generator = SecurityReportGenerator(score_result)
            pdf_buffer = generator.generate_report()
            
            # Preview (inline)
            response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = 'inline; filename="preview.pdf"'
            
            logger.info(f"PDF preview generated for ScoreResult {score_result_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error generating PDF preview: {str(e)}")
            return HttpResponse("Error generando la vista previa.", status=500)


class BulkReportsGenerateView(LoginRequiredMixin, View):
    """
    Generate bulk PDF reports for multiple score results.
    """
    
    def get(self, request):
        """Generate and return ZIP file with multiple PDF reports."""
        try:
            # Get parameters
            score_ids = request.GET.get('score_ids', '')
            survey_id = request.GET.get('survey_id')
            risk_level = request.GET.get('risk_level')
            
            # Build base queryset
            queryset = ScoreResult.objects.select_related(
                'submission__prospect',
                'submission__survey'
            ).filter(
                submission__completed_at__isnull=False
            )
            
            # Filter by specific IDs if provided
            if score_ids:
                try:
                    id_list = [int(id.strip()) for id in score_ids.split(',') if id.strip()]
                    queryset = queryset.filter(id__in=id_list)
                except ValueError:
                    return HttpResponse("IDs de score inválidos", status=400)
            
            # Additional filters
            if survey_id:
                queryset = queryset.filter(submission__survey_id=survey_id)
            
            if risk_level:
                queryset = queryset.filter(risk_level=risk_level)
            
            # Safety limit
            if queryset.count() > 50:
                return HttpResponse(
                    "Demasiados reportes solicitados. Máximo 50 reportes por lote.", 
                    status=400
                )
            
            if not queryset.exists():
                return HttpResponse("No se encontraron score results válidos", status=404)
            
            # Create ZIP with PDFs
            zip_buffer = BytesIO()
            
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for score_result in queryset:
                    try:
                        # Generate individual PDF
                        generator = SecurityReportGenerator(score_result)
                        pdf_buffer = generator.generate_report()
                        
                        # File name
                        filename_info = generator.get_filename_info()
                        filename = f"Reporte_{filename_info['base_name']}_{filename_info['date']}.pdf"
                        
                        # Add to ZIP
                        zip_file.writestr(filename, pdf_buffer.getvalue())
                        
                    except Exception as e:
                        logger.error(f"Error generating PDF for ScoreResult {score_result.id} in bulk: {str(e)}")
                        continue
            
            # Configure response
            zip_buffer.seek(0)
            response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
            
            timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
            response['Content-Disposition'] = f'attachment; filename="Reportes_Ciberseguridad_{timestamp}.zip"'
            
            logger.info(f"Bulk PDF generation completed: {queryset.count()} reports by user {request.user.email}")
            
            return response
            
        except Exception as e:
            logger.error(f"Error in bulk PDF generation: {str(e)}")
            return HttpResponse("Error generando los reportes masivos.", status=500)