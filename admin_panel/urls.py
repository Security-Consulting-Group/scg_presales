# admin_panel/urls.py
from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    # Authentication
    path('login/', views.AdminLoginView.as_view(), name='login'),
    path('logout/', views.AdminLogoutView.as_view(), name='logout'),
    
    # Dashboard
    path('', views.DashboardView.as_view(), name='dashboard'),
    
    # Surveys CRUD
    path('surveys/', views.SurveyListView.as_view(), name='surveys_list'),
    path('surveys/create/', views.SurveyCreateView.as_view(), name='survey_create'),
    path('surveys/<str:code>/', views.SurveyDetailView.as_view(), name='survey_detail'),
    path('surveys/<str:code>/edit/', views.SurveyUpdateView.as_view(), name='survey_edit'),
    
    # Survey Sections CRUD
    path('surveys/<str:code>/sections/create/', views.SectionCreateView.as_view(), name='section_create'),
    path('sections/<int:pk>/edit/', views.SectionUpdateView.as_view(), name='section_edit'),
    path('sections/<int:pk>/delete/', views.SectionDeleteView.as_view(), name='section_delete'),
    
    # Survey Questions CRUD
    path('surveys/<str:code>/questions/create/', views.QuestionCreateView.as_view(), name='question_create'),
    path('questions/<int:pk>/edit/', views.QuestionUpdateView.as_view(), name='question_edit'),
    path('questions/<int:pk>/delete/', views.QuestionDeleteView.as_view(), name='question_delete'),
    path('ajax/questions/<int:question_id>/options/bulk-save/', views.OptionBulkSaveView.as_view(), name='option_bulk_save'),

    # Prospects CRUD
    path('prospects/', views.ProspectListView.as_view(), name='prospects_list'),
    path('prospects/create/', views.ProspectCreateView.as_view(), name='prospect_create'),  # NEW
    path('prospects/<int:pk>/', views.ProspectDetailView.as_view(), name='prospect_detail'),
    path('prospects/<int:pk>/edit/', views.ProspectUpdateView.as_view(), name='prospect_edit'),
    path('ajax/prospects/<int:prospect_id>/change-status/', views.ChangeProspectStatusView.as_view(), name='change_prospect_status'),
    
    # AJAX Actions
    path('ajax/surveys/<str:code>/toggle-status/', views.ToggleSurveyStatusView.as_view(), name='toggle_survey_status'),
    path('ajax/inquiries/<int:inquiry_id>/mark-responded/', views.MarkInquiryRespondedView.as_view(), name='mark_inquiry_responded'),
    
    # Question Options AJAX
    path('ajax/questions/<int:question_id>/options/create/', views.OptionCreateView.as_view(), name='option_create'),
    path('ajax/options/<int:pk>/update/', views.OptionUpdateView.as_view(), name='option_update'),
    path('ajax/options/<int:pk>/delete/', views.OptionDeleteView.as_view(), name='option_delete'),
    
    # ====================================
    # SCORING URLS
    # ====================================

    # Scoring principal (lista)
    path('scoring/', views.ScoreResultListView.as_view(), name='scoring_list'),

    # Score Results CRUD
    path('scoring/results/', views.ScoreResultListView.as_view(), name='score_results_list'),
    path('scoring/results/<int:pk>/', views.ScoreResultDetailView.as_view(), name='score_result_detail'),
    path('scoring/results/export/', views.ExportScoresView.as_view(), name='export_scores'),

    # Risk Configuration Management
    path('scoring/risk-configs/create/', views.SurveyRiskConfigCreateView.as_view(), name='risk_config_create'),
    path('scoring/risk-configs/<int:pk>/edit/', views.SurveyRiskConfigUpdateView.as_view(), name='risk_config_edit'),
    path('scoring/risk-configs/quick-create/', views.QuickRiskConfigCreateView.as_view(), name='risk_config_quick_create'),
    path('scoring/risk-configs/', views.SurveyRiskConfigListView.as_view(), name='risk_configs_list'),
    path('scoring/risk-configs/<int:pk>/', views.SurveyRiskConfigDetailView.as_view(), name='risk_config_detail'),

    # AJAX Actions for Scoring
    path('ajax/scoring/recalculate/', views.RecalculateScoresView.as_view(), name='recalculate_scores'),
]