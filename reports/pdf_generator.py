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
        
        # Enhanced WeasyPrint configuration for production
        html_doc = weasyprint.HTML(
            string=html_content,
            base_url=base_url
        )
        
        # Define CSS string for better page handling
        css_string = """
        @page {
            size: letter;
            margin: 0.75in;
            orphans: 3;
            widows: 3;
        }
        
        .page-with-sidebar {
            page-break-before: always;
            page-break-inside: avoid;
        }
        
        .content-section {
            page-break-inside: avoid;
        }
        
        h1, h2, h3 {
            page-break-after: avoid;
            orphans: 3;
            widows: 3;
        }
        
        .vulnerability-item {
            page-break-inside: avoid;
            margin-bottom: 15px;
        }
        
        .stat-item {
            page-break-inside: avoid;
        }
        
        /* Better content flow */
        p {
            orphans: 2;
            widows: 2;
        }
        
        ul, ol {
            page-break-inside: avoid;
        }
        
        /* Sidebar layout improvements */
        .main-sidebar-layout {
            page-break-inside: avoid;
        }
        """
        
        css = weasyprint.CSS(string=css_string)
        
        # Generate PDF with CSS configuration
        pdf_doc = html_doc.write_pdf(stylesheets=[css])
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
        final_cover_image_url = self._get_absolute_static_url('img/reports/final_cover.png')
        

        
        return {
            # Datos del score
            'score_result': self.score_result,
            'prospect': self.prospect,
            'company_name': company_name,
            'fecha_actual': fecha_actual,
            'risk_level_display': risk_level_display,
            'risk_level_color': self._get_risk_level_color(),
            
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
            'final_cover_image_url': final_cover_image_url,
            
            # Contenido dinámico
            'risk_content': content_data.get_risk_level_content(self.score_result.risk_level),

            'vulnerabilities': self._process_vulnerabilities(content_data.get_vulnerabilities_for_score(self.score_result.risk_level)),
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
        timestamp = self.submission.completed_at.strftime('%Y%m%d%H%M%S')
        
        return {
            'base_name': filename_base,
            'date': eval_date,
            'full_name': f"SCG_Reporte_Ciberseguridad_{timestamp}.pdf"
        }
    
    def _format_date(self):
        """Formatea la fecha en español usando la fecha de completion del survey"""
        meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
                'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
        # Use the survey completion date instead of current date
        fecha_completion = self.submission.completed_at
        return f"{fecha_completion.day} de {meses[fecha_completion.month-1]} de {fecha_completion.year}"
    
    def _get_risk_level_display(self):
        """Retorna el display del nivel de riesgo"""
        risk_displays = {
            'CRITICAL': 'CRÍTICO',
            'HIGH': 'ALTO',
            'MODERATE': 'MEDIO',
            'GOOD': 'BAJO',
            'EXCELLENT': 'EXCELENTE'
        }
        return risk_displays.get(self.score_result.risk_level, self.score_result.risk_level)
    
    def _get_risk_level_color(self):
        """Retorna la variable CSS de color apropiada para el nivel de riesgo"""
        risk_colors = {
            'CRITICAL': 'var(--risk-critical)',
            'HIGH': 'var(--risk-high)',
            'MODERATE': 'var(--risk-moderate)',
            'GOOD': 'var(--risk-good)',
            'EXCELLENT': 'var(--risk-excellent)'
        }
        return risk_colors.get(self.score_result.risk_level, 'var(--risk-critical)')
    
    def _get_vulnerability_color(self, vuln_level):
        """Retorna la variable CSS de color apropiada para el nivel de vulnerabilidad"""
        vuln_colors = {
            'CRÍTICO': 'var(--vuln-critico)',
            'ALTO': 'var(--vuln-alto)',
            'MEDIO': 'var(--vuln-medio)',
            'BAJO': 'var(--vuln-bajo)',
            'INFORMATIVO': 'var(--vuln-informativo)'
        }
        return vuln_colors.get(vuln_level, 'var(--vuln-critico)')
    
    def _process_vulnerabilities(self, vulnerabilities):
        """Procesa las vulnerabilidades añadiendo información de color"""
        processed_vulns = []
        for vuln in vulnerabilities:
            # Create a copy of the vulnerability dict and add color info
            processed_vuln = vuln.copy()
            processed_vuln['level_color'] = self._get_vulnerability_color(vuln['level'])
            processed_vulns.append(processed_vuln)
        return processed_vulns