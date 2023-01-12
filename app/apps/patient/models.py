import logging
from uuid import uuid4
from django.db import models
from tasks.tasks import create_email

logger = logging.getLogger(__name__)

class PatientManager(models.Manager):
    """
    A Manager for Patient objects
    """
    def get_query_set(self):
        return self.get_queryset()

    def cancelled(self):
        qs = self.get_query_set().filter(
            cancelled__gt=0
        )
        return qs

    def in_study(self):
        qs = self.get_query_set().filter(
            cancelled=0, status =0
        )
        return qs



class Patient(models.Model):

    """
    A "Patient" connects a user to a study.
    """

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey('auth.User', on_delete=models.PROTECT)
    study = models.ForeignKey('study.Study', on_delete=models.PROTECT)
    status = models.IntegerField(choices=(
        (0, "New"),
        (10, "Engaged"),
        (20, "Consented"),
        (30, "Complete"),
    ), default=0)
    cancelled = models.IntegerField(choices=(
        (0, "-"),
        (10, "Not Eligible"),
        (20, "Not Consented"),
        (30, "Opted out"),
        (40, "Not contactable"),
    ), default=0)

    objects = PatientManager()

    class Meta:
        constraints = (
                models.constraints.UniqueConstraint(
                fields=["study", "user"],
                name="unique_patient_per_study"
            ),
        )
        verbose_name = "Patient"
        verbose_name_plural = "Patients"

    def __str__(self):
        return str(self.id)

    
    def in_study(self) -> bool:
        #Used to check a patient is in the linked study
        if self.cancelled == 0 and self.status == 0:
            return True
        return False


    def send_email(self):
        #Double check that the patient is in a study
        if not self.in_study:
            logging.DEBUG(f'Patient ID: {self.id}, is not participating in Study ID: {self.study.id}')
        else:

            create_email.delay(
                email = self.user.email,
                cc = [],
                context = {
                    'patient_username': self.user.username,
                    'care_provider_contact': 'XXX',
                    'care_provider_name': 'XXX',
                }
                )
