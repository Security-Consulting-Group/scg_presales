# landing/views.py
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.contrib import messages
from django.db import transaction
from django.core.exceptions import ValidationError
from prospects.models import Prospect, ProspectInquiry
import logging

logger = logging.getLogger(__name__)


class LandingPageView(TemplateView):
    """Vista principal del landing page"""
    template_name = 'landing/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener el survey activo más reciente para el botón
        from surveys.models import Survey
        active_survey = Survey.objects.filter(is_active=True).order_by('-created_at').first()
        
        if active_survey:
            context['survey_code'] = active_survey.code
        
        return context


class ContactFormView(TemplateView):
    """Vista para procesar el formulario de contacto"""
    template_name = 'landing/index.html'
    
    def post(self, request, *args, **kwargs):
        try:
            # Obtener datos del formulario
            nombre = request.POST.get('nombre', '').strip()
            empresa = request.POST.get('empresa', '').strip()
            email = request.POST.get('email', '').strip().lower()
            preocupacion = request.POST.get('preocupacion', '').strip()
            
            logger.info(f"Formulario recibido - Email: {email}, Empresa: {empresa}")
            
            # Validación básica
            if not all([nombre, empresa, email, preocupacion]):
                error_msg = 'Todos los campos son obligatorios.'
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'message': error_msg}, status=400)
                messages.error(request, error_msg)
                return self.get(request, *args, **kwargs)
            
            # Validación de email básica
            if '@' not in email or '.' not in email:
                error_msg = 'Por favor ingrese un email válido.'
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'message': error_msg}, status=400)
                messages.error(request, error_msg)
                return self.get(request, *args, **kwargs)
            
            # Crear o actualizar prospect y inquiry en una transacción
            with transaction.atomic():
                # Crear o obtener prospect
                prospect, created = Prospect.objects.get_or_create(
                    email=email,
                    defaults={
                        'name': nombre,
                        'company_name': empresa,
                        'status': 'LEAD',
                        'initial_source': 'CONTACT_FORM'
                    }
                )
                
                # Si el prospect ya existía, actualizar información si es necesaria
                if not created:
                    # Actualizar solo si hay nueva información
                    if prospect.name != nombre or prospect.company_name != empresa:
                        prospect.name = nombre
                        prospect.company_name = empresa
                        prospect.save()
                        logger.info(f"Prospect actualizado: {email}")
                    else:
                        logger.info(f"Prospect existente: {email}")
                else:
                    logger.info(f"Nuevo prospect creado: {email}")
                
                # Crear inquiry - USANDO LOS CAMPOS CORRECTOS DEL MODELO
                inquiry = ProspectInquiry.objects.create(
                    prospect=prospect,
                    message=preocupacion,  # Solo usamos message, no subject ni inquiry_type
                    source='CONTACT_FORM'
                )
                
                logger.info(f"Inquiry creada - ID: {inquiry.id}")
            
            success_msg = '¡Gracias! Hemos recibido su solicitud. Nos pondremos en contacto con usted pronto.'
            
            # Si es AJAX, devolver JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': success_msg})
            
            # Si es POST normal, usar messages y redirigir
            messages.success(request, success_msg)
            return redirect('landing:index')
            
        except ValidationError as e:
            logger.error(f"Error de validación: {str(e)}")
            error_msg = 'Error en los datos proporcionados. Por favor verifique e intente nuevamente.'
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': error_msg}, status=400)
            messages.error(request, error_msg)
            return self.get(request, *args, **kwargs)
            
        except Exception as e:
            logger.error(f"Error inesperado en formulario de contacto: {str(e)}", exc_info=True)
            error_msg = 'Error procesando su solicitud. Por favor intente nuevamente.'
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': error_msg}, status=500)
            messages.error(request, error_msg)
            return self.get(request, *args, **kwargs)