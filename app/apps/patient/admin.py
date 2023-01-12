from django.contrib import admin

from apps.patient.models import Patient

def send_email_button(modeladmin, request, queryset):
    for patient in queryset:
        patient.send_email()

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):

    list_display = ("id", "user_id", "study", "status", "cancelled")
    list_filter = ("status", "cancelled")
    actions = [send_email_button]
