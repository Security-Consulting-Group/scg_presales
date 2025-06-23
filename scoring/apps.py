from django.apps import AppConfig


class ScoringConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'scoring'

default_app_config = 'scoring.apps.ScoringConfig'