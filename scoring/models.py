"""
Scoring models for SCG Presales system.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class RiskLevel(models.TextChoices):
    """Risk levels based on score ranges."""
    CRITICAL = 'CRITICAL', 'Estado Crítico'
    HIGH = 'HIGH', 'Riesgos Significativos'
    MODERATE = 'MODERATE', 'Vulnerabilidades Moderadas'
    GOOD = 'GOOD', 'Buena Base'
    EXCELLENT = 'EXCELLENT', 'Postura Sólida'


class SurveyRiskConfiguration(models.Model):
    """
    Configuración de rangos de riesgo para cada survey.
    
    Define los rangos de puntuación que determinan cada nivel de riesgo.
    Completamente agnóstico - funciona con cualquier survey.
    """
    survey = models.OneToOneField(
        'surveys.Survey',
        on_delete=models.CASCADE,
        related_name='risk_config'
    )
    
    # Rangos de riesgo (porcentajes del max_score)
    critical_max = models.PositiveIntegerField(
        default=20,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Máximo porcentaje para Estado Crítico (ej: 20%)"
    )
    
    high_max = models.PositiveIntegerField(
        default=40,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Máximo porcentaje para Riesgos Significativos (ej: 40%)"
    )
    
    moderate_max = models.PositiveIntegerField(
        default=60,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Máximo porcentaje para Vulnerabilidades Moderadas (ej: 60%)"
    )
    
    good_max = models.PositiveIntegerField(
        default=80,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Máximo porcentaje para Buena Base (ej: 80%)"
    )
    
    # excellent_max siempre es 100%
    
    is_active = models.BooleanField(
        default=True,
        help_text="¿Esta configuración está activa?"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Survey Risk Configuration'
        verbose_name_plural = 'Survey Risk Configurations'
    
    def __str__(self):
        return f"Risk Config for {self.survey.title}"
    
    def get_risk_level_for_percentage(self, percentage):
        """Determina el risk level basado en el porcentaje obtenido."""
        if percentage <= self.critical_max:
            return RiskLevel.CRITICAL
        elif percentage <= self.high_max:
            return RiskLevel.HIGH
        elif percentage <= self.moderate_max:
            return RiskLevel.MODERATE
        elif percentage <= self.good_max:
            return RiskLevel.GOOD
        else:
            return RiskLevel.EXCELLENT


class RiskLevelPackageRecommendation(models.Model):
    """
    Recomendaciones de paquetes por nivel de riesgo.
    
    Permite asignar paquetes primary y secondary a cada risk level.
    """
    survey = models.ForeignKey(
        'surveys.Survey',
        on_delete=models.CASCADE,
        related_name='package_recommendations'
    )
    
    risk_level = models.CharField(
        max_length=20,
        choices=RiskLevel.choices,
        help_text="Nivel de riesgo"
    )
    
    # Por ahora hardcoded, después será FK a inventory app
    primary_package = models.CharField(
        max_length=50,
        choices=[
            ('PROTECCION_ESENCIAL', 'Protección Esencial'),
            ('SEGURIDAD_PROACTIVA', 'Seguridad Proactiva'),
            ('DEFENSA_INTEGRAL', 'Defensa Integral'),
            ('MANTENIMIENTO', 'Mantenimiento y Optimización'),
        ],
        help_text="Paquete principal recomendado"
    )
    
    secondary_package = models.CharField(
        max_length=50,
        choices=[
            ('PROTECCION_ESENCIAL', 'Protección Esencial'),
            ('SEGURIDAD_PROACTIVA', 'Seguridad Proactiva'),
            ('DEFENSA_INTEGRAL', 'Defensa Integral'),
            ('MANTENIMIENTO', 'Mantenimiento y Optimización'),
        ],
        blank=True,
        null=True,
        help_text="Paquete secundario recomendado (opcional)"
    )
    
    class Meta:
        verbose_name = 'Risk Level Package Recommendation'
        verbose_name_plural = 'Risk Level Package Recommendations'
        unique_together = ['survey', 'risk_level']
    
    def __str__(self):
        return f"{self.survey.title} - {self.risk_level}: {self.primary_package}"


class ScoreResult(models.Model):
    """
    Resultado del scoring para un SurveySubmission.
    
    Completamente agnóstico - funciona con cualquier survey.
    Calcula basado en survey.max_score y suma de response.points_earned.
    """
    submission = models.OneToOneField(
        'surveys.SurveySubmission',
        on_delete=models.CASCADE,
        related_name='score_result'
    )
    
    # Score absoluto obtenido
    total_points = models.PositiveIntegerField(
        help_text="Puntos totales obtenidos de las respuestas"
    )
    
    # Score como porcentaje del máximo posible
    score_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Porcentaje del score (total_points / survey.max_score * 100)"
    )
    
    # Interpretación automática
    risk_level = models.CharField(
        max_length=20,
        choices=RiskLevel.choices,
        help_text="Nivel de riesgo calculado automáticamente"
    )
    
    # Paquetes recomendados
    primary_package = models.CharField(
        max_length=50,
        help_text="Paquete principal recomendado"
    )
    
    secondary_package = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Paquete secundario recomendado"
    )
    
    # Scores por sección (automático desde SurveySection)
    section_scores = models.JSONField(
        default=dict,
        help_text="Scores desglosados por sección del survey"
    )
    
    # Metadatos
    calculated_at = models.DateTimeField(auto_now_add=True)
    recalculated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-calculated_at']
        verbose_name = 'Score Result'
        verbose_name_plural = 'Score Results'
    
    def __str__(self):
        return f"{self.submission.prospect.name} - {self.score_percentage}% ({self.risk_level})"
    
    @classmethod
    def calculate_for_submission(cls, submission):
        """
        Calcula el score para un SurveySubmission de manera agnóstica.
        
        1. Suma todos los points_earned de las responses
        2. Calcula porcentaje basado en survey.max_score
        3. Determina risk_level según configuración
        4. Asigna paquetes recomendados
        5. Calcula scores por sección automáticamente
        """
        survey = submission.survey
        
        # 1. Obtener o crear configuración de riesgo con defaults
        risk_config, created = SurveyRiskConfiguration.objects.get_or_create(
            survey=survey,
            defaults={
                'critical_max': 20,
                'high_max': 40, 
                'moderate_max': 60,
                'good_max': 80
            }
        )
        
        # 2. Calcular puntos totales
        responses = submission.responses.all()
        total_points = sum(response.points_earned for response in responses)
        
        # 3. Calcular porcentaje
        if survey.max_score > 0:
            score_percentage = (total_points / survey.max_score) * 100
        else:
            score_percentage = 0
        
        # 4. Determinar risk level
        risk_level = risk_config.get_risk_level_for_percentage(score_percentage)
        
        # 5. Obtener paquetes recomendados
        package_rec = RiskLevelPackageRecommendation.objects.filter(
            survey=survey,
            risk_level=risk_level
        ).first()
        
        primary_package = package_rec.primary_package if package_rec else 'PROTECCION_ESENCIAL'
        secondary_package = package_rec.secondary_package if package_rec else None
        
        # 6. Calcular scores por sección
        section_scores = cls._calculate_section_scores(submission)
        
        # 7. Crear o actualizar resultado
        score_result, created = cls.objects.update_or_create(
            submission=submission,
            defaults={
                'total_points': total_points,
                'score_percentage': round(score_percentage, 2),
                'risk_level': risk_level,
                'primary_package': primary_package,
                'secondary_package': secondary_package,
                'section_scores': section_scores,
            }
        )
        
        return score_result
    
    @staticmethod
    def _calculate_section_scores(submission):
        """
        Calcula scores por sección usando el modelo SurveySection existente.
        """
        section_scores = {}
        
        # Agrupar responses por sección
        responses = submission.responses.select_related('question__section').all()
        
        for response in responses:
            section = response.question.section
            section_key = f"section_{section.order}"
            
            if section_key not in section_scores:
                section_scores[section_key] = {
                    'title': section.title,
                    'points': 0,
                    'max_points': section.max_points,
                    'percentage': 0
                }
            
            section_scores[section_key]['points'] += response.points_earned
        
        # Calcular porcentajes
        for section_key, data in section_scores.items():
            if data['max_points'] > 0:
                data['percentage'] = round((data['points'] / data['max_points']) * 100, 2)
        
        return section_scores
    
    def get_risk_level_display_with_description(self):
        """Retorna el nivel de riesgo con descripción detallada."""
        descriptions = {
            RiskLevel.CRITICAL: "Su empresa presenta vulnerabilidades críticas que requieren atención inmediata.",
            RiskLevel.HIGH: "Existen riesgos significativos que deben ser abordados con urgencia.",
            RiskLevel.MODERATE: "Su empresa tiene una base sólida pero presenta vulnerabilidades moderadas.",
            RiskLevel.GOOD: "Tiene una buena base de seguridad que puede ser optimizada estratégicamente.",
            RiskLevel.EXCELLENT: "Su empresa mantiene una postura de seguridad sólida y madura."
        }
        return descriptions.get(self.risk_level, "")
    
    def get_section_score(self, section_order):
        """Obtiene el score de una sección específica por orden."""
        section_key = f"section_{section_order}"
        return self.section_scores.get(section_key, {})