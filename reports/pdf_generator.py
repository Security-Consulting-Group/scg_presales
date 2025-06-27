"""
reports/pdf_generator.py - WeasyPrint PDF Generator
Uses WeasyPrint for full CSS support and better HTML rendering
"""
import os
from io import BytesIO
from django.template.loader import render_to_string
from django.contrib.staticfiles import finders
from django.conf import settings
import weasyprint


class SecurityReportGenerator:
    """Generador de reportes usando WeasyPrint con soporte completo de CSS"""
    
    def __init__(self, score_result):
        self.score_result = score_result
        self.submission = score_result.submission
        self.prospect = self.submission.prospect
        self.survey = self.submission.survey
        
    def generate_report(self):
        """
        Genera reporte PDF usando WeasyPrint
        
        Returns:
            BytesIO buffer con PDF generado
        """
        # Preparar contexto para template
        context = self._prepare_context()
        
        # Renderizar template HTML completo
        html_content = render_to_string('reports/security_assessment.html', context)
        
        # Generar PDF con WeasyPrint
        return self._generate_pdf_with_weasyprint(html_content)
    
    def _generate_pdf_with_weasyprint(self, html_content):
        """Genera PDF usando WeasyPrint"""
        # Create PDF buffer
        pdf_buffer = BytesIO()
        
        # Configure WeasyPrint with base URL for static files
        base_url = self._get_base_url()
        
        # Generate PDF
        html_doc = weasyprint.HTML(
            string=html_content,
            base_url=base_url
        )
        
        pdf_doc = html_doc.write_pdf()
        pdf_buffer.write(pdf_doc)
        pdf_buffer.seek(0)
        
        return pdf_buffer
    
    def _get_base_url(self):
        """Get base URL for static files"""
        if settings.DEBUG:
            # In development, use the local static files directory
            static_dirs = getattr(settings, 'STATICFILES_DIRS', [])
            if static_dirs:
                import urllib.request
                return urllib.request.pathname2url(os.path.abspath(static_dirs[0]))
            
            # Fallback to STATIC_ROOT if no STATICFILES_DIRS
            static_root = getattr(settings, 'STATIC_ROOT', '')
            if static_root:
                import urllib.request
                return urllib.request.pathname2url(os.path.abspath(static_root))
        else:
            # In production, use the configured static URL
            return settings.STATIC_URL
        
        # Final fallback
        return '.'
    
    def _prepare_context(self):
        """Prepara contexto para el template"""
        from .security_content_data import SecurityContentData
        
        content_data = SecurityContentData()
        
        # Información básica
        company_name = self.prospect.company_name or f"{self.prospect.name.split()[0].upper()} EMPRESA"
        fecha_actual = self._format_date()
        risk_level_display = self._get_risk_level_display()
        
        # Get absolute file paths for images
        cover_image_url = self._get_absolute_static_url('img/reports/cover.png')
        logo_image_url = self._get_absolute_static_url('img/reports/ImagotipoNegativo.png')
        sidebar_image_1 = self._get_absolute_static_url('img/reports/sidebart_1.png')
        sidebar_image_5 = self._get_absolute_static_url('img/reports/sidebart_5.png')
        sidebar_image_8 = self._get_absolute_static_url('img/reports/sidebart_8.png')
        sidebar_image_10 = self._get_absolute_static_url('img/reports/sidebart_10.png')
        sidebar_image_11 = self._get_absolute_static_url('img/reports/sidebart_11.png')
        sidebar_image_12 = self._get_absolute_static_url('img/reports/sidebart_12.png')
        section_globe_image_url = self._get_absolute_static_url('img/reports/section_globe.png')
        section_risk_image_url = self._get_absolute_static_url('img/reports/section_risk.png')
        section_solution_image_url = self._get_absolute_static_url('img/reports/section_solution.png')
        

        
        return {
            # Datos del score
            'score_result': self.score_result,
            'prospect': self.prospect,
            'company_name': company_name,
            'fecha_actual': fecha_actual,
            'risk_level_display': risk_level_display,
            
            # Absolute image URLs for WeasyPrint
            'cover_image_url': cover_image_url,
            'logo_image_url': logo_image_url,
            'sidebar_image_1': sidebar_image_1,
            'sidebar_image_5': sidebar_image_5,
            'sidebar_image_8': sidebar_image_8,
            'sidebar_image_10': sidebar_image_10,
            'sidebar_image_11': sidebar_image_11,
            'sidebar_image_12': sidebar_image_12,
            'section_globe_image_url': section_globe_image_url,
            'section_risk_image_url': section_risk_image_url,
            'section_solution_image_url': section_solution_image_url,
            
            # Contenido dinámico
            'risk_content': content_data.get_risk_level_content(self.score_result.risk_level),

            'vulnerabilities': content_data.get_vulnerabilities_for_score(self.score_result.risk_level),
            'recommended_package': content_data.get_recommended_package_details(self.score_result.primary_package),
            'other_packages': content_data.get_other_packages_summary(self.score_result.primary_package),
            'session_items': content_data.get_session_items(),
            'contact_info': content_data.get_contact_info(),
            'references': content_data.get_references(),
        }
    
    def _get_absolute_static_url(self, path):
        """Get absolute file URL for a static file"""
        # Find the file using Django's static file finder
        file_path = finders.find(path)
        if file_path:
            # Convert to absolute file URL
            return f"file://{os.path.abspath(file_path)}"
        
        # Fallback: try to construct path manually
        static_dirs = getattr(settings, 'STATICFILES_DIRS', [])
        for static_dir in static_dirs:
            full_path = os.path.join(static_dir, path)
            if os.path.exists(full_path):
                return f"file://{os.path.abspath(full_path)}"
        
        # Final fallback
        return None
    
    def get_filename_info(self):
        """Info para nombre de archivo"""
        prospect_name = self.prospect.name.replace(' ', '_')
        company_name = self.prospect.company_name
        
        if company_name:
            company_name = company_name.replace(' ', '_')
            filename_base = f"{company_name}_{prospect_name}"
        else:
            filename_base = prospect_name
        
        eval_date = self.submission.completed_at.strftime('%Y%m%d')
        
        return {
            'base_name': filename_base,
            'date': eval_date,
            'full_name': f"Reporte_Ciberseguridad_{filename_base}_{eval_date}.pdf"
        }
    
    def _format_date(self):
        """Formatea la fecha en español"""
        from datetime import datetime
        meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
                'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
        ahora = datetime.now()
        return f"{ahora.day} de {meses[ahora.month-1]} de {ahora.year}"
    
    def _get_risk_level_display(self):
        """Retorna el display del nivel de riesgo con emoji"""
        risk_displays = {
            'CRITICAL': '🔴 CRÍTICO',
            'HIGH': '🟠 ALTO',
            'MODERATE': '🟡 MEDIO',
            'GOOD': '🟢 BAJO',
            'EXCELLENT': '🟢 EXCELENTE'
        }
        return risk_displays.get(self.score_result.risk_level, self.score_result.risk_level)