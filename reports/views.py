"""
reports/views.py - SÚPER SIMPLE
Solo llama al generador - Sin lógica de contenido
"""
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods

from scoring.models import ScoreResult
from .pdf_generator import SecurityReportGenerator

import logging
logger = logging.getLogger(__name__)


@login_required
@require_http_methods(["GET"])
def generate_security_report_pdf(request, score_result_id):
    """
    Genera y descarga el reporte PDF de evaluación de ciberseguridad
    """
    try:
        # Obtener el score result
        score_result = get_object_or_404(
            ScoreResult.objects.select_related(
                'submission__prospect',
                'submission__survey'
            ),
            id=score_result_id
        )
        
        # Verificar que esté completo
        if not score_result.submission.completed_at:
            return HttpResponse(
                "No se puede generar reporte para una evaluación incompleta",
                status=400
            )
        
        # Generar PDF - TODO se maneja en el HTML
        generator = SecurityReportGenerator(score_result)
        pdf_buffer = generator.generate_report()
        
        # Configurar descarga
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


@login_required
@require_http_methods(["GET"])
def preview_security_report_pdf(request, score_result_id):
    """Vista previa del reporte PDF"""
    try:
        score_result = get_object_or_404(
            ScoreResult.objects.select_related(
                'submission__prospect',
                'submission__survey'
            ),
            id=score_result_id
        )
        
        if not score_result.submission.completed_at:
            return HttpResponse("No se puede generar vista previa para evaluación incompleta", status=400)
        
        # Generar PDF
        generator = SecurityReportGenerator(score_result)
        pdf_buffer = generator.generate_report()
        
        # Vista previa (inline)
        response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="preview.pdf"'
        
        logger.info(f"PDF preview generated for ScoreResult {score_result_id}")
        return response
        
    except Exception as e:
        logger.error(f"Error generating PDF preview: {str(e)}")
        return HttpResponse("Error generando la vista previa.", status=500)


@login_required  
@require_http_methods(["GET"])
def bulk_generate_reports(request):
    """
    Genera reportes PDF para múltiples score results
    """
    import zipfile
    from io import BytesIO
    from django.utils import timezone
    
    try:
        # Obtener parámetros
        score_ids = request.GET.get('score_ids', '')
        survey_id = request.GET.get('survey_id')
        risk_level = request.GET.get('risk_level')
        
        # Construir queryset base
        queryset = ScoreResult.objects.select_related(
            'submission__prospect',
            'submission__survey'
        ).filter(
            submission__completed_at__isnull=False
        )
        
        # Filtrar por IDs específicos si se proporcionan
        if score_ids:
            try:
                id_list = [int(id.strip()) for id in score_ids.split(',') if id.strip()]
                queryset = queryset.filter(id__in=id_list)
            except ValueError:
                return HttpResponse("IDs de score inválidos", status=400)
        
        # Filtros adicionales
        if survey_id:
            queryset = queryset.filter(submission__survey_id=survey_id)
        
        if risk_level:
            queryset = queryset.filter(risk_level=risk_level)
        
        # Límite de seguridad
        if queryset.count() > 50:
            return HttpResponse("Demasiados reportes solicitados. Máximo 50 reportes por lote.", status=400)
        
        if not queryset.exists():
            return HttpResponse("No se encontraron score results válidos", status=404)
        
        # Crear ZIP con PDFs
        zip_buffer = BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for score_result in queryset:
                try:
                    # Generar PDF individual
                    generator = SecurityReportGenerator(score_result)
                    pdf_buffer = generator.generate_report()
                    
                    # Nombre del archivo
                    filename_info = generator.get_filename_info()
                    filename = f"Reporte_{filename_info['base_name']}_{filename_info['date']}.pdf"
                    
                    # Agregar al ZIP
                    zip_file.writestr(filename, pdf_buffer.getvalue())
                    
                except Exception as e:
                    logger.error(f"Error generating PDF for ScoreResult {score_result.id} in bulk: {str(e)}")
                    continue
        
        # Configurar response
        zip_buffer.seek(0)
        response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
        
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        response['Content-Disposition'] = f'attachment; filename="Reportes_Ciberseguridad_{timestamp}.zip"'
        
        logger.info(f"Bulk PDF generation completed: {queryset.count()} reports by user {request.user.email}")
        
        return response
        
    except Exception as e:
        logger.error(f"Error in bulk PDF generation: {str(e)}")
        return HttpResponse("Error generando los reportes masivos.", status=500)