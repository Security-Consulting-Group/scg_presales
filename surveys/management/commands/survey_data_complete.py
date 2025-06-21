"""
DATOS COMPLETOS DEL SURVEY - SCG DIAGNÓSTICO EJECUTIVO DE CIBERSEGURIDAD
Ubicación: surveys/management/commands/survey_data_complete.py
"""

SURVEY_DATA = {
    "survey": {
        "title": "Diagnóstico Ejecutivo de Ciberseguridad",
        "description": "Cuestionario de 14 preguntas para evaluar la postura de ciberseguridad de empresas PYME",
        "version": "1.0",
        "max_score": 100,
        "created_by": "SCG Team"
    },
    
    "sections": [
        {
            "title": "Contexto de Negocio",
            "description": "Información básica sobre la empresa y su perfil de riesgo",
            "order": 1,
            "max_points": 15
        },
        {
            "title": "Gestión de Accesos y Autenticación", 
            "description": "Control de acceso a sistemas críticos",
            "order": 2,
            "max_points": 35
        },
        {
            "title": "Protección de Infraestructura",
            "description": "Seguridad de sistemas y datos",
            "order": 3,
            "max_points": 25
        },
        {
            "title": "Gestión de Riesgos y Respuesta",
            "description": "Preparación y respuesta ante incidentes",
            "order": 4,
            "max_points": 25
        },
        {
            "title": "Objetivos y Prioridades",
            "description": "Necesidades y urgencia del cliente",
            "order": 5,
            "max_points": 0  # No suma puntos, solo para segmentación
        }
    ],
    
    "questions": [
        # SECCIÓN A: Contexto de Negocio (15 puntos)
        {
            "section": 1,
            "order": 1,
            "question_text": "¿En qué sector opera su empresa?",
            "question_type": "SINGLE_CHOICE",
            "is_required": True,
            "max_points": 5,
            "options": [
                {"text": "Servicios financieros", "order": 1, "points": 1},
                {"text": "Retail/E-commerce", "order": 2, "points": 3},
                {"text": "Manufactura", "order": 3, "points": 4},
                {"text": "Servicios de salud", "order": 4, "points": 2},
                {"text": "Logística y transporte", "order": 5, "points": 4},
                {"text": "Tecnología", "order": 6, "points": 3},
                {"text": "Otros", "order": 7, "points": 4}
            ]
        },
        {
            "section": 1,
            "order": 2,
            "question_text": "¿Cuántos empleados tiene su organización?",
            "question_type": "SINGLE_CHOICE",
            "is_required": True,
            "max_points": 5,
            "options": [
                {"text": "10-50 empleados", "order": 1, "points": 5},
                {"text": "51-200 empleados", "order": 2, "points": 4},
                {"text": "201-500 empleados", "order": 3, "points": 3},
                {"text": "Más de 500 empleados", "order": 4, "points": 2}
            ]
        },
        {
            "section": 1,
            "order": 3,
            "question_text": "¿Su empresa maneja información sensible de clientes? (Seleccione todas las que apliquen)",
            "question_type": "MULTIPLE_CHOICE",
            "is_required": True,
            "max_points": 5,
            "options": [
                {"text": "Datos financieros/tarjetas de crédito", "order": 1, "points": -1},
                {"text": "Información personal", "order": 2, "points": -1},
                {"text": "Información médica o de salud", "order": 3, "points": -1},
                {"text": "Propiedad intelectual crítica", "order": 4, "points": -1},
                {"text": "No manejamos información sensible", "order": 5, "points": 5}
            ]
        },
        
        # SECCIÓN B: Gestión de Accesos (35 puntos)
        {
            "section": 2,
            "order": 4,
            "question_text": "¿Cómo controlan el acceso a sus sistemas más importantes?",
            "question_type": "SINGLE_CHOICE",
            "is_required": True,
            "max_points": 15,
            "options": [
                {"text": "Autenticación multifactor (MFA) en todos los sistemas críticos", "order": 1, "points": 15},
                {"text": "Contraseñas únicas y políticas estrictas", "order": 2, "points": 10},
                {"text": "Contraseñas básicas, algunos sistemas compartidos", "order": 3, "points": 5},
                {"text": "No tenemos políticas claras de acceso", "order": 4, "points": 0}
            ]
        },
        {
            "section": 2,
            "order": 5,
            "question_text": "¿Tienen visibilidad de quién accede a qué información y cuándo?",
            "question_type": "SINGLE_CHOICE",
            "is_required": True,
            "max_points": 10,
            "options": [
                {"text": "Logs completos con revisión y alertas automáticas", "order": 1, "points": 10},
                {"text": "Logs básicos que revisamos ocasionalmente", "order": 2, "points": 6},
                {"text": "Registros limitados en algunos sistemas", "order": 3, "points": 3},
                {"text": "No tenemos visibilidad clara de accesos", "order": 4, "points": 0}
            ]
        },
        {
            "section": 2,
            "order": 6,
            "question_text": "¿Cómo manejan las cuentas cuando empleados dejan la empresa?",
            "question_type": "SINGLE_CHOICE",
            "is_required": True,
            "max_points": 10,
            "options": [
                {"text": "Proceso automatizado de desactivación inmediata", "order": 1, "points": 10},
                {"text": "Proceso manual que ejecutamos el mismo día", "order": 2, "points": 8},
                {"text": "Lo hacemos dentro de unos días", "order": 3, "points": 4},
                {"text": "No tenemos proceso formal establecido", "order": 4, "points": 0}
            ]
        },
        
        # SECCIÓN C: Protección de Infraestructura (25 puntos)
        {
            "section": 3,
            "order": 7,
            "question_text": "¿Qué tan conectados están sus sistemas críticos a internet?",
            "question_type": "SINGLE_CHOICE",
            "is_required": True,
            "max_points": 8,
            "options": [
                {"text": "Completamente en la nube con protecciones avanzadas", "order": 1, "points": 8},
                {"text": "Híbrido (local y nube) con firewall corporativo", "order": 2, "points": 6},
                {"text": "Principalmente local con acceso remoto básico", "order": 3, "points": 4},
                {"text": "Sistemas aislados/sin conexión externa", "order": 4, "points": 8}
            ]
        },
        {
            "section": 3,
            "order": 8,
            "question_text": "¿Con qué frecuencia actualizan y parchean sus sistemas?",
            "question_type": "SINGLE_CHOICE",
            "is_required": True,
            "max_points": 9,
            "options": [
                {"text": "Proceso automatizado con pruebas regulares", "order": 1, "points": 9},
                {"text": "Proceso manual planificado mensualmente", "order": 2, "points": 6},
                {"text": "Cuando es posible o hay tiempo", "order": 3, "points": 3},
                {"text": "Solo cuando surgen problemas críticos", "order": 4, "points": 0}
            ]
        },
        {
            "section": 3,
            "order": 9,
            "question_text": "¿Tienen respaldos de su información crítica?",
            "question_type": "SINGLE_CHOICE",
            "is_required": True,
            "max_points": 8,
            "options": [
                {"text": "Respaldos automatizados, probados regularmente", "order": 1, "points": 8},
                {"text": "Respaldos automáticos, pero no los hemos probado", "order": 2, "points": 5},
                {"text": "Respaldos manuales ocasionales", "order": 3, "points": 2},
                {"text": "No tenemos sistema formal de respaldos", "order": 4, "points": 0}
            ]
        },
        
        # SECCIÓN D: Gestión de Riesgos (25 puntos)
        {
            "section": 4,
            "order": 10,
            "question_text": "¿Ha experimentado algún incidente de ciberseguridad en los últimos 2 años?",
            "question_type": "SINGLE_CHOICE",
            "is_required": True,
            "max_points": 8,
            "options": [
                {"text": "No, ningún incidente que conozcamos", "order": 1, "points": 8},
                {"text": "No estoy seguro si hubo incidentes", "order": 2, "points": 4},
                {"text": "Sí, incidentes menores (emails maliciosos, intentos de acceso)", "order": 3, "points": 2},
                {"text": "Sí, un incidente mayor que afectó operaciones", "order": 4, "points": 0}
            ]
        },
        {
            "section": 4,
            "order": 11,
            "question_text": "¿Tienen un plan documentado para responder a incidentes de ciberseguridad?",
            "question_type": "SINGLE_CHOICE",
            "is_required": True,
            "max_points": 9,
            "options": [
                {"text": "Plan completo, probado y actualizado", "order": 1, "points": 9},
                {"text": "Plan documentado pero no probado", "order": 2, "points": 6},
                {"text": "Plan básico o procedimientos informales", "order": 3, "points": 3},
                {"text": "No tenemos plan de respuesta", "order": 4, "points": 0}
            ]
        },
        {
            "section": 4,
            "order": 12,
            "question_text": "¿Con qué frecuencia capacitan a sus empleados en ciberseguridad?",
            "question_type": "SINGLE_CHOICE",
            "is_required": True,
            "max_points": 8,
            "options": [
                {"text": "Capacitación regular con pruebas de phishing", "order": 1, "points": 8},
                {"text": "Capacitación anual obligatoria", "order": 2, "points": 5},
                {"text": "Solo orientación para nuevos empleados", "order": 3, "points": 2},
                {"text": "No brindamos capacitación específica", "order": 4, "points": 0}
            ]
        },
        
        # SECCIÓN E: Objetivos y Prioridades (0 puntos - solo segmentación)
        {
            "section": 5,
            "order": 13,
            "question_text": "¿Cuál es su principal preocupación respecto a ciberseguridad? (Seleccione la más importante)",
            "question_type": "SINGLE_CHOICE",
            "is_required": True,
            "max_points": 0,
            "options": [
                {"text": "Pérdida o robo de datos de clientes", "order": 1, "points": 0},
                {"text": "Interrupción prolongada de operaciones", "order": 2, "points": 0},
                {"text": "Daño a la reputación de la empresa", "order": 3, "points": 0},
                {"text": "Multas o problemas con reguladores", "order": 4, "points": 0},
                {"text": "Pérdida de propiedad intelectual", "order": 5, "points": 0}
            ]
        },
        {
            "section": 5,
            "order": 14,
            "question_text": "¿En qué plazo necesita fortalecer su postura de ciberseguridad?",
            "question_type": "SINGLE_CHOICE",
            "is_required": True,
            "max_points": 0,
            "options": [
                {"text": "Lo antes posible (no estoy seguro de nuestra situación actual)", "order": 1, "points": 0},
                {"text": "En los próximos 3 meses", "order": 2, "points": 0},
                {"text": "En los próximos 6-12 meses", "order": 3, "points": 0},
                {"text": "Es una mejora planificada a largo plazo", "order": 4, "points": 0}
            ]
        }
    ]
}

