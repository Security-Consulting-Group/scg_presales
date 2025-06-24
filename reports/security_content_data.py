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
                'description': 'Su empresa está en riesgo extremo. Las vulnerabilidades detectadas la colocan en el 43% de PYMEs que son blanco frecuente de ciberataques.',
                'threats_title': '🚨 AMENAZAS INMINENTES IDENTIFICADAS:',
                'threats': [
                    'Ataques de ransomware que pueden paralizar completamente sus operaciones',
                    'Acceso no autorizado por credenciales comprometidas',
                    'Pérdida masiva de datos por controles de seguridad inexistentes',
                    'Interceptación de comunicaciones por cifrado débil',
                    'Inyección de código malicioso en aplicaciones web'
                ],
                'statistic': '⚠️ ESTADÍSTICA ALARMANTE: "El 60% de las PYMEs que sufren un ciberataque cierran definitivamente en los siguientes 6 meses" (Kaspersky Lab, 2023). Su empresa NO puede permitirse formar parte de esta estadística.'
            }
        
        elif risk_level == 'HIGH':
            return {
                'title': 'VULNERABILIDADES SIGNIFICATIVAS DETECTADAS',
                'description': 'Su empresa presenta brechas importantes que la exponen a amenazas del 43% de ataques dirigidos contra PYMEs.',
                'threats_title': '⚠️ RIESGOS CRÍTICOS IDENTIFICADOS:',
                'threats': [
                    'Ataques de phishing dirigidos aprovechando controles de acceso débiles',
                    'Explotación de vulnerabilidades en software desactualizado',
                    'Configuraciones inseguras que facilitan el acceso lateral',
                    'Fallas en autenticación que permiten suplantación de identidad',
                    'Exposición de datos sensibles por monitoreo inadecuado'
                ],
                'statistic': '📊 REALIDAD PREOCUPANTE: "Las empresas con este perfil de vulnerabilidades tienen 3.2 veces más probabilidad de sufrir una brecha en los próximos 12 meses" (IBM Security, 2024)'
            }
        
        elif risk_level == 'MODERATE':
            return {
                'title': 'FUNDAMENTOS SÓLIDOS CON OPORTUNIDADES CRÍTICAS',
                'description': 'Su empresa demuestra conciencia sobre ciberseguridad, pero aún presenta vulnerabilidades que pueden ser explotadas.',
                'threats_title': '🔍 ÁREAS QUE REQUIEREN ATENCIÓN:',
                'threats': [
                    'Ataques automatizados contra configuraciones por defecto',
                    'Compromiso de cuentas por políticas de contraseñas insuficientes',
                    'Validación inadecuada de datos que permite inyecciones',
                    'Fallas en integridad de software que exponen la cadena de suministro',
                    'Monitoreo insuficiente que retrasa la detección de incidentes'
                ],
                'statistic': '✅ VENTAJA COMPETITIVA: "Está mejor posicionado que el 60% de empresas similares, pero el costo promedio de una brecha sigue siendo $4.45 millones USD" (IBM Cost of Data Breach 2024). La mejora continua es la diferencia entre ser víctima o estar protegido.'
            }
        
        elif risk_level in ['GOOD', 'EXCELLENT']:
            return {
                'title': '¡EXCELENTE POSTURA DE SEGURIDAD!',
                'description': 'Su empresa forma parte del selecto grupo que toma la ciberseguridad en serio. Sin embargo, las amenazas evolucionan constantemente.',
                'threats_title': '🎯 AMENAZAS EMERGENTES A CONSIDERAR:',
                'threats': [
                    'Ataques sofisticados de APT (Amenazas Persistentes Avanzadas)',
                    'Zero-day exploits en aplicaciones críticas',
                    'Ataques de cadena de suministro digital',
                    'Técnicas avanzadas de evasión y ofuscación',
                    'Ataques basados en inteligencia artificial'
                ],
                'statistic': '🚀 MANTENER LA EXCELENCIA: "Las empresas que realizan evaluaciones continuas de seguridad reducen el tiempo de detección de incidentes de 287 a 204 días" (IBM Security, 2024). Su inversión en seguridad debe ser continua para mantener esta ventaja.'
            }
        
        # Fallback
        return {
            'title': 'EVALUACIÓN DE CIBERSEGURIDAD COMPLETADA',
            'description': 'Su empresa ha sido evaluada según estándares internacionales de ciberseguridad.',
            'threats_title': '🔍 ÁREAS DE ATENCIÓN IDENTIFICADAS:',
            'threats': [
                'Oportunidades de mejora en controles de seguridad',
                'Fortalecimiento de procesos y procedimientos',
                'Capacitación del equipo humano',
                'Optimización de la infraestructura tecnológica'
            ],
            'statistic': 'La ciberseguridad es un proceso continuo que requiere atención constante y mejora permanente.'
        }
    
    @staticmethod
    def get_global_statistics():
        """Estadísticas globales de ciberseguridad"""
        return {
            'world': [
                "🔴 Una empresa es atacada cada 39 segundos (University of Maryland)",
                "🔴 43% de los ciberataques se dirigen específicamente a pequeñas empresas (Verizon DBIR 2024)",
                "🔴 4,000 ataques de ransomware ocurren diariamente (FBI, 2024)",
                "🔴 El 95% de las brechas exitosas son causadas por error humano (Cybersecurity Ventures, 2024)"
            ],
            'financial': [
                "💰 Costo promedio global de una brecha de datos: $4.45 millones USD (IBM Security, 2024)",
                "💰 Las PYMEs pierden en promedio $25,700 USD por incidente (Hiscox, 2024)",
                "💰 Tiempo promedio para detectar una brecha: 204 días (IBM Security, 2024)"
            ],
            'costa_rica': [
                "• 85% de empresas costarricenses NO tienen un plan formal de ciberseguridad (MICITT, 2023)",
                "• Solo 23% de PYMEs realizan respaldos regulares de datos (Cámara de TIC, 2023)",
                "• Ataques de ransomware aumentaron 300% en Costa Rica (2022-2024) (OIJ, 2024)"
            ]
        }
    
    @staticmethod
    def get_vulnerabilities_for_score(risk_level):
        """Vulnerabilidades según el nivel de riesgo"""
        base_vulns = [
            {
                'level': '🔴 CRÍTICO',
                'title': 'GESTIÓN DE ACCESOS Y CREDENCIALES',
                'description': 'Su organización presenta exposición en la autenticación y control de accesos. Las credenciales débiles son la puerta de entrada preferida del 89% de atacantes.',
                'impact': 'Acceso no autorizado a sistemas críticos, manipulación de datos financieros, y exposición de información estratégica de la empresa.'
            },
            {
                'level': '🟠 ALTO',
                'title': 'CULTURA Y CAPACITACIÓN EN SEGURIDAD',
                'description': 'El factor humano representa el 95% de brechas exitosas. Detectamos oportunidades de fortalecimiento en la conciencia de seguridad de su equipo.',
                'impact': 'Susceptibilidad a ataques de ingeniería social, pérdida de información confidencial, y potencial paralización operativa.'
            }
        ]
        
        if risk_level in ['CRITICAL', 'HIGH']:
            base_vulns.append({
                'level': '🟡 MEDIO',
                'title': 'CONTINUIDAD DE NEGOCIO Y RECUPERACIÓN',
                'description': 'Sus procesos de contingencia y recuperación ante incidentes requieren optimización para garantizar continuidad operativa.',
                'impact': 'Tiempo de inactividad prolongado, pérdida de ingresos, y daño reputacional ante clientes e inversionistas.'
            })
        
        return base_vulns
    
    @staticmethod
    def get_recommended_package_details(primary_package):
        """Detalles del paquete recomendado según el score"""
        if primary_package == 'SEGURIDAD_PROACTIVA':
            return {
                'name': 'SEGURIDAD PROACTIVA - $2,500/mes',
                'subtitle': '"Liderazgo en Ciberseguridad para Empresas Visionarias"',
                'features': [
                    'Evaluaciones profesionales de vulnerabilidades (4 veces al año)',
                    'Simulación de ataques reales (penetration testing)',
                    'Arquitectura de recuperación ante desastres (DRP/BCP)',
                    'Marco de políticas corporativas alineadas con estándares internacionales',
                    'Capacitación intensiva (4 sesiones anuales)',
                    'Soporte prioritario 24 horas'
                ],
                'ideal': 'Su nivel actual de riesgo requiere acción proactiva inmediata'
            }
        
        elif primary_package == 'DEFENSA_INTEGRAL':
            return {
                'name': 'DEFENSA INTEGRAL - $3,500/mes',
                'subtitle': '"Excelencia Operativa en Ciberseguridad de Clase Mundial"',
                'features': [
                    'Monitoreo continuo 24/7 con detección en tiempo real',
                    'Centro de operaciones de seguridad (SOC) dedicado',
                    'Respuesta inmediata ante incidentes (SLA de 3 horas)',
                    'Evaluaciones continuas de cumplimiento',
                    'Consultoría estratégica para transformación digital segura',
                    'Soporte premium especializado'
                ],
                'ideal': 'Organizaciones que requieren estándares de seguridad de clase mundial'
            }
        
        else:  # PROTECCION_ESENCIAL o default
            return {
                'name': 'PROTECCIÓN ESENCIAL - $1,000/mes',
                'subtitle': '"Fundamentos Sólidos para Crecimiento Seguro"',
                'features': [
                    'Evaluaciones profesionales de vulnerabilidades (2 veces al año)',
                    'Reportes ejecutivos trimestrales para toma de decisiones',
                    'Capacitación especializada del equipo humano',
                    'Asesoría estratégica mensual personalizada',
                    'Soporte técnico especializado'
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
    def get_value_propositions():
        """Propuestas de valor de SCG"""
        return [
            "🎯 GARANTIZAMOS RESULTADOS: 99% de nuestros clientes evitan incidentes mayores",
            "📊 MÉTRICAS EJECUTIVAS: Reducción promedio de 85% en vulnerabilidades críticas",
            "🤝 ALIANZA ESTRATÉGICA: Nos convertimos en extensión de su equipo ejecutivo",
            "⚡ ROI DEMOSTRABLE: Promedio de 320% en el primer año de implementación"
        ]
    
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
        return [
            ['📞', '+506 1234-5678'],
            ['📧', 'services@securitygroupcr.com'],
            ['🌐', 'www.securitygroupcr.com']
        ]
    
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