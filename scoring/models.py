"""
Scoring models for SCG Presales system.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class RiskLevel(models.TextChoices):
    """Risk levels based on score ranges."""
    CRITICAL = 'CRITICAL', 'Estado Crítico (0-20)'
    HIGH = 'HIGH', 'Riesgos Significativos (21-40)'
    MODERATE = 'MODERATE', 'Vulnerabilidades Moderadas (41-60)'
    GOOD = 'GOOD', 'Buena Base (61-80)'
    EXCELLENT = 'EXCELLENT', 'Postura Sólida (81-100)'


class RecommendedPackage(models.TextChoices):
    """Recommended service packages based on score."""
    PROTECCION_ESENCIAL = 'PROTECCION_ESENCIAL', 'Protección Esencial'
    SEGURIDAD_PROACTIVA = 'SEGURIDAD_PROACTIVA', 'Seguridad Proactiva'
    DEFENSA_INTEGRAL = 'DEFENSA_INTEGRAL', 'Defensa Integral'
    MANTENIMIENTO = 'MANTENIMIENTO', 'Mantenimiento y Optimización'


class ScoreResult(models.Model):
    """
    Simple score result model without complex relationships for now.
    """
    # Basic identification
    prospect_email = models.EmailField(help_text="Email of the prospect")
    prospect_name = models.CharField(max_length=100, help_text="Name of the prospect")
    
    # Overall scoring
    total_score = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Total score out of 100"
    )
    
    risk_level = models.CharField(
        max_length=20,
        choices=RiskLevel.choices,
        help_text="Risk level based on total score"
    )
    
    recommended_package = models.CharField(
        max_length=30,
        choices=RecommendedPackage.choices,
        help_text="Recommended service package"
    )
    
    # Section scores
    context_score = models.PositiveIntegerField(default=0)
    access_management_score = models.PositiveIntegerField(default=0)
    infrastructure_score = models.PositiveIntegerField(default=0)
    risk_management_score = models.PositiveIntegerField(default=0)
    
    # Timestamps
    calculated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-calculated_at']
        verbose_name = 'Score Result'
        verbose_name_plural = 'Score Results'
    
    def __str__(self):
        return f"{self.prospect_name} - Score: {self.total_score} ({self.risk_level})"