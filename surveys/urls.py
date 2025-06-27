# surveys/urls.py
from django.urls import path
from . import views

app_name = 'surveys'

urlpatterns = [
    # Survey principal con código único
    path('<str:code>/', views.SurveyView.as_view(), name='survey_detail'),
    
    # Endpoint para procesar respuestas via AJAX
    path('<str:code>/submit/', views.SurveySubmitView.as_view(), name='survey_submit'),
]