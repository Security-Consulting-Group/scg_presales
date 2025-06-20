"""
Management command para cargar los datos del survey de SCG.
Ubicación: surveys/management/commands/load_survey_data.py
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from surveys.models import (
    Survey, SurveySection, Question, QuestionOption, QuestionType
)


class Command(BaseCommand):
    help = 'Carga los datos del Diagnóstico Ejecutivo de Ciberseguridad SCG'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Fuerza la recreación del survey si ya existe'
        )
        
        parser.add_argument(
            '--survey-code',
            type=str,
            help='Código específico para el survey (formato YYYYMMDDHHMMSS)'
        )

    def handle(self, *args, **options):
        force = options['force']
        survey_code = options.get('survey_code')
        
        try:
            with transaction.atomic():
                # Generar código único si no se proporciona
                if not survey_code:
                    survey_code = Survey.generate_code()
                
                self.stdout.write(
                    self.style.SUCCESS(f'Iniciando carga de datos con código: {survey_code}')
                )
                
                # Verificar si el survey ya existe
                if Survey.objects.filter(code=survey_code).exists():
                    if not force:
                        raise CommandError(
                            f'Survey con código {survey_code} ya existe. '
                            'Use --force para sobrescribir.'
                        )
                    else:
                        Survey.objects.filter(code=survey_code).delete()
                        self.stdout.write(
                            self.style.WARNING(f'Survey existente eliminado: {survey_code}')
                        )
                
                # Crear el survey principal
                survey = self.create_survey(survey_code)
                self.stdout.write(
                    self.style.SUCCESS(f'Survey creado: {survey}')
                )
                
                # Crear las secciones
                sections = self.create_sections(survey)
                self.stdout.write(
                    self.style.SUCCESS(f'Creadas {len(sections)} secciones')
                )
                
                # Crear las preguntas y opciones
                total_questions = self.create_questions_and_options(survey, sections)
                self.stdout.write(
                    self.style.SUCCESS(f'Creadas {total_questions} preguntas con sus opciones')
                )
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Survey cargado exitosamente!\n'
                        f'URL: /surveys/{survey_code}/'
                    )
                )
                
        except Exception as e:
            raise CommandError(f'Error cargando survey: {str(e)}')

    def create_survey(self, code):
        """Crea el survey principal."""
        from surveys.management.commands.survey_data_complete import SURVEY_DATA
        
        survey_info = SURVEY_DATA['survey']
        
        survey = Survey.objects.create(
            code=code,
            title=survey_info['title'],
            description=survey_info['description'],
            version=survey_info['version'],
            max_score=survey_info['max_score'],
            created_by=survey_info['created_by'],
            is_active=True
        )
        
        return survey

    def create_sections(self, survey):
        """Crea las secciones del survey."""
        from surveys.management.commands.survey_data_complete import SURVEY_DATA
        
        sections = {}
        
        for section_data in SURVEY_DATA['sections']:
            section = SurveySection.objects.create(
                survey=survey,
                title=section_data['title'],
                description=section_data['description'],
                order=section_data['order'],
                max_points=section_data['max_points']
            )
            sections[section_data['order']] = section
            
        return sections

    def create_questions_and_options(self, survey, sections):
        """Crea las preguntas y sus opciones."""
        from surveys.management.commands.survey_data_complete import SURVEY_DATA
        
        questions_created = 0
        
        for question_data in SURVEY_DATA['questions']:
            section = sections[question_data['section']]
            
            # Crear la pregunta
            question = Question.objects.create(
                survey=survey,
                section=section,
                question_text=question_data['question_text'],
                question_type=question_data['question_type'],
                order=question_data['order'],
                is_required=question_data['is_required'],
                max_points=question_data['max_points'],
                help_text=question_data.get('help_text', ''),
                is_active=True
            )
            
            # Crear las opciones
            for option_data in question_data['options']:
                QuestionOption.objects.create(
                    question=question,
                    option_text=option_data['text'],
                    order=option_data['order'],
                    points=option_data['points'],
                    is_active=True
                )
            
            questions_created += 1
            
            self.stdout.write(
                f'  ✓ Q{question_data["section"]}.{question_data["order"]}: '
                f'{question_data["question_text"][:50]}...'
            )
        
        return questions_created