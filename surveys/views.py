# surveys/views.py
from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, View
from django.http import JsonResponse
from django.contrib import messages
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from prospects.models import Prospect
from .models import Survey, SurveySubmission, Response, Question, QuestionOption
import logging
import json

logger = logging.getLogger(__name__)


class SurveyView(TemplateView):
    """Vista principal para mostrar el survey"""
    template_name = 'surveys/survey.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener el survey por código
        code = kwargs.get('code')
        survey = get_object_or_404(Survey, code=code, is_active=True)
        
        # Obtener todas las preguntas activas del survey
        questions = survey.get_active_questions()
        
        # Organizar preguntas en grupos para el SPA (dinámico)
        questions_list = list(questions)
        total_questions = len(questions_list)
        
        # Calcular grupos dinámicamente
        if total_questions <= 5:
            # Si hay 5 o menos preguntas, todo en un grupo
            question_groups = [questions_list]
        elif total_questions <= 10:
            # Si hay 6-10 preguntas, dividir en 2 grupos
            mid = total_questions // 2
            question_groups = [
                questions_list[:mid],
                questions_list[mid:]
            ]
        else:
            # Si hay más de 10 preguntas, dividir en 3 grupos
            # Distribuir lo más equitativamente posible
            group_size = total_questions // 3
            remainder = total_questions % 3
            
            # Calcular tamaños de grupos
            sizes = [group_size] * 3
            for i in range(remainder):
                sizes[i] += 1
            
            # Crear grupos
            start = 0
            question_groups = []
            for size in sizes:
                question_groups.append(questions_list[start:start + size])
                start += size
        
        context.update({
            'survey': survey,
            'question_groups': question_groups,
            'total_questions': len(questions_list),
        })
        
        return context


class SurveySubmitView(View):
    """Vista para procesar las respuestas del survey via AJAX"""
    
    def post(self, request, code):
        try:
            # Obtener el survey
            survey = get_object_or_404(Survey, code=code, is_active=True)
            
            # Parsear datos JSON del request
            data = json.loads(request.body)
            logger.info(f"Survey submission received for {code}: {data}")
            
            # Validar que tenemos respuestas y datos del prospect
            responses_data = data.get('responses', {})
            prospect_data = data.get('prospect', {})
            
            if not responses_data or not prospect_data:
                return JsonResponse({
                    'success': False, 
                    'message': 'Datos incompletos'
                }, status=400)
            
            # Validar datos del prospect
            email = prospect_data.get('email', '').strip().lower()
            nombre = prospect_data.get('nombre', '').strip()
            empresa = prospect_data.get('empresa', '').strip()
            
            if not all([email, nombre, empresa]):
                return JsonResponse({
                    'success': False,
                    'message': 'Email, nombre y empresa son obligatorios'
                }, status=400)
            
            # Validar email básico
            if '@' not in email or '.' not in email:
                return JsonResponse({
                    'success': False,
                    'message': 'Por favor ingrese un email válido'
                }, status=400)
            
            # Procesar todo en una transacción
            with transaction.atomic():
                # Crear o actualizar prospect
                prospect, created = Prospect.objects.get_or_create(
                    email=email,
                    defaults={
                        'name': nombre,
                        'company_name': empresa,
                        'status': 'QUALIFIED',  # Los que completan survey son qualified
                        'initial_source': 'SURVEY'
                    }
                )
                
                # Si el prospect ya existía, actualizar información
                if not created:
                    prospect.name = nombre
                    prospect.company_name = empresa
                    if prospect.status == 'LEAD':
                        prospect.status = 'QUALIFIED'
                    prospect.save()
                    logger.info(f"Prospect actualizado: {email}")
                else:
                    logger.info(f"Nuevo prospect creado: {email}")
                
                # Crear survey submission
                submission = SurveySubmission.objects.create(
                    prospect=prospect,
                    survey=survey,
                    completed_at=timezone.now(),
                    ip_address=self.get_client_ip(request)
                )
                
                # Procesar respuestas
                self.process_responses(submission, responses_data)
                
                logger.info(f"Survey submission completed - ID: {submission.id}")
            
            # Respuesta exitosa
            return JsonResponse({
                'success': True,
                'message': '¡Gracias por completar nuestro diagnóstico de ciberseguridad! Nuestro equipo analizará sus respuestas y se pondrá en contacto en las próximas 24 horas para agendar una consulta personalizada donde revisaremos los resultados juntos.'
            })
            
        except json.JSONDecodeError:
            logger.error("Error parsing JSON data")
            return JsonResponse({
                'success': False,
                'message': 'Error en el formato de datos'
            }, status=400)
            
        except ValidationError as e:
            logger.error(f"Validation error: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': 'Error en los datos proporcionados'
            }, status=400)
            
        except Exception as e:
            logger.error(f"Unexpected error in survey submission: {str(e)}", exc_info=True)
            return JsonResponse({
                'success': False,
                'message': 'Error procesando su solicitud. Por favor intente nuevamente.'
            }, status=500)
    
    def process_responses(self, submission, responses_data):
        """Procesar y guardar las respuestas del survey"""
        for question_id, response_data in responses_data.items():
            try:
                question = Question.objects.get(
                    id=question_id,
                    survey=submission.survey,
                    is_active=True
                )
                
                # Crear la respuesta
                response = Response.objects.create(
                    submission=submission,
                    question=question
                )
                
                # Procesar según el tipo de pregunta
                if question.question_type == 'SINGLE_CHOICE':
                    option_id = response_data.get('option_id')
                    if option_id:
                        option = QuestionOption.objects.get(
                            id=option_id,
                            question=question,
                            is_active=True
                        )
                        response.selected_option = option
                        response.points_earned = option.points
                        response.save()
                
                elif question.question_type == 'MULTIPLE_CHOICE':
                    option_ids = response_data.get('option_ids', [])
                    if option_ids:
                        options = QuestionOption.objects.filter(
                            id__in=option_ids,
                            question=question,
                            is_active=True
                        )
                        response.save()  # Guardar primero para poder usar M2M
                        response.selected_options.set(options)
                        response.points_earned = sum(opt.points for opt in options)
                        response.save()
                
                elif question.question_type in ['TEXT', 'EMAIL']:
                    text_value = response_data.get('text', '').strip()
                    response.text_response = text_value
                    response.save()
                
                logger.info(f"Response saved for question {question.id}: {response_data}")
                
            except Question.DoesNotExist:
                logger.warning(f"Question {question_id} not found or inactive")
                continue
            except QuestionOption.DoesNotExist:
                logger.warning(f"Option not found for question {question_id}")
                continue
            except Exception as e:
                logger.error(f"Error processing response for question {question_id}: {str(e)}")
                continue
    
    def get_client_ip(self, request):
        """Obtener la IP del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip