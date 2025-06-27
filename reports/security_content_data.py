"""
reports/security_content_data.py
Contenido de texto separado para reportes de ciberseguridad
"""

class SecurityContentData:
    """Datos de contenido para reportes de seguridad"""
    
    @staticmethod
    def get_risk_level_content(risk_level):
        """Retorna contenido personalizado según el nivel de riesgo"""
        
        if risk_level == 'CRITICAL':
            return {
                'title': '¡ACCIÓN INMEDIATA REQUERIDA!',
                'description': 'Su empresa está en riesgo extremo. Las vulnerabilidades detectadas la colocan en el 43% de PYMEs que son blanco frecuente de ciberataques. La falta de controles básicos de seguridad expone datos críticos y operaciones comerciales a amenazas inmediatas.',
                'threats_title': 'AMENAZAS INMINENTES IDENTIFICADAS:',
                'threats': [
                    'Ataques de ransomware que pueden paralizar completamente sus operaciones por días o semanas, causando pérdidas de ingresos directas',
                    'Acceso no autorizado por credenciales comprometidas, permitiendo robo de datos financieros y personales de clientes',
                    'Pérdida masiva de datos por controles de seguridad inexistentes, resultando en multas regulatorias y pérdida de confianza',
                    'Interceptación de comunicaciones por cifrado débil, exponiendo información comercial sensible a competidores',
                    'Inyección de código malicioso en aplicaciones web que compromete toda la infraestructura digital',
                    'Exfiltración de propiedad intelectual y secretos comerciales por actores maliciosos',
                    'Compromiso de sistemas financieros y transferencias no autorizadas'
                ],
                'statistic': 'ESTADÍSTICA ALARMANTE: "El 60% de las PYMEs que sufren un ciberataque cierran definitivamente en los siguientes 6 meses" (Kaspersky Lab, 2023). Su empresa NO puede permitirse formar parte de esta estadística. Adicionalmente, el costo promedio de recuperación para empresas sin preparación es de $4.88 millones USD, muy superior a los ingresos anuales de la mayoría de PYMEs.'
            }
        
        elif risk_level == 'HIGH':
            return {
                'title': 'VULNERABILIDADES SIGNIFICATIVAS DETECTADAS',
                'description': 'Su empresa presenta brechas importantes que la exponen a amenazas del 43% de ataques dirigidos contra PYMEs. Si bien existen algunos controles de seguridad, las deficiencias identificadas pueden ser explotadas por atacantes con motivaciones financieras.',
                'threats_title': 'RIESGOS CRÍTICOS IDENTIFICADOS:',
                'threats': [
                    'Ataques de phishing dirigidos aprovechando controles de acceso débiles, resultando en compromiso de cuentas ejecutivas',
                    'Explotación de vulnerabilidades en software desactualizado, creando puertas traseras para acceso persistente',
                    'Configuraciones inseguras que facilitan el movimiento lateral de atacantes dentro de la red corporativa',
                    'Fallas en autenticación que permiten suplantación de identidad y acceso a sistemas críticos',
                    'Exposición de datos sensibles por monitoreo inadecuado, incluyendo información de clientes y proveedores',
                    'Ataques de ingeniería social dirigidos a empleados con acceso privilegiado',
                    'Compromiso de sistemas de respaldo, impidiendo la recuperación efectiva ante incidentes'
                ],
                'statistic': 'REALIDAD PREOCUPANTE: "Las empresas con este perfil de vulnerabilidades tienen 3.2 veces más probabilidad de sufrir una brecha en los próximos 12 meses" (IBM Security, 2024). El tiempo promedio para detectar y contener una brecha es de 277 días, período durante el cual los atacantes tienen acceso completo a sistemas y datos críticos.'
            }
        
        elif risk_level == 'MODERATE':
            return {
                'title': 'FUNDAMENTOS SÓLIDOS CON OPORTUNIDADES CRÍTICAS',
                'description': 'Su empresa demuestra conciencia sobre ciberseguridad, pero aún presenta vulnerabilidades que pueden ser explotadas por atacantes persistentes. Los controles actuales proporcionan protección básica, pero no son suficientes contra amenazas modernas y sofisticadas.',
                'threats_title': 'ÁREAS QUE REQUIEREN ATENCIÓN:',
                'threats': [
                    'Ataques automatizados contra configuraciones por defecto, aprovechando servicios no endurecidos',
                    'Compromiso de cuentas por políticas de contraseñas insuficientes y falta de autenticación multifactor',
                    'Validación inadecuada de datos que permite inyecciones SQL y cross-site scripting en aplicaciones web',
                    'Fallas en integridad de software que exponen la cadena de suministro a compromiso de terceros',
                    'Monitoreo insuficiente que retrasa la detección de incidentes, permitiendo daños extensos',
                    'Configuraciones de red que facilitan la propagación lateral de malware',
                    'Gestión inadecuada de privilegios que otorga acceso excesivo a usuarios regulares'
                ],
                'statistic': 'VENTAJA COMPETITIVA: "Está mejor posicionado que el 60% de empresas similares, pero el costo promedio de una brecha sigue siendo $4.88 millones USD" (IBM Cost of Data Breach 2024). La mejora continua es la diferencia entre ser víctima o estar protegido. Las empresas que invierten en seguridad proactiva reducen los costos de incidentes en un 80%.'
            }
        
        elif risk_level in ['GOOD', 'EXCELLENT']:
            return {
                'title': '¡EXCELENTE POSTURA DE SEGURIDAD!',
                'description': 'Su empresa forma parte del selecto grupo que toma la ciberseguridad en serio. Sin embargo, las amenazas evolucionan constantemente y los atacantes desarrollan técnicas más sofisticadas. Mantener esta posición requiere vigilancia y actualización continua de controles.',
                'threats_title': 'AMENAZAS EMERGENTES A CONSIDERAR:',
                'threats': [
                    'Ataques sofisticados de APT (Amenazas Persistentes Avanzadas) patrocinados por estados y grupos criminales organizados',
                    'Zero-day exploits en aplicaciones críticas que evaden sistemas de detección tradicionales',
                    'Ataques de cadena de suministro digital dirigidos a proveedores y partners tecnológicos',
                    'Técnicas avanzadas de evasión y ofuscación que burlan sistemas de seguridad existentes',
                    'Ataques basados en inteligencia artificial que personalizan técnicas de ingeniería social',
                    'Compromisos de infraestructura cloud y servicios en la nube mal configurados',
                    'Ataques híbridos que combinan vectores físicos y digitales para evadir defensas perimetrales'
                ],
                'statistic': 'MANTENER LA EXCELENCIA: "Las empresas que realizan evaluaciones continuas de seguridad reducen el tiempo de detección de incidentes de 287 a 204 días" (IBM Security, 2024). Su inversión en seguridad debe ser continua para mantener esta ventaja. Las organizaciones líderes en seguridad experimentan 95% menos incidentes críticos que empresas reactivas.'
            }
        
        # Fallback
        return {
            'title': 'EVALUACIÓN DE CIBERSEGURIDAD COMPLETADA',
            'description': 'Su empresa ha sido evaluada según estándares internacionales de ciberseguridad. Los resultados indican oportunidades específicas para fortalecer su postura de seguridad.',
            'threats_title': 'ÁREAS DE ATENCIÓN IDENTIFICADAS:',
            'threats': [
                'Oportunidades de mejora en controles de seguridad que requieren atención prioritaria',
                'Fortalecimiento de procesos y procedimientos de respuesta a incidentes',
                'Capacitación especializada del equipo humano en reconocimiento de amenazas',
                'Optimización de la infraestructura tecnológica para resiliencia operacional'
            ],
            'statistic': 'La ciberseguridad es un proceso continuo que requiere atención constante y mejora permanente. Las empresas que adoptan un enfoque proactivo experimentan 58% menos interrupciones operacionales.'
        }
    

    
    @staticmethod
    def get_vulnerabilities_for_score(risk_level):
        """Vulnerabilidades según el nivel de riesgo"""
        base_vulns = [
            {
                'level': 'CRÍTICO',
                'title': 'GESTIÓN DE ACCESOS Y CREDENCIALES',
                'description': 'Su organización presenta exposición en la autenticación y control de accesos. Las credenciales débiles son la puerta de entrada preferida del 89% de atacantes.',
                'impact': 'Acceso no autorizado a sistemas críticos, manipulación de datos financieros, y exposición de información estratégica de la empresa.',
                'recommendations': [
                    'Implementar autenticación multifactor (MFA) en todos los sistemas críticos',
                    'Establecer políticas robustas de contraseñas con renovación periódica',
                    'Realizar auditorías regulares de permisos y accesos de usuario',
                    'Implementar gestión centralizada de identidades y accesos (IAM)'
                ]
            },
            {
                'level': 'ALTO',
                'title': 'CULTURA Y CAPACITACIÓN EN SEGURIDAD',
                'description': 'El factor humano representa el 95% de brechas exitosas. Detectamos oportunidades de fortalecimiento en la conciencia de seguridad de su equipo.',
                'impact': 'Susceptibilidad a ataques de ingeniería social, pérdida de información confidencial, y potencial paralización operativa.',
                'recommendations': [
                    'Implementar programa de capacitación continua en ciberseguridad',
                    'Realizar simulacros de phishing para evaluar y mejorar la respuesta del equipo',
                    'Establecer políticas claras de uso aceptable de tecnología',
                    'Crear programa de recompensas por reporte de incidentes de seguridad'
                ]
            }
        ]
        
        if risk_level in ['CRITICAL', 'HIGH']:
            base_vulns.append({
                'level': 'MEDIO',
                'title': 'CONTINUIDAD DE NEGOCIO Y RECUPERACIÓN',
                'description': 'Sus procesos de contingencia y recuperación ante incidentes requieren optimización para garantizar continuidad operativa.',
                'impact': 'Tiempo de inactividad prolongado, pérdida de ingresos, y daño reputacional ante clientes e inversionistas.',
                'recommendations': [
                    'Desarrollar y documentar plan de continuidad de negocio (BCP)',
                    'Implementar soluciones de respaldo automatizado y recuperación de desastres',
                    'Realizar pruebas regulares de recuperación y restauración',
                    'Establecer acuerdos de nivel de servicio (SLA) para recuperación crítica'
                ]
            })
        
        return base_vulns
    
    @staticmethod
    def get_recommended_package_details(primary_package):
        """Detalles del paquete recomendado según el score"""
        if primary_package == 'SEGURIDAD_PROACTIVA':
            return {
                'name': 'SEGURIDAD PROACTIVA',
                'subtitle': '"Liderazgo en Ciberseguridad para Empresas Visionarias"',
                'price': '$2,500/mes',
                'billing_period': 'Facturación mensual',
                'features': [
                    'Evaluaciones profesionales de vulnerabilidades (4 veces al año)',
                    'Simulación de ataques reales (penetration testing)',
                    'Arquitectura de recuperación ante desastres (DRP/BCP)',
                    'Marco de políticas corporativas alineadas con estándares internacionales',
                    'Capacitación intensiva (4 sesiones anuales)',
                    'Soporte prioritario 24 horas'
                ],
                'benefits': [
                    'Reducción del 70% en tiempo de detección de amenazas',
                    'Cumplimiento con estándares internacionales (ISO 27001, NIST)',
                    'ROI comprobado del 300% en el primer año',
                    'Reducción de riesgos operacionales críticos'
                ],
                'ideal': 'Su nivel actual de riesgo requiere acción proactiva inmediata'
            }
        
        elif primary_package == 'DEFENSA_INTEGRAL':
            return {
                'name': 'DEFENSA INTEGRAL',
                'subtitle': '"Excelencia Operativa en Ciberseguridad de Clase Mundial"',
                'price': '$3,500/mes',
                'billing_period': 'Facturación mensual',
                'features': [
                    'Monitoreo continuo 24/7 con detección en tiempo real',
                    'Centro de operaciones de seguridad (SOC) dedicado',
                    'Respuesta inmediata ante incidentes (SLA de 3 horas)',
                    'Evaluaciones continuas de cumplimiento',
                    'Consultoría estratégica para transformación digital segura',
                    'Soporte premium especializado'
                ],
                'benefits': [
                    'Detección de amenazas en tiempo real',
                    'Respuesta automática ante incidentes',
                    'Cumplimiento garantizado con regulaciones',
                    'Ventaja competitiva en seguridad digital'
                ],
                'ideal': 'Organizaciones que requieren estándares de seguridad de clase mundial'
            }
        
        else:  # PROTECCION_ESENCIAL o default
            return {
                'name': 'PROTECCIÓN ESENCIAL',
                'subtitle': '"Fundamentos Sólidos para Crecimiento Seguro"',
                'price': '$1,000/mes',
                'billing_period': 'Facturación mensual',
                'features': [
                    'Evaluaciones profesionales de vulnerabilidades (2 veces al año)',
                    'Reportes ejecutivos trimestrales para toma de decisiones',
                    'Capacitación especializada del equipo humano',
                    'Asesoría estratégica mensual personalizada',
                    'Soporte técnico especializado'
                ],
                'benefits': [
                    'Base sólida de seguridad para crecimiento',
                    'Reducción significativa de riesgos operacionales',
                    'Equipo humano capacitado y consciente',
                    'Inversión escalable según crecimiento'
                ],
                'ideal': 'Empresas que inician su journey de ciberseguridad con bases sólidas'
            }
    
    @staticmethod
    def get_other_packages_summary(current_package):
        """Resumen de otros paquetes disponibles"""
        all_packages = [
            {
                'name': 'Protección Esencial ($1,000/mes)',
                'description': 'Fundamentos sólidos para empresas que inician en ciberseguridad'
            },
            {
                'name': 'Seguridad Proactiva ($2,500/mes)',
                'description': 'Liderazgo proactivo con pruebas de penetración y DRP/BCP'
            },
            {
                'name': 'Defensa Integral ($3,500/mes)',
                'description': 'Excelencia operativa con monitoreo 24/7 y SOC dedicado'
            }
        ]
        
        # Filtrar el paquete actual
        current_name = current_package.replace('_', ' ').title()
        return [pkg for pkg in all_packages if not pkg['name'].startswith(current_name)]
    
    @staticmethod
    def get_session_items():
        """Items de la sesión ejecutiva"""
        return [
            "✓ Implementación inmediata de controles críticos",
            "✓ Hoja de ruta personalizada para su sector",
            "✓ ROI proyectado y métricas de éxito",
            "✓ Timeline de implementación sin interrumpir operaciones"
        ]
    
    @staticmethod
    def get_contact_info():
        """Información de contacto"""
        return {
            'phone': '+506 1234-5678',
            'email': 'services@securitygroupcr.com',
            'website': 'www.securitygroupcr.com',
            'address': 'San José, Costa Rica',
            'company_description': 'Somos su socio estratégico en ciberseguridad, comprometidos con la protección integral de su empresa ante las amenazas digitales actuales y futuras.',
            'services': [
                'Evaluaciones de vulnerabilidades y penetration testing',
                'Implementación de marcos de seguridad (ISO 27001, NIST)',
                'Monitoreo 24/7 y respuesta ante incidentes',
                'Capacitación especializada en ciberseguridad',
                'Consultoría estratégica para transformación digital segura'
            ],
            'certifications': [
                'Certified Ethical Hacker (CEH)',
                'Certified Information Systems Security Professional (CISSP)',
                'ISO 27001 Lead Auditor',
                'NIST Cybersecurity Framework Certified'
            ]
        }
    
    @staticmethod
    def get_references():
        """Referencias consultadas"""
        return [
            "• IBM Security - Cost of Data Breach Report 2024",
            "• Verizon - Data Breach Investigations Report 2024",
            "• University of Maryland - Cybersecurity Research",
            "• MICITT Costa Rica 2023",
            "• OIJ Costa Rica - Unidad de Delitos Informáticos 2024"
        ]