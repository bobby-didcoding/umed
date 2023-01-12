from uuid import uuid4
from django.db import models


class CareProvider(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=100, help_text="The name of the care provider.")
    ods = models.CharField(max_length=8, unique=True, help_text="NHS identifier for the care provider")
    contact = models.CharField(max_length=50, help_text="Full name and salutation of the main contact at the care provider.")

    class Meta:
        verbose_name = "Care Provider"
        verbose_name_plural = "Care Providers"

    def __str__(self):
        return self.name

