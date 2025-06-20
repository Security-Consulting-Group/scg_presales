# landing/views.py
from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import JsonResponse
from prospects.models import Prospect, ProspectInquiry


class LandingPageView(TemplateView):
    """Vista principal del landing page"""
    template_name = 'landing/index.html'


class ContactFormView(TemplateView):
    """Vista para procesar el formulario de contacto"""
    
    def post(self, request, *args, **kwargs):
        try:
            nombre = request.POST.get('nombre', '').strip()
            empresa = request.POST.get('empresa', '').strip()
            email = request.POST.get('email', '').strip().lower()
            preocupacion = request.POST.get('preocupacion', '').strip()
            
            if not all([nombre, empresa, email, preocupacion]):
                return JsonResponse({
                    'success': False,
                    'message': 'Todos los campos son obligatorios.'
                }, status=400)
            
            # Crear prospect
            prospect, created = Prospect.objects.get_or_create(
                email=email,
                defaults={
                    'name': nombre,
                    'company_name': empresa,
                    'status': 'LEAD',
                    'initial_source': 'CONTACT_FORM'
                }
            )
            
            # Crear inquiry
            ProspectInquiry.objects.create(
                prospect=prospect,
                inquiry_type='CONSULTATION',
                subject=f'Consulta de asesoría - {empresa}',
                message=preocupacion,
                source='CONTACT_FORM'
            )
            
            return JsonResponse({
                'success': True,
                'message': '¡Gracias! Nos pondremos en contacto con usted pronto.'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': 'Error procesando su solicitud.'
            }, status=500)