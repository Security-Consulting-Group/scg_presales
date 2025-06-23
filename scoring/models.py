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
