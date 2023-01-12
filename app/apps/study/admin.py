from django.contrib import admin

from apps.study.models import Study


@admin.register(Study)
class StudyAdmin(admin.ModelAdmin):

    list_display = ("id", "name")
