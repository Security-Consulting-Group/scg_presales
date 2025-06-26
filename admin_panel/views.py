# admin_panel/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView, View, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q, Count, Avg, Min, Max
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import timedelta, datetime
import csv

from surveys.models import Survey, SurveySubmission, SurveySection, Question, QuestionOption
from prospects.models import Prospect, ProspectInquiry, InteractionNote
from scoring.models import ScoreResult, SurveyRiskConfiguration, RiskLevelPackageRecommendation, RiskLevel
from scoring.signals import recalculate_scores_for_survey
from core.models import User
import json

import logging
logger = logging.getLogger(__name__)


# ====================================
# AUTHENTICATION VIEWS  
# ====================================

class AdminLoginView(View):
    """Login view for admin panel"""
    template_name = 'admin_panel/auth/login.html'
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('admin_panel:dashboard')
        return render(request, self.template_name)
    
    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, username=email, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            messages.success(request, f'Bienvenido, {user.first_name}!')
            return redirect('admin_panel:dashboard')
        else:
            messages.error(request, 'Credenciales inválidas o sin permisos de acceso.')
            return render(request, self.template_name)


class AdminLogoutView(LoginRequiredMixin, View):
    """Logout view for admin panel"""
    
    def get(self, request):
        logout(request)
        messages.success(request, 'Sesión cerrada exitosamente.')
        return redirect('admin_panel:login')


# ====================================
# DASHBOARD
# ====================================

class DashboardView(LoginRequiredMixin, TemplateView):
    """Main dashboard - placeholder for now"""
    template_name = 'admin_panel/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Basic counts for placeholder
        context.update({
            'total_prospects': Prospect.objects.count(),
            'total_surveys': Survey.objects.count(),
            'active_surveys': Survey.objects.filter(is_active=True).count(),
            'recent_submissions': SurveySubmission.objects.filter(status='ACTIVE').count(),
        })
        
        return context


# ====================================
# SURVEYS CRUD
# ====================================

class SurveyListView(LoginRequiredMixin, ListView):
    """List all surveys with filters"""
    model = Survey
    template_name = 'admin_panel/surveys/list.html'
    context_object_name = 'surveys'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Survey.objects.all().order_by('-created_at')
        
        # Search filter
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(code__icontains=search) |
                Q(description__icontains=search)
            )
        
        # Status filter
        status = self.request.GET.get('status')
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['status_filter'] = self.request.GET.get('status', '')
        return context


class SurveyDetailView(LoginRequiredMixin, DetailView):
    """View survey details and submissions"""
    model = Survey
    template_name = 'admin_panel/surveys/detail.html'
    context_object_name = 'survey'
    slug_field = 'code'
    slug_url_kwarg = 'code'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get recent submissions
        context['recent_submissions'] = self.object.submissions.filter(
            status='ACTIVE'
        ).select_related('prospect').order_by('-started_at')[:10]
        
        # Basic stats
        context['total_submissions'] = self.object.submissions.filter(status='ACTIVE').count()
        context['completed_submissions'] = self.object.submissions.filter(
            status='ACTIVE', 
            completed_at__isnull=False
        ).count()
        
        return context


class SurveyCreateView(LoginRequiredMixin, CreateView):
    """Create new survey"""
    model = Survey
    template_name = 'admin_panel/surveys/form.html'
    fields = ['title', 'description', 'version', 'max_score', 'is_active', 'is_featured']
    success_url = reverse_lazy('admin_panel:surveys_list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, f'Survey "{form.instance.title}" creado exitosamente.')
        return super().form_valid(form)


class SurveyUpdateView(LoginRequiredMixin, UpdateView):
    """Edit existing survey"""
    model = Survey
    template_name = 'admin_panel/surveys/form.html'
    fields = ['title', 'description', 'version', 'max_score', 'is_active', 'is_featured']
    slug_field = 'code'
    slug_url_kwarg = 'code'
    
    def get_success_url(self):
        messages.success(self.request, f'Survey "{self.object.title}" actualizado exitosamente.')
        return reverse_lazy('admin_panel:survey_detail', kwargs={'code': self.object.code})


# ====================================
# PROSPECTS CRUD
# ====================================

class ProspectListView(LoginRequiredMixin, ListView):
    """List all prospects with filters and search"""
    model = Prospect
    template_name = 'admin_panel/prospects/list.html'
    context_object_name = 'prospects'
    paginate_by = 25
    
    def get_queryset(self):
        queryset = Prospect.objects.all().prefetch_related(
            'inquiries', 'survey_submissions'
        ).order_by('-created_at')
        
        # Search filter
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(email__icontains=search) |
                Q(company_name__icontains=search)
            )
        
        # Status filter
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Source filter
        source = self.request.GET.get('source')
        if source:
            queryset = queryset.filter(initial_source=source)
        
        # Industry filter
        industry = self.request.GET.get('industry')
        if industry:
            queryset = queryset.filter(company_industry=industry)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['status_filter'] = self.request.GET.get('status', '')
        context['source_filter'] = self.request.GET.get('source', '')
        context['industry_filter'] = self.request.GET.get('industry', '')
        
        # For filter dropdowns
        from prospects.models import ProspectStatus, IndustryChoices
        context['status_choices'] = ProspectStatus.choices
        context['industry_choices'] = IndustryChoices.choices
        context['source_choices'] = [
            ('CONTACT_FORM', 'Contact Form'),
            ('SURVEY', 'Diagnostic Survey'),
            ('REFERRAL', 'Referral'),
            ('OTHER', 'Other'),
        ]
        
        return context


