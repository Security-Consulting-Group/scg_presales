# admin_panel/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView, View
from django.urls import reverse_lazy
from django.db.models import Q, Count
from django.http import JsonResponse
from django.core.paginator import Paginator

from surveys.models import Survey, SurveySubmission, SurveySection, Question, QuestionOption
from django.views.generic import DeleteView
from prospects.models import Prospect, ProspectInquiry, InteractionNote
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