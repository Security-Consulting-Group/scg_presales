# landing/urls.py
from django.urls import path
from . import views

app_name = 'landing'

urlpatterns = [
    path('', views.LandingPageView.as_view(), name='index'),
    path('contact/', views.ContactFormView.as_view(), name='contact'),
]