class ProspectDetailView(LoginRequiredMixin, DetailView):
    """View prospect details, inquiries, and submissions"""
    model = Prospect
    template_name = 'admin_panel/prospects/detail.html'
    context_object_name = 'prospect'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all inquiries
        context['inquiries'] = self.object.inquiries.all().order_by('-created_at')
        
        # Get survey submissions
        context['survey_submissions'] = self.object.survey_submissions.filter(
            status='ACTIVE'
        ).select_related('survey').order_by('-started_at')
        
        # Get interaction notes
        context['interaction_notes'] = self.object.interaction_notes.all().order_by('-created_at')
        
        # Latest score if available
        latest_submission = context['survey_submissions'].first()
        if latest_submission:
            context['latest_score'] = latest_submission.get_total_score()
        
        return context


class ProspectUpdateView(LoginRequiredMixin, UpdateView):
    """Edit prospect information"""
    model = Prospect
    template_name = 'admin_panel/prospects/form.html'
    fields = [
        'name', 'email', 'phone', 'company_name', 'company_industry', 
        'company_size', 'status', 'last_contact_at'
    ]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add stats for existing prospects
        if self.object:
            context['pending_inquiries_count'] = self.object.inquiries.filter(is_responded=False).count()
            context['total_inquiries_count'] = self.object.inquiries.count()
            context['surveys_count'] = self.object.survey_submissions.filter(status='ACTIVE').count()
            context['notes_count'] = self.object.interaction_notes.count()
        
        return context
    
    def get_success_url(self):
        messages.success(self.request, f'Prospect "{self.object.name}" actualizado exitosamente.')
        return reverse_lazy('admin_panel:prospect_detail', kwargs={'pk': self.object.pk})


class ProspectCreateView(LoginRequiredMixin, CreateView):
    """Create new prospect manually"""
    model = Prospect
    template_name = 'admin_panel/prospects/form.html'
    fields = [
        'name', 'email', 'phone', 'company_name', 'company_industry', 
        'company_size', 'status'
    ]
    
    def form_valid(self, form):
        # Set initial_source to MANUAL for manually created prospects
        form.instance.initial_source = 'MANUAL'
        messages.success(self.request, f'Prospect "{form.instance.name}" creado exitosamente.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('admin_panel:prospect_detail', kwargs={'pk': self.object.pk})

# ====================================
# SURVEY SECTIONS CRUD
# ====================================

class SectionCreateView(LoginRequiredMixin, CreateView):
    """Create new section for a survey"""
    model = SurveySection
    template_name = 'admin_panel/surveys/section_form.html'
    fields = ['title', 'description', 'order', 'max_points']
    
    def dispatch(self, request, *args, **kwargs):
        self.survey = get_object_or_404(Survey, code=kwargs['code'])
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.survey = self.survey
        messages.success(self.request, f'Sección "{form.instance.title}" creada exitosamente.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('admin_panel:survey_detail', kwargs={'code': self.survey.code}) + '#sections'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['survey'] = self.survey
        context['next_order'] = self.survey.sections.count() + 1
        return context


class SectionUpdateView(LoginRequiredMixin, UpdateView):
    """Edit existing section"""
    model = SurveySection
    template_name = 'admin_panel/surveys/section_form.html'
    fields = ['title', 'description', 'order', 'max_points']
    
    def get_success_url(self):
        messages.success(self.request, f'Sección "{self.object.title}" actualizada exitosamente.')
        return reverse_lazy('admin_panel:survey_detail', kwargs={'code': self.object.survey.code}) + '#sections'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['survey'] = self.object.survey
        return context


class SectionDeleteView(LoginRequiredMixin, View):
    """Delete section via AJAX"""
    
    def post(self, request, pk):
        section = get_object_or_404(SurveySection, pk=pk)
        survey_code = section.survey.code
        section_title = section.title
        questions_count = section.questions.count()
        
        # Delete section (cascade will delete questions)
        section.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Sección "{section_title}" eliminada exitosamente ({questions_count} preguntas eliminadas).',
            'redirect_url': reverse_lazy('admin_panel:survey_detail', kwargs={'code': survey_code}) + '#sections'
        })


# ====================================
# SURVEY QUESTIONS CRUD
# ====================================

class QuestionCreateView(LoginRequiredMixin, CreateView):
    """Create new question for a survey"""
    model = Question
    template_name = 'admin_panel/surveys/question_form.html'
    fields = ['section', 'question_text', 'question_type', 'order', 'is_required', 'max_points', 'help_text']
    
    def dispatch(self, request, *args, **kwargs):
        self.survey = get_object_or_404(Survey, code=kwargs['code'])
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.survey = self.survey
        messages.success(self.request, f'Pregunta creada exitosamente.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('admin_panel:survey_detail', kwargs={'code': self.survey.code}) + '#questions'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['survey'] = self.survey
        context['sections'] = self.survey.sections.all().order_by('order')
        return context
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Limit section choices to this survey's sections
        form.fields['section'].queryset = self.survey.sections.all().order_by('order')
        return form


class QuestionUpdateView(LoginRequiredMixin, UpdateView):
    """Edit existing question"""
    model = Question
    template_name = 'admin_panel/surveys/question_form.html'
    fields = ['section', 'question_text', 'question_type', 'order', 'is_required', 'max_points', 'help_text']
    
    def get_success_url(self):
        messages.success(self.request, f'Pregunta actualizada exitosamente.')
        return reverse_lazy('admin_panel:survey_detail', kwargs={'code': self.object.survey.code}) + '#questions'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['survey'] = self.object.survey
        context['sections'] = self.object.survey.sections.all().order_by('order')
        return context
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Limit section choices to this survey's sections
        form.fields['section'].queryset = self.object.survey.sections.all().order_by('order')
        return form


class QuestionDeleteView(LoginRequiredMixin, View):
    """Delete question via AJAX"""
    
    def post(self, request, pk):
        question = get_object_or_404(Question, pk=pk)
        survey_code = question.survey.code
        options_count = question.options.count()
        
        # Delete question (cascade will delete options)
        question.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Pregunta eliminada exitosamente ({options_count} opciones eliminadas).',
            'redirect_url': reverse_lazy('admin_panel:survey_detail', kwargs={'code': survey_code}) + '#questions'
        })

class ToggleSurveyStatusView(LoginRequiredMixin, View):
    """Toggle survey active status via AJAX"""
    
    def post(self, request, code):
        survey = get_object_or_404(Survey, code=code)
        survey.is_active = not survey.is_active
        survey.save()
        
        return JsonResponse({
            'success': True,
            'new_status': survey.is_active,
            'message': f'Survey {"activado" if survey.is_active else "desactivado"} exitosamente.'
        })


class MarkInquiryRespondedView(LoginRequiredMixin, View):
    """Mark inquiry as responded via AJAX"""
    
    def post(self, request, inquiry_id):
        inquiry = get_object_or_404(ProspectInquiry, id=inquiry_id)
        inquiry.mark_as_responded(responded_by=f"{request.user.first_name} {request.user.last_name}")
        
        return JsonResponse({
            'success': True,
            'message': 'Inquiry marcada como respondida.'
        })
        

# ====================================
# QUESTION OPTIONS AJAX MANAGEMENT
# ====================================

class OptionCreateView(LoginRequiredMixin, View):
    """Create new option for a question via AJAX"""
    
    def post(self, request, question_id):
        try:
            question = get_object_or_404(Question, pk=question_id)
            
            # Get data from request
            option_text = request.POST.get('option_text', '').strip()
            order = int(request.POST.get('order', 1))
            points = int(request.POST.get('points', 0))
            
            if not option_text:
                return JsonResponse({
                    'success': False,
                    'message': 'El texto de la opción es requerido'
                }, status=400)
            
            # Create the option
            option = QuestionOption.objects.create(
                question=question,
                option_text=option_text,
                order=order,
                points=points,
                is_active=True
            )
            
            return JsonResponse({
                'success': True,
                'message': f'Opción "{option_text}" creada exitosamente',
                'option': {
                    'id': option.id,
                    'text': option.option_text,
                    'order': option.order,
                    'points': option.points
                }
            })
            
        except ValueError as e:
            return JsonResponse({
                'success': False,
                'message': 'Error en los datos numéricos'
            }, status=400)
        except Exception as e:
            logger.error(f"Error creating option: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': 'Error creando la opción'
            }, status=500)


class OptionUpdateView(LoginRequiredMixin, View):
    """Update existing option via AJAX"""
    
    def post(self, request, pk):
        try:
            option = get_object_or_404(QuestionOption, pk=pk)
            
            # Get data from request
            option_text = request.POST.get('option_text', '').strip()
            order = int(request.POST.get('order', option.order))
            points = int(request.POST.get('points', option.points))
            
            if not option_text:
                return JsonResponse({
                    'success': False,
                    'message': 'El texto de la opción es requerido'
                }, status=400)
            
            # Update the option
            option.option_text = option_text
            option.order = order
            option.points = points
            option.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Opción actualizada exitosamente',
                'option': {
                    'id': option.id,
                    'text': option.option_text,
                    'order': option.order,
                    'points': option.points
                }
            })
            
        except ValueError as e:
            return JsonResponse({
                'success': False,
                'message': 'Error en los datos numéricos'
            }, status=400)
        except Exception as e:
            logger.error(f"Error updating option: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': 'Error actualizando la opción'
            }, status=500)


class OptionDeleteView(LoginRequiredMixin, View):
    """Delete option via AJAX"""
    
    def post(self, request, pk):
        try:
            option = get_object_or_404(QuestionOption, pk=pk)
            option_text = option.option_text
            
            # Delete the option
            option.delete()
            
            return JsonResponse({
                'success': True,
                'message': f'Opción "{option_text}" eliminada exitosamente'
            })
            
        except Exception as e:
            logger.error(f"Error deleting option: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': 'Error eliminando la opción'
            }, status=500)
            
class OptionBulkSaveView(LoginRequiredMixin, View):
    """Save multiple options at once via AJAX"""
    
    def post(self, request, question_id):
        try:
            question = get_object_or_404(Question, pk=question_id)
            
            # Parse JSON data
            data = json.loads(request.body)
            options_data = data.get('options', [])
            
            if not options_data:
                return JsonResponse({
                    'success': False,
                    'message': 'No hay opciones para guardar'
                }, status=400)
            
            # Track what we're doing
            created_count = 0
            updated_count = 0
            deleted_count = 0
            
            # Get existing option IDs that should be kept
            incoming_option_ids = [
                opt.get('id') for opt in options_data 
                if opt.get('id') and opt.get('isExisting')
            ]
            incoming_option_ids = [id for id in incoming_option_ids if id]  # Remove None values
            
            # Delete options that are no longer in the list
            existing_options = question.options.all()
            for existing_option in existing_options:
                if str(existing_option.id) not in [str(id) for id in incoming_option_ids]:
                    existing_option.delete()
                    deleted_count += 1
            
            # Process each option
            for option_data in options_data:
                option_text = option_data.get('text', '').strip()
                option_order = int(option_data.get('order', 1))
                option_points = int(option_data.get('points', 0))
                option_id = option_data.get('id')
                is_existing = option_data.get('isExisting', False)
                
                if not option_text:
                    continue  # Skip empty options
                
                if option_id and is_existing:
                    # Update existing option
                    try:
                        option = QuestionOption.objects.get(id=option_id, question=question)
                        option.option_text = option_text
                        option.order = option_order
                        option.points = option_points
                        option.save()
                        updated_count += 1
                    except QuestionOption.DoesNotExist:
                        # Option was deleted, create new one
                        QuestionOption.objects.create(
                            question=question,
                            option_text=option_text,
                            order=option_order,
                            points=option_points,
                            is_active=True
                        )
                        created_count += 1
                else:
                    # Create new option
                    QuestionOption.objects.create(
                        question=question,
                        option_text=option_text,
                        order=option_order,
                        points=option_points,
                        is_active=True
                    )
                    created_count += 1
            
            # Build success message
            message_parts = []
            if created_count > 0:
                message_parts.append(f"{created_count} opción{'es' if created_count != 1 else ''} creada{'s' if created_count != 1 else ''}")
            if updated_count > 0:
                message_parts.append(f"{updated_count} opción{'es' if updated_count != 1 else ''} actualizada{'s' if updated_count != 1 else ''}")
            if deleted_count > 0:
                message_parts.append(f"{deleted_count} opción{'es' if deleted_count != 1 else ''} eliminada{'s' if deleted_count != 1 else ''}")
            
            if not message_parts:
                message = "No se realizaron cambios"
            else:
                message = "Opciones guardadas: " + ", ".join(message_parts)
            
            return JsonResponse({
                'success': True,
                'message': message,
                'stats': {
                    'created': created_count,
                    'updated': updated_count,
                    'deleted': deleted_count
                }
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Error en el formato de datos'
            }, status=400)
        except ValueError as e:
            return JsonResponse({
                'success': False,
                'message': 'Error en los datos numéricos'
            }, status=400)
        except Exception as e:
            logger.error(f"Error in bulk save options: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': 'Error guardando las opciones'
            }, status=500)


# ====================================
# SCORING VIEWS
# ====================================

class ScoreResultListView(LoginRequiredMixin, ListView):
    """Lista todos los resultados de scoring con filtros"""
    model = ScoreResult
    template_name = 'admin_panel/scoring/list.html'
    context_object_name = 'score_results'
    paginate_by = 25
    
    def get_queryset(self):
        queryset = ScoreResult.objects.select_related(
            'submission__prospect', 
            'submission__survey'
        ).order_by('-calculated_at')
        
        # Filtro por risk level
        risk_level = self.request.GET.get('risk_level')
        if risk_level and risk_level in dict(RiskLevel.choices):
            queryset = queryset.filter(risk_level=risk_level)
        
        # Filtro por survey
        survey = self.request.GET.get('survey')
        if survey:
            queryset = queryset.filter(submission__survey_id=survey)
        
        # Filtro por rango de score
        min_score = self.request.GET.get('min_score')
        max_score = self.request.GET.get('max_score')
        if min_score:
            try:
                queryset = queryset.filter(score_percentage__gte=float(min_score))
            except ValueError:
                pass
        if max_score:
            try:
                queryset = queryset.filter(score_percentage__lte=float(max_score))
            except ValueError:
                pass
        
        # Filtro por fecha
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        if date_from:
            try:
                date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
                queryset = queryset.filter(calculated_at__date__gte=date_from)
            except ValueError:
                pass
        if date_to:
            try:
                date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
                queryset = queryset.filter(calculated_at__date__lte=date_to)
            except ValueError:
                pass
        
        # Búsqueda por nombre o email del prospect
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(submission__prospect__name__icontains=search) |
                Q(submission__prospect__email__icontains=search) |
                Q(submission__prospect__company_name__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Para los filtros
        context['surveys'] = Survey.objects.filter(is_active=True).order_by('title')
        context['risk_levels'] = RiskLevel.choices
        
        # Valores actuales de filtros
        context['current_filters'] = {
            'risk_level': self.request.GET.get('risk_level', ''),
            'survey': self.request.GET.get('survey', ''),
            'min_score': self.request.GET.get('min_score', ''),
            'max_score': self.request.GET.get('max_score', ''),
            'date_from': self.request.GET.get('date_from', ''),
            'date_to': self.request.GET.get('date_to', ''),
            'search': self.request.GET.get('search', ''),
        }
        
        # Estadísticas rápidas de la query actual
        current_queryset = self.get_queryset()
        context['filtered_stats'] = {
            'total': current_queryset.count(),
            'avg_score': current_queryset.aggregate(avg=Avg('score_percentage'))['avg'] or 0,
            'risk_distribution': current_queryset.values('risk_level').annotate(
                count=Count('id')
            ).order_by('risk_level')
        }
        
        return context


class ScoreResultDetailView(LoginRequiredMixin, DetailView):
    """Vista detallada de un resultado de scoring"""
    model = ScoreResult
    template_name = 'admin_panel/scoring/detail.html'
    context_object_name = 'score_result'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener el score_result (self.object)
        score_result = self.object
        
        # Obtener survey a través de la relación submission
        survey = score_result.submission.survey
        
        # Obtener la configuración de riesgo del survey
        try:
            risk_config = SurveyRiskConfiguration.objects.get(survey=survey)
        except SurveyRiskConfiguration.DoesNotExist:
            risk_config = None
        
        # Agregar datos básicos al contexto
        context.update({
            'survey': survey,
            'submission': score_result.submission,
            'prospect': score_result.submission.prospect,
            'risk_config': risk_config,
        })
        
        # Solo proceder con cálculos si existe configuración de riesgo
        if risk_config:
            # Calcular rangos en puntos para evitar usar filtros mul/div en template
            max_score = survey.max_score
            
            # Calcular puntos para cada rango
            critical_points_max = int((risk_config.critical_max / 100) * max_score)
            high_points_min = critical_points_max + 1
            high_points_max = int((risk_config.high_max / 100) * max_score)
            moderate_points_min = high_points_max + 1
            moderate_points_max = int((risk_config.moderate_max / 100) * max_score)
            good_points_min = moderate_points_max + 1
            good_points_max = int((risk_config.good_max / 100) * max_score)
            excellent_points_min = good_points_max + 1
            
            # Preparar datos de rangos para el template
            context['risk_ranges'] = {
                'critical': {
                    'percent_min': 0,
                    'percent_max': risk_config.critical_max,
                    'points_min': 0,
                    'points_max': critical_points_max,
                },
                'high': {
                    'percent_min': risk_config.critical_max + 1,
                    'percent_max': risk_config.high_max,
                    'points_min': high_points_min,
                    'points_max': high_points_max,
                },
                'moderate': {
                    'percent_min': risk_config.high_max + 1,
                    'percent_max': risk_config.moderate_max,
                    'points_min': moderate_points_min,
                    'points_max': moderate_points_max,
                },
                'good': {
                    'percent_min': risk_config.moderate_max + 1,
                    'percent_max': risk_config.good_max,
                    'points_min': good_points_min,
                    'points_max': good_points_max,
                },
                'excellent': {
                    'percent_min': risk_config.good_max + 1,
                    'percent_max': 100,
                    'points_min': excellent_points_min,
                    'points_max': max_score,
                }
            }
            
            # Calcular anchos para la visualización
            context['range_widths'] = {
                'critical': risk_config.critical_max,
                'high': risk_config.high_max - risk_config.critical_max,
                'moderate': risk_config.moderate_max - risk_config.high_max,
                'good': risk_config.good_max - risk_config.moderate_max,
                'excellent': 100 - risk_config.good_max,
            }
        
        # Estadísticas del mismo survey
        same_survey_stats = ScoreResult.objects.filter(
            submission__survey=survey
        ).aggregate(
            avg_score=Avg('score_percentage'),
            min_score=Min('score_percentage'),
            max_score=Max('score_percentage'),
            total_count=Count('id')
        )
        
        if same_survey_stats['total_count'] > 0:
            context['same_survey_stats'] = same_survey_stats
            
            # Calcular percentil (posición relativa)
            lower_scores_count = ScoreResult.objects.filter(
                submission__survey=survey,
                score_percentage__lt=score_result.score_percentage
            ).count()
            
            if same_survey_stats['total_count'] > 1:
                percentile = round((lower_scores_count / (same_survey_stats['total_count'] - 1)) * 100)
                context['score_percentile'] = percentile
                
                # Calcular posición del marcador para visualización
                score_range = same_survey_stats['max_score'] - same_survey_stats['min_score']
                if score_range > 0:
                    marker_position = ((score_result.score_percentage - same_survey_stats['min_score']) / score_range) * 100
                    context['score_marker_position'] = marker_position
        
        # Obtener recomendación de paquete si existe
        if risk_config:
            try:
                package_recommendation = RiskLevelPackageRecommendation.objects.get(
                    survey=survey,
                    risk_level=score_result.risk_level
                )
                context['package_recommendation'] = package_recommendation
            except RiskLevelPackageRecommendation.DoesNotExist:
                pass
        
        # Obtener respuestas del survey organizadas por sección
        try:
            from surveys.models import Response
            
            responses = Response.objects.filter(
                submission=score_result.submission
            ).select_related('question__section', 'selected_option').prefetch_related(
                'selected_options'  # Para preguntas de múltiple selección
            ).order_by('question__section__order', 'question__order')
            
            # Organizar respuestas por sección
            if responses.exists():
                responses_by_section = {}
                for response in responses:
                    section = response.question.section
                    if section not in responses_by_section:
                        responses_by_section[section] = []
                    responses_by_section[section].append(response)
                
                context['responses_by_section'] = responses_by_section
            
        except Exception as e:
            # Si hay cualquier error, simplemente no mostrar respuestas
            logger.warning(f"No se pudieron cargar las respuestas del survey: {e}")
            pass
        
        # Otros scores del mismo prospect
        other_scores = ScoreResult.objects.filter(
            submission__prospect=score_result.submission.prospect
        ).exclude(
            id=score_result.id
        ).select_related(
            'submission__survey'
        ).order_by('-calculated_at')[:5]
        
        if other_scores.exists():
            context['other_scores'] = other_scores
        
        return context

class SurveyRiskConfigListView(LoginRequiredMixin, ListView):
    """Lista las configuraciones de riesgo por survey"""
    model = SurveyRiskConfiguration
    template_name = 'admin_panel/scoring/risk_config_list.html'
    context_object_name = 'risk_configs'
    paginate_by = 20
    
    def get_queryset(self):
        return SurveyRiskConfiguration.objects.select_related('survey').order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Surveys sin configuración
        surveys_without_config = Survey.objects.filter(
            risk_config__isnull=True,
            is_active=True
        ).order_by('title')
        
        context['surveys_without_config'] = surveys_without_config
        
        return context


class SurveyRiskConfigDetailView(LoginRequiredMixin, DetailView):
    """Vista detallada de configuración de riesgo"""
    model = SurveyRiskConfiguration
    template_name = 'admin_panel/scoring/risk_config_detail.html'
    context_object_name = 'risk_config'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        risk_config = self.object
        survey = risk_config.survey
        
        # Calcular rangos en puntos para evitar usar filtros mul/div en template
        max_score = survey.max_score
        
        # Calcular puntos para cada rango
        critical_points_max = int((risk_config.critical_max / 100) * max_score)
        high_points_min = critical_points_max + 1
        high_points_max = int((risk_config.high_max / 100) * max_score)
        moderate_points_min = high_points_max + 1
        moderate_points_max = int((risk_config.moderate_max / 100) * max_score)
        good_points_min = moderate_points_max + 1
        good_points_max = int((risk_config.good_max / 100) * max_score)
        excellent_points_min = good_points_max + 1
        
        # Preparar datos de rangos para el template
        context['risk_ranges'] = {
            'critical': {
                'percent_min': 0,
                'percent_max': risk_config.critical_max,
                'points_min': 0,
                'points_max': critical_points_max,
            },
            'high': {
                'percent_min': risk_config.critical_max + 1,
                'percent_max': risk_config.high_max,
                'points_min': high_points_min,
                'points_max': high_points_max,
            },
            'moderate': {
                'percent_min': risk_config.high_max + 1,
                'percent_max': risk_config.moderate_max,
                'points_min': moderate_points_min,
                'points_max': moderate_points_max,
            },
            'good': {
                'percent_min': risk_config.moderate_max + 1,
                'percent_max': risk_config.good_max,
                'points_min': good_points_min,
                'points_max': good_points_max,
            },
            'excellent': {
                'percent_min': risk_config.good_max + 1,
                'percent_max': 100,
                'points_min': excellent_points_min,
                'points_max': max_score,
            }
        }
        
        # Calcular anchos para la visualización (corregido)
        context['range_widths'] = {
            'critical': risk_config.critical_max,  # 0 to critical_max
            'high': risk_config.high_max - risk_config.critical_max,  # critical_max to high_max
            'moderate': risk_config.moderate_max - risk_config.high_max,  # high_max to moderate_max
            'good': risk_config.good_max - risk_config.moderate_max,  # moderate_max to good_max
            'excellent': 100 - risk_config.good_max,  # good_max to 100
        }
        
        # Debug: imprimir para verificar
        print("🔍 Range widths:", context['range_widths'])
        print("🔍 Risk config values:", {
            'critical_max': risk_config.critical_max,
            'high_max': risk_config.high_max,
            'moderate_max': risk_config.moderate_max,
            'good_max': risk_config.good_max,
        })
        
        # Estadísticas de scores con esta configuración
        scores_stats_queryset = ScoreResult.objects.filter(
            submission__survey=survey
        ).values('risk_level').annotate(
            count=Count('id'),
            avg_score=Avg('score_percentage')
        ).order_by('risk_level')
        
        # Convertir queryset a lista
        scores_stats = list(scores_stats_queryset)
        
        # Calcular porcentajes para las barras de estadísticas
        total_scores = sum(stat['count'] for stat in scores_stats)
        scores_stats_with_percentages = []
        for stat in scores_stats:
            stat_copy = dict(stat)
            if total_scores > 0:
                stat_copy['percentage_width'] = round((stat['count'] / total_scores) * 100, 1)
            else:
                stat_copy['percentage_width'] = 0
            scores_stats_with_percentages.append(stat_copy)
        
        print("🔍 Scores stats:", scores_stats_with_percentages)
        
        context['scores_stats'] = scores_stats_with_percentages
        
        # Recomendaciones de paquetes para este survey
        package_recommendations = RiskLevelPackageRecommendation.objects.filter(
            survey=survey
        ).order_by('risk_level')
        
        context['package_recommendations'] = package_recommendations
        
        # Submissions recientes
        recent_submissions = ScoreResult.objects.filter(
            submission__survey=survey
        ).select_related('submission__prospect').order_by('-calculated_at')[:10]
        
        context['recent_submissions'] = recent_submissions
        
        return context


class RecalculateScoresView(LoginRequiredMixin, View):
    """Vista AJAX para recalcular scores masivamente"""
    
    def post(self, request):
        survey_id = request.POST.get('survey_id')
        force_recalculate = request.POST.get('force', 'false').lower() == 'true'
        
        if not survey_id:
            return JsonResponse({
                'success': False,
                'message': 'ID del survey es requerido'
            }, status=400)
        
        try:
            survey = Survey.objects.get(id=survey_id)
        except Survey.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Survey no encontrado'
            }, status=404)
        
        try:
            # Usar la función utilitaria del signals
            success_count, error_count = recalculate_scores_for_survey(
                survey=survey,
                force=force_recalculate
            )
            
            return JsonResponse({
                'success': True,
                'message': f'Recálculo completado: {success_count} exitosos, {error_count} errores',
                'stats': {
                    'success_count': success_count,
                    'error_count': error_count
                }
            })
            
        except Exception as e:
            logger.error(f"Error en recálculo masivo para survey {survey_id}: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': f'Error en el recálculo: {str(e)}'
            }, status=500)


class ExportScoresView(LoginRequiredMixin, View):
    """Vista para exportar scores en CSV"""
    
    def get(self, request):
        # Aplicar los mismos filtros que en la lista
        queryset = ScoreResult.objects.select_related(
            'submission__prospect', 
            'submission__survey'
        ).order_by('-calculated_at')
        
        # Aplicar filtros (misma lógica que ScoreResultListView)
        risk_level = request.GET.get('risk_level')
        if risk_level and risk_level in dict(RiskLevel.choices):
            queryset = queryset.filter(risk_level=risk_level)
        
        survey = request.GET.get('survey')
        if survey:
            queryset = queryset.filter(submission__survey_id=survey)
        
        search = request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(submission__prospect__name__icontains=search) |
                Q(submission__prospect__email__icontains=search) |
                Q(submission__prospect__company_name__icontains=search)
            )
        
        # Crear response CSV
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="scores_export_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        
        # Headers
        writer.writerow([
            'Prospect',
            'Email', 
            'Empresa',
            'Survey',
            'Score (%)',
            'Puntos',
            'Risk Level',
            'Paquete Primario',
            'Paquete Secundario',
            'Fecha Cálculo',
            'Fecha Completion'
        ])
        
        # Datos
        for score in queryset:
            writer.writerow([
                score.submission.prospect.name,
                score.submission.prospect.email,
                score.submission.prospect.company_name or '',
                score.submission.survey.title,
                f"{score.score_percentage}%",
                f"{score.total_points}/{score.submission.survey.max_score}",
                score.get_risk_level_display(),
                score.primary_package,
                score.secondary_package or '',
                score.calculated_at.strftime('%Y-%m-%d %H:%M:%S'),
                score.submission.completed_at.strftime('%Y-%m-%d %H:%M:%S') if score.submission.completed_at else ''
            ])
        
        return response
    
    
# ====================================
# SCORING CONFIG
# ====================================

class SurveyRiskConfigCreateView(LoginRequiredMixin, CreateView):
    """Crear nueva configuración de riesgo para un survey"""
    model = SurveyRiskConfiguration
    template_name = 'admin_panel/scoring/risk_config_form.html'
    fields = [
        'survey', 'critical_max', 'high_max', 'moderate_max', 'good_max', 'is_active'
    ]
    success_url = reverse_lazy('admin_panel:risk_configs_list')
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Solo mostrar surveys que no tengan configuración de riesgo
        surveys_without_config = Survey.objects.filter(
            risk_config__isnull=True,
            is_active=True
        ).order_by('title')
        form.fields['survey'].queryset = surveys_without_config
        
        # Valores por defecto para rangos
        form.fields['critical_max'].initial = 20
        form.fields['high_max'].initial = 40
        form.fields['moderate_max'].initial = 60
        form.fields['good_max'].initial = 80
        
        return form
    
    def form_valid(self, form):
        messages.success(
            self.request, 
            f'Configuración de riesgo creada para "{form.instance.survey.title}"'
        )
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Crear Configuración de Riesgo'
        context['action'] = 'create'
        return context


class SurveyRiskConfigUpdateView(LoginRequiredMixin, UpdateView):
    """Editar configuración de riesgo existente"""
    model = SurveyRiskConfiguration
    template_name = 'admin_panel/scoring/risk_config_form.html'
    fields = [
        'critical_max', 'high_max', 'moderate_max', 'good_max', 'is_active'
    ]
    
    def get_success_url(self):
        messages.success(
            self.request, 
            f'Configuración de riesgo actualizada para "{self.object.survey.title}"'
        )
        return reverse_lazy('admin_panel:risk_config_detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Editar Configuración - {self.object.survey.title}'
        context['action'] = 'edit'
        return context


class QuickRiskConfigCreateView(LoginRequiredMixin, View):
    """Crear configuración de riesgo rápida con valores por defecto"""
    
    def post(self, request):
        survey_id = request.POST.get('survey_id')
        
        if not survey_id:
            return JsonResponse({
                'success': False,
                'message': 'ID del survey es requerido'
            }, status=400)
        
        try:
            survey = Survey.objects.get(id=survey_id)
        except Survey.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Survey no encontrado'
            }, status=404)
        
        # Verificar si ya existe configuración
        if hasattr(survey, 'risk_config'):
            return JsonResponse({
                'success': False,
                'message': f'El survey "{survey.title}" ya tiene configuración de riesgo'
            }, status=400)
        
        try:
            # Crear configuración con valores por defecto
            risk_config = SurveyRiskConfiguration.objects.create(
                survey=survey,
                critical_max=20,  # 0-20%
                high_max=40,      # 21-40%
                moderate_max=60,  # 41-60%
                good_max=80,      # 61-80%
                # excellent: 81-100%
                is_active=True
            )
            
            return JsonResponse({
                'success': True,
                'message': f'Configuración de riesgo creada para "{survey.title}" con valores por defecto',
                'config_id': risk_config.id,
                'redirect_url': reverse_lazy('admin_panel:risk_config_detail', kwargs={'pk': risk_config.pk})
            })
            
        except Exception as e:
            logger.error(f"Error creando configuración de riesgo: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': f'Error creando configuración: {str(e)}'
            }, status=500)

class ChangeProspectStatusView(LoginRequiredMixin, View):
    """Vista para cambiar el estado de un prospect vía AJAX"""
    
    def post(self, request, prospect_id):
        prospect = get_object_or_404(Prospect, pk=prospect_id)
        new_status = request.POST.get('status')
        
        # Validar que el estado sea uno de los permitidos
        if new_status in dict(Prospect._meta.get_field('status').choices):
            old_status = prospect.status
            prospect.status = new_status
            prospect.save(update_fields=['status', 'updated_at'])
            
            return JsonResponse({
                'success': True,
                'status': prospect.status,
                'status_display': prospect.get_status_display(),
                'message': f'Estado actualizado de {dict(Prospect._meta.get_field("status").choices)[old_status]} a {prospect.get_status_display()}'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Estado inválido'
            }, status=400)