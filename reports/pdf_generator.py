"""
reports/pdf_generator.py - MINIMALISTA
SOLO convierte HTML a PDF - Sin lógica de negocio, sin hardcoding
"""
import re
from io import BytesIO
from xml.etree import ElementTree as ET
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from django.template.loader import render_to_string


class HTMLToPDFParser:
    """Parser que convierte HTML con estilos inline a PDF"""
    
    def __init__(self):
        self.document_config = {}
        self.colors_map = {}
        self.styles_map = {}
        self.page_settings = {}
        
    def parse_html_to_pdf(self, html_content):
        """
        Convierte HTML completo (con config y estilos) a PDF
        
        Args:
            html_content: String con HTML completo del template
            
        Returns:
            BytesIO buffer con PDF generado
        """
        # Extraer configuración del HTML
        self._extract_config_from_html(html_content)
        
        # Extraer estilos del HTML  
        self._extract_styles_from_html(html_content)
        
        # Extraer páginas del HTML
        pages = self._extract_pages_from_html(html_content)
        
        # Convertir páginas a elementos Platypus
        story_elements = self._convert_pages_to_story(pages)
        
        # Generar PDF
        return self._generate_pdf(story_elements)
    
    def _extract_config_from_html(self, html_content):
        """Extrae configuración del documento desde HTML"""
        config_match = re.search(r'<document_config>(.*?)</document_config>', html_content, re.DOTALL)
        if config_match:
            config_content = config_match.group(1)
            
            # Extraer valores de configuración
            self.document_config = {
                'title': self._extract_tag_value(config_content, 'title'),
                'header_text': self._extract_tag_value(config_content, 'header_text'),
                'contact_info': self._extract_tag_value(config_content, 'contact_info'),
                'tagline': self._extract_tag_value(config_content, 'tagline'),
                'show_header_on_cover': self._extract_tag_value(config_content, 'show_header_on_cover') == 'true'
            }
    
    def _extract_styles_from_html(self, html_content):
        """Extrae estilos CSS del HTML"""
        styles_match = re.search(r'<pdf_styles>(.*?)</pdf_styles>', html_content, re.DOTALL)
        if styles_match:
            styles_content = styles_match.group(1)
            
            # Extraer colores
            colors_match = re.search(r'<colors>(.*?)</colors>', styles_content, re.DOTALL)
            if colors_match:
                colors_content = colors_match.group(1)
                color_tags = re.findall(r'<(\w+)>(#[0-9a-fA-F]{6})</(\w+)>', colors_content)
                for color_name, hex_value, _ in color_tags:
                    self.colors_map[color_name] = self._hex_to_color(hex_value)
            
            # Extraer configuración de página
            page_match = re.search(r'<page_settings>(.*?)</page_settings>', styles_content, re.DOTALL)
            if page_match:
                page_content = page_match.group(1)
                margins_match = re.search(r'<margins\s+top="(\d+)"\s+bottom="(\d+)"\s+left="(\d+)"\s+right="(\d+)"></margins>', page_content)
                if margins_match:
                    self.page_settings = {
                        'top': int(margins_match.group(1)),
                        'bottom': int(margins_match.group(2)),
                        'left': int(margins_match.group(3)),
                        'right': int(margins_match.group(4))
                    }
    
    def _extract_pages_from_html(self, html_content):
        """Extrae páginas individuales del HTML"""
        # Buscar todas las páginas
        page_pattern = r'<page[^>]*id="([^"]*)"[^>]*>(.*?)</page>'
        pages = re.findall(page_pattern, html_content, re.DOTALL)
        
        return [(page_id, content.strip()) for page_id, content in pages]
    
    def _convert_pages_to_story(self, pages):
        """Convierte páginas HTML a elementos Platypus"""
        story = []
        
        for i, (page_id, page_content) in enumerate(pages):
            # Procesar contenido de la página
            page_elements = self._parse_page_content(page_content)
            story.extend(page_elements)
            
            # Agregar page break excepto en la última página
            if i < len(pages) - 1:
                story.append(PageBreak())
        
        return story
    
    def _parse_page_content(self, content):
        """Parsea el contenido de una página"""
        elements = []
        
        # Split por líneas y procesar
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        for line in lines:
            element = self._parse_html_line(line)
            if element:
                elements.append(element)
        
        return elements
    
    def _parse_html_line(self, line):
        """Parsea una línea HTML individual"""
        # Spacer
        spacer_match = re.match(r'<spacer\s+height="(\d+)"></spacer>', line)
        if spacer_match:
            height = int(spacer_match.group(1))
            return Spacer(1, height)
        
        # Imagen placeholder
        img_match = re.match(r'<img\s+placeholder="([^"]*)"[^>]*></img>', line)
        if img_match:
            placeholder = img_match.group(1)
            return Paragraph(f"<i>[{placeholder}]</i>", self._get_style('p'))
        
        # Título H1
        h1_match = re.match(r'<h1[^>]*>(.*?)</h1>', line)
        if h1_match:
            text = h1_match.group(1)
            return Paragraph(text, self._get_style('h1'))
        
        # Título H2
        h2_match = re.match(r'<h2[^>]*>(.*?)</h2>', line)
        if h2_match:
            text = h2_match.group(1)
            return Paragraph(text, self._get_style('h2'))
        
        # Título H3
        h3_match = re.match(r'<h3[^>]*>(.*?)</h3>', line)
        if h3_match:
            text = h3_match.group(1)
            return Paragraph(text, self._get_style('h3'))
        
        # Párrafo con clase
        p_class_match = re.match(r'<p\s+class="([^"]*)"[^>]*>(.*?)</p>', line)
        if p_class_match:
            class_name = p_class_match.group(1)
            text = p_class_match.group(2)
            return Paragraph(text, self._get_style(f'p.{class_name}'))
        
        # Párrafo normal
        p_match = re.match(r'<p[^>]*>(.*?)</p>', line)
        if p_match:
            text = p_match.group(1)
            return Paragraph(text, self._get_style('p'))
        
        # Lista item
        li_match = re.match(r'<li[^>]*>(.*?)</li>', line)
        if li_match:
            text = li_match.group(1)
            return Paragraph(f"• {text}", self._get_style('li'))
        
        # Tabla simple
        table_match = re.match(r'<table[^>]*id="([^"]*)"[^>]*>', line)
        if table_match:
            # Por ahora retornamos None, las tablas se procesan aparte
            return None
        
        return None
    
    def _get_style(self, tag_name):
        """Obtiene estilo ReportLab para un tag HTML"""
        base_styles = getSampleStyleSheet()
        
        # Estilos por defecto
        style_map = {
            'h1': ParagraphStyle(
                'H1Custom',
                parent=base_styles['Normal'],
                fontSize=24,
                spaceAfter=30,
                alignment=TA_CENTER,
                textColor=self.colors_map.get('primary', colors.black),
                fontName='Helvetica-Bold'
            ),
            'h2': ParagraphStyle(
                'H2Custom',
                parent=base_styles['Normal'],
                fontSize=18,
                spaceAfter=15,
                spaceBefore=25,
                textColor=self.colors_map.get('primary', colors.black),
                fontName='Helvetica-Bold'
            ),
            'h3': ParagraphStyle(
                'H3Custom',
                parent=base_styles['Normal'],
                fontSize=14,
                spaceAfter=20,
                alignment=TA_CENTER,
                textColor=self.colors_map.get('primary_light', colors.black),
                fontName='Helvetica'
            ),
            'p': ParagraphStyle(
                'PCustom',
                parent=base_styles['Normal'],
                fontSize=11,
                spaceAfter=8,
                textColor=self.colors_map.get('black', colors.black),
                fontName='Helvetica'
            ),
            'p.critical': ParagraphStyle(
                'PCriticalCustom',
                parent=base_styles['Normal'],
                fontSize=12,
                spaceAfter=10,
                textColor=self.colors_map.get('critical', colors.red),
                fontName='Helvetica-Bold'
            ),
            'p.stat': ParagraphStyle(
                'PStatCustom',
                parent=base_styles['Normal'],
                fontSize=11,
                spaceAfter=8,
                textColor=self.colors_map.get('primary', colors.black),
                fontName='Helvetica'
            ),
            'li': ParagraphStyle(
                'LiCustom',
                parent=base_styles['Normal'],
                fontSize=11,
                spaceAfter=4,
                textColor=self.colors_map.get('black', colors.black),
                fontName='Helvetica'
            )
        }
        
        return style_map.get(tag_name, style_map['p'])
    
    def _generate_pdf(self, story_elements):
        """Genera el PDF final"""
        buffer = BytesIO()
        
        # Usar configuración de página desde HTML
        margins = self.page_settings
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=margins.get('right', 50),
            leftMargin=margins.get('left', 50),
            topMargin=margins.get('top', 100),
            bottomMargin=margins.get('bottom', 80)
        )
        
        # Construir PDF
        doc.build(
            story_elements,
            onFirstPage=self._first_page_template,
            onLaterPages=self._later_page_template
        )
        
        buffer.seek(0)
        return buffer
    
    def _first_page_template(self, canvas_obj, doc):
        """Template para primera página"""
        if self.document_config.get('show_header_on_cover', False):
            self._draw_header(canvas_obj)
        self._draw_footer(canvas_obj)
    
    def _later_page_template(self, canvas_obj, doc):
        """Template para páginas posteriores"""
        self._draw_header(canvas_obj)
        self._draw_footer(canvas_obj)
    
    def _draw_header(self, canvas_obj):
        """Dibuja header desde configuración HTML"""
        canvas_obj.saveState()
        canvas_obj.setFont("Helvetica-Bold", 14)
        canvas_obj.setFillColor(self.colors_map.get('primary', colors.black))
        header_text = self.document_config.get('header_text', 'DOCUMENT HEADER')
        canvas_obj.drawString(50, letter[1] - 60, header_text)
        canvas_obj.restoreState()
    
    def _draw_footer(self, canvas_obj):
        """Dibuja footer desde configuración HTML"""
        canvas_obj.saveState()
        
        # Línea separadora
        canvas_obj.setStrokeColor(self.colors_map.get('primary_light', colors.blue))
        canvas_obj.setLineWidth(1)
        canvas_obj.line(50, 50, letter[0] - 50, 50)
        
        # Texto del footer
        canvas_obj.setFont("Helvetica", 8)
        canvas_obj.setFillColor(colors.gray)
        
        # Información de contacto
        contact_info = self.document_config.get('contact_info', 'Contact information')
        canvas_obj.drawString(50, 35, contact_info)
        
        # Tagline
        tagline = self.document_config.get('tagline', 'Document tagline')
        tagline_width = canvas_obj.stringWidth(tagline, "Helvetica", 8)
        canvas_obj.drawString(letter[0] - 50 - tagline_width, 35, tagline)
        
        # Número de página
        page_num = f"Página {canvas_obj.getPageNumber()}"
        page_width = canvas_obj.stringWidth(page_num, "Helvetica", 8)
        canvas_obj.drawString(letter[0] / 2 - page_width / 2, 20, page_num)
        
        canvas_obj.restoreState()
    
    # Helper methods
    def _extract_tag_value(self, content, tag_name):
        """Extrae valor de un tag HTML"""
        pattern = f'<{tag_name}>(.*?)</{tag_name}>'
        match = re.search(pattern, content, re.DOTALL)
        return match.group(1).strip() if match else ''
    
    def _hex_to_color(self, hex_value):
        """Convierte hex a Color de ReportLab"""
        hex_value = hex_value.lstrip('#')
        r = int(hex_value[0:2], 16) / 255
        g = int(hex_value[2:4], 16) / 255
        b = int(hex_value[4:6], 16) / 255
        return colors.Color(r, g, b)


class SecurityReportGenerator:
    """Generador minimalista para reportes de seguridad"""
    
    def __init__(self, score_result):
        self.score_result = score_result
        self.submission = score_result.submission
        self.prospect = self.submission.prospect
        self.survey = self.submission.survey
        self.parser = HTMLToPDFParser()
        
    def generate_report(self):
        """
        Genera reporte desde HTML template
        
        Returns:
            BytesIO buffer con PDF
        """
        # Preparar contexto para template
        context = self._prepare_context()
        
        # Renderizar template HTML completo
        html_content = render_to_string('reports/security_assessment.html', context)
        
        # Convertir HTML a PDF
        return self.parser.parse_html_to_pdf(html_content)
    
    def _prepare_context(self):
        """Prepara contexto para el template"""
        from .security_content_data import SecurityContentData
        
        content_data = SecurityContentData()
        
        # Información básica
        company_name = self.prospect.company_name or f"{self.prospect.name.split()[0].upper()} EMPRESA"
        fecha_actual = self._format_date()
        risk_level_display = self._get_risk_level_display()
        
        return {
            # Datos del score
            'score_result': self.score_result,
            'prospect': self.prospect,
            'company_name': company_name,
            'fecha_actual': fecha_actual,
            'risk_level_display': risk_level_display,
            
            # Contenido dinámico
            'risk_content': content_data.get_risk_level_content(self.score_result.risk_level),
            'global_stats': content_data.get_global_statistics(),
            'vulnerabilities': content_data.get_vulnerabilities_for_score(self.score_result.risk_level),
            'recommended_package': content_data.get_recommended_package_details(self.score_result.primary_package),
            'other_packages': content_data.get_other_packages_summary(self.score_result.primary_package),
            'value_props': content_data.get_value_propositions(),
            'session_items': content_data.get_session_items(),
            'contact_info': content_data.get_contact_info(),
            'references': content_data.get_references(),
        }
    
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