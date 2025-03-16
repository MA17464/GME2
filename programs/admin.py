from django.contrib import admin
from .models import Program

@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'program_type', 'start_date', 'end_date', 'status', 'capacity')
    list_filter = ('program_type', 'department', 'status')
    search_fields = ('name', 'description')
    date_hierarchy = 'start_date'
    ordering = ('department', 'program_type', 'name')