# SCORING LOGIC PARA PREGUNTA 3 (MULTIPLE CHOICE)
QUESTION_3_SCORING = {
    "logic": "Count selected sensitive data types, then award points inversely",
    "calculation": {
        0: 5,  # No sensitive data = 5 points
        1: 4,  # 1 type = 4 points  
        2: 3,  # 2 types = 3 points
        3: 2,  # 3 types = 2 points
        4: 1   # 4+ types = 1 point
    }
}

# RISK LEVELS Y PACKAGES
SCORING_INTERPRETATION = {
    "risk_levels": {
        "CRITICAL": {"min": 0, "max": 20, "label": "Estado Crítico"},
        "HIGH": {"min": 21, "max": 40, "label": "Riesgos Significativos"},
        "MODERATE": {"min": 41, "max": 60, "label": "Vulnerabilidades Moderadas"},
        "GOOD": {"min": 61, "max": 80, "label": "Buena Base"},
        "EXCELLENT": {"min": 81, "max": 100, "label": "Postura Sólida"}
    },
    
    "recommended_packages": {
        "0-20": "PROTECCION_ESENCIAL",
        "21-40": "PROTECCION_ESENCIAL", 
        "41-60": "SEGURIDAD_PROACTIVA",
        "61-80": "SEGURIDAD_PROACTIVA",
        "81-100": "DEFENSA_INTEGRAL"
    },
    
    "urgency_levels": {
        "0-20": "CRITICAL",
        "21-40": "HIGH", 
        "41-60": "MEDIUM",
        "61-100": "LOW"
    }
}

# EXAMPLE MANAGEMENT COMMAND USAGE:
"""
python manage.py load_survey_data --settings=core.settings.development

Este comando debe:
1. Crear el Survey principal
2. Crear las 5 secciones 
3. Crear las 14 preguntas con sus opciones
4. Configurar el scoring según los puntos especificados
5. Manejar la lógica especial de la pregunta 3 (multiple choice)
"""