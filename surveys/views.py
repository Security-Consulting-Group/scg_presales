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
from scoring.models import ScoreResult  # NUEVO IMPORT
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
                
                # 🎯 NUEVO: Calcular scoring automáticamente
                try:
                    score_result = ScoreResult.calculate_for_submission(submission)
                    logger.info(f"Score calculated - Total: {score_result.total_points}, Percentage: {score_result.score_percentage}%, Risk: {score_result.risk_level}")
                    
                    # Incluir información del scoring en la respuesta
                    scoring_info = {
                        'total_points': score_result.total_points,
                        'score_percentage': float(score_result.score_percentage),
                        'risk_level': score_result.risk_level,
                        'risk_level_display': score_result.get_risk_level_display(),
                        'primary_package': score_result.primary_package,
                        'secondary_package': score_result.secondary_package,
                        'description': score_result.get_risk_level_display_with_description()
                    }
                    
                except Exception as scoring_error:
                    logger.error(f"Error calculating score: {str(scoring_error)}", exc_info=True)
                    # No fallar la submission por error de scoring
                    scoring_info = None
                
                logger.info(f"Survey submission completed - ID: {submission.id}")
            
            # Respuesta exitosa con información de scoring
            response_data = {
                'success': True,
                'message': '¡Gracias por completar nuestro diagnóstico de ciberseguridad! Nuestro equipo analizará sus respuestas y se pondrá en contacto en las próximas 24 horas para agendar una consulta personalizada donde revisaremos los resultados juntos.'
            }
            
            # Agregar información de scoring si está disponible
            if scoring_info:
                response_data['scoring'] = scoring_info
                
                # Personalizar mensaje según risk level
                risk_messages = {
                    'CRITICAL': '¡Gracias por completar nuestro diagnóstico! Los resultados muestran áreas que requieren atención inmediata. Nuestro equipo se pondrá en contacto hoy mismo para agendar una consulta urgente.',
                    'HIGH': '¡Gracias por completar nuestro diagnóstico! Identificamos riesgos significativos que debemos abordar pronto. Nos comunicaremos en las próximas 24 horas.',
                    'MODERATE': '¡Gracias por completar nuestro diagnóstico! Su empresa tiene una base sólida con algunas áreas de mejora. Nos pondremos en contacto para revisar las oportunidades de optimización.',
                    'GOOD': '¡Gracias por completar nuestro diagnóstico! Su empresa mantiene buenas prácticas de seguridad. Nos comunicaremos para mostrarle cómo optimizar aún más su postura.',
                    'EXCELLENT': '¡Felicitaciones! Su empresa mantiene excelentes prácticas de seguridad. Nos pondremos en contacto para discutir estrategias de mantenimiento y optimización continua.'
                }
                
                custom_message = risk_messages.get(scoring_info['risk_level'])
                if custom_message:
                    response_data['message'] = custom_message
            
            return JsonResponse(response_data)
            
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
                            
                            # NUEVA LÓGICA FLEXIBLE: Calcular puntos para multiple choice
                            response.points_earned = self._calculate_multiple_choice_points(options)
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
    
    def _calculate_multiple_choice_points(self, selected_options):
        """
        Calcula puntos para preguntas de multiple choice con lógica flexible.
        
        Lógica:
        1. Si hay opciones exclusivas seleccionadas, solo contar esas
        2. Si no hay exclusivas, sumar todas las opciones normalmente
        3. Manejar casos especiales como la pregunta de datos sensibles
        """
        exclusive_options = [opt for opt in selected_options if opt.is_exclusive]
        non_exclusive_options = [opt for opt in selected_options if not opt.is_exclusive]
        
        # Si hay opciones exclusivas seleccionadas
        if exclusive_options:
            # Solo contar las opciones exclusivas (ignorar las demás)
            total_points = sum(opt.points for opt in exclusive_options)
            logger.info(f"Exclusive options selected, using only exclusive points: {total_points}")
            return total_points
        
        # Si no hay opciones exclusivas, usar lógica normal o especial
        elif non_exclusive_options:
            # Detectar si es la pregunta especial de datos sensibles (pregunta 3, sección 1)
            first_option = non_exclusive_options[0]
            question = first_option.question
            
            if (question.order == 3 and 
                question.section.order == 1 and 
                any("información sensible" in opt.option_text.lower() for opt in question.options.all())):
                
                # Lógica especial para pregunta de datos sensibles
                num_selected = len(non_exclusive_options)
                scoring_map = {0: 5, 1: 4, 2: 3, 3: 2, 4: 1}
                points = scoring_map.get(num_selected, 1)
                logger.info(f"Special sensitive data scoring: {num_selected} types selected = {points} points")
                return points
            else:
                # Lógica normal: sumar todos los puntos
                total_points = sum(opt.points for opt in non_exclusive_options)
                logger.info(f"Normal multiple choice scoring: {total_points} points")
                return total_points
        
        return 0
    
    def get_client_ip(self, request):
        """Obtener la IP del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip