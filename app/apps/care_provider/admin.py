from django.contrib import admin

from apps.care_provider.models import CareProvider


@admin.register(CareProvider)
class CareProviderAdmin(admin.ModelAdmin):

    list_display = ("id", "name", "ods", "contact")
