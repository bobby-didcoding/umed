# --------------------------------------------------------------
# Django imports
# --------------------------------------------------------------
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import get_connection 


# --------------------------------------------------------------
# 3rd party imports
# --------------------------------------------------------------
from celery import shared_task
from celery.utils.log import get_task_logger
 
logger = get_task_logger(__name__)

@shared_task(bind=True)
def create_email(self,**kwargs):
    '''
    Used to create an email and send via a selection of templates
    '''
    context = kwargs.get("context", {})
    subject = kwargs.get("subject", "")
    email = kwargs.get("email")
    template = kwargs.get("template", "tasks/patient_email.html")
    cc_email = kwargs.get("cc_email", [])
 
    html_content = render_to_string(template, context ) # render with dynamic value
    text_content = strip_tags(html_content) # Strip the html tag. So people can see the pure text at least.

    with get_connection(
            host= settings.EMAIL_HOST,
            port= settings.EMAIL_PORT,
            username=settings.EMAIL_HOST_USER,
            password=settings.EMAIL_HOST_PASSWORD,
            use_tls=settings.EMAIL_USE_TLS,
        ) as connection:
            msg = EmailMultiAlternatives(
                subject,
                text_content,
                f'{settings.DISPLAY_NAME} <{settings.EMAIL_HOST_USER}>',
                [email],
                cc=[cc_email],
                connection=connection)
            msg.attach_alternative(html_content, "text/html")
            msg.send()
    return f"Task: Send email to [{email}]: Success"
 
