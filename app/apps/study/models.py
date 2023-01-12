from uuid import uuid4
from django.db import models


class Study(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True, help_text="The name of the study.")

    class Meta:
        verbose_name = "Study"
        verbose_name_plural = "Studies"

    def __str__(self):
        return self.name
