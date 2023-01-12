# --------------------------------------------------------------
# Django imports
# --------------------------------------------------------------
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import get_connection 
from apps.patient.models import Patient


# --------------------------------------------------------------
# 3rd party imports
# --------------------------------------------------------------
from celery import shared_task
from celery.utils.log import get_task_logger
 
logger = get_task_logger(__name__)

@shared_task(bind=True)
def bulk_email(self,**kwargs):
    '''
    Used to bulk send email
    '''
    patients = Patient.objects.in_study()

    #I would use Django bulk_send as it uses a single connection
    pass
    