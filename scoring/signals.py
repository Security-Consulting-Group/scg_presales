"""
Django signals for automatic scoring calculation.

This module handles automatic score calculation when survey submissions are completed.
"""
import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db import transaction

from surveys.models import SurveySubmission, Response
from .models import ScoreResult
from core.email_service import SurveyEmailService

logger = logging.getLogger(__name__)


@receiver(post_save, sender=SurveySubmission)
def calculate_score_on_submission_completion(sender, instance, created, **kwargs):
    """
    Calculate score automatically when a SurveySubmission is completed.
    
    This signal triggers when:
    - A SurveySubmission is marked as completed (completed_at is set)
    - The submission status is ACTIVE
    """
    # Only calculate if submission is completed and active
    if instance.is_completed and instance.status == 'ACTIVE':
        logger.info(f"Calculando score para submission completada: {instance.id}")
        
        try:
            with transaction.atomic():
                # Calculate or recalculate the score
                score_result = ScoreResult.calculate_for_submission(instance)
                
                logger.info(
                    f"Score calculado exitosamente: {score_result.score_percentage}% "
                    f"({score_result.risk_level}) para {instance.prospect.name}"
                )
                
                # Update prospect's last_contact_at if this is a new completion
                if not hasattr(instance, '_score_already_calculated'):
                    instance.prospect.last_contact_at = instance.completed_at
                    instance.prospect.save(update_fields=['last_contact_at'])
                    
                    logger.info(f"Actualizado last_contact_at para {instance.prospect.name}")
                    
                    # Send survey completion email
                    try:
                        email_sent = SurveyEmailService.send_survey_completion_email(score_result)
                        if email_sent:
                            logger.info(f"Email de completion enviado a {instance.prospect.email}")
                        else:
                            logger.warning(f"No se pudo enviar email a {instance.prospect.email}")
                    except Exception as e:
                        logger.error(f"Error enviando email de completion: {str(e)}")
                        # Don't raise exception - email failure shouldn't break the scoring process
                
        except Exception as e:
            logger.error(f"Error calculando score para submission {instance.id}: {str(e)}")
            # Don't raise the exception to avoid breaking the submission save
            # but log it for debugging
    
    elif created:
        # Nueva submission creada pero no completada
        pass


@receiver(post_save, sender=Response)
def recalculate_score_on_response_change(sender, instance, created, **kwargs):
    """
    Recalculate score when responses are added or modified.
    
    This ensures the score is always up-to-date when individual responses change.
    Only triggers if the submission is already completed.
    """
    submission = instance.submission
    
    # Only recalculate if submission is completed and active
    if submission.is_completed and submission.status == 'ACTIVE':
        logger.info(f"Recalculando score por cambio en response: {instance.id}")
        
        try:
            with transaction.atomic():
                # Recalculate the score
                score_result = ScoreResult.calculate_for_submission(submission)
                
                logger.info(
                    f"Score recalculado: {score_result.score_percentage}% "
                    f"({score_result.risk_level}) para {submission.prospect.name}"
                )
                
        except Exception as e:
            logger.error(
                f"Error recalculando score para submission {submission.id} "
                f"tras cambio en response {instance.id}: {str(e)}"
            )


@receiver(post_delete, sender=Response)
def recalculate_score_on_response_deletion(sender, instance, **kwargs):
    """
    Recalculate score when responses are deleted.
    
    This ensures the score reflects the current state after response deletion.
    """
    try:
        # Check if submission still exists (might be cascade deleted)
        submission = instance.submission
        
        # Only recalculate if submission is completed and active
        if submission.is_completed and submission.status == 'ACTIVE':
            logger.info(f"Recalculando score por eliminación de response: {instance.id}")
            
            with transaction.atomic():
                # Recalculate the score
                score_result = ScoreResult.calculate_for_submission(submission)
                
                logger.info(
                    f"Score recalculado tras eliminación: {score_result.score_percentage}% "
                    f"({score_result.risk_level}) para {submission.prospect.name}"
                )
                
    except SurveySubmission.DoesNotExist:
        # Submission was deleted, nothing to recalculate
        pass
    except Exception as e:
        logger.error(
            f"Error recalculando score tras eliminación de response {instance.id}: {str(e)}"
        )


@receiver(post_save, sender=SurveySubmission)
def handle_submission_status_change(sender, instance, created, **kwargs):
    """
    Handle scoring when submission status changes.
    
    - If status changes to DISABLED: Keep score but mark as inactive
    - If status changes back to ACTIVE and is completed: Recalculate score
    """
    if not created and hasattr(instance, '_original_status'):
        original_status = instance._original_status
        current_status = instance.status
        
        # Status changed from ACTIVE to something else
        if original_status == 'ACTIVE' and current_status != 'ACTIVE':
            logger.info(f"Submission {instance.id} cambió de ACTIVE a {current_status}")
            
            # Mark existing score as inactive (don't delete, keep for history)
            try:
                score_result = ScoreResult.objects.get(submission=instance)
                # Could add an 'is_active' field to ScoreResult in the future
                logger.info(f"Score mantenido para historial: {score_result.score_percentage}%")
            except ScoreResult.DoesNotExist:
                pass
        
        # Status changed back to ACTIVE
        elif original_status != 'ACTIVE' and current_status == 'ACTIVE':
            logger.info(f"Submission {instance.id} reactivada a ACTIVE desde {original_status}")
            
            # Recalculate if completed
            if instance.is_completed:
                try:
                    with transaction.atomic():
                        score_result = ScoreResult.calculate_for_submission(instance)
                        logger.info(f"Score recalculado al reactivar: {score_result.score_percentage}%")
                except Exception as e:
                    logger.error(f"Error recalculando score al reactivar: {str(e)}")


# Store original status to detect changes
@receiver(post_save, sender=SurveySubmission)
def store_original_status(sender, instance, **kwargs):
    """Store original status to detect changes in next save."""
    if instance.pk:
        try:
            original = SurveySubmission.objects.get(pk=instance.pk)
            instance._original_status = original.status
        except SurveySubmission.DoesNotExist:
            instance._original_status = None


# Batch operations signal for performance
def recalculate_scores_for_survey(survey, force=False):
    """
    Utility function to recalculate scores for all submissions of a survey.
    
    Args:
        survey: Survey instance
        force: Whether to recalculate even if score already exists
    
    This is not a signal but a utility function that can be called from
    management commands or admin actions.
    """
    logger.info(f"Iniciando recálculo masivo para survey: {survey.title}")
    
    submissions = survey.submissions.filter(
        status='ACTIVE',
        completed_at__isnull=False
    )
    
    success_count = 0
    error_count = 0
    
    for submission in submissions:
        try:
            # Only recalculate if forced or no score exists
            if force or not hasattr(submission, 'score_result'):
                with transaction.atomic():
                    score_result = ScoreResult.calculate_for_submission(submission)
                    success_count += 1
                    
            else:
                # Saltado (ya existe)
                pass
                
        except Exception as e:
            error_count += 1
            logger.error(
                f"Error recalculando {submission.id} ({submission.prospect.name}): {str(e)}"
            )
    
    logger.info(
        f"Recálculo masivo completado para {survey.title}: "
        f"{success_count} exitosos, {error_count} errores"
    )
    
    return success_count, error_count