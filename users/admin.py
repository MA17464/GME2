from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Applicant, Program, Application

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'user_type', 'program', 'is_approved', 'is_staff')
    list_filter = ('user_type', 'is_approved', 'program')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone_number')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('GME Info', {'fields': ('user_type', 'program', 'is_approved')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'user_type', 'program', 'is_approved'),
        }),
    )
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)

class ApplicantAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name_en', 'last_name_en', 'national_id')
    search_fields = ('first_name_en', 'last_name_en', 'national_id')

class ProgramAdmin(admin.ModelAdmin):
    list_display = ('name', 'program_type', 'start_date', 'end_date', 'status', 'capacity')
    list_filter = ('program_type', 'status')
    search_fields = ('name',)

class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('applicant', 'program', 'university_name', 'gpa', 'status', 'created_at')
    list_filter = ('status', 'program')
    search_fields = ('applicant__username', 'program__name', 'university_name')
    date_hierarchy = 'created_at'

admin.site.register(User, CustomUserAdmin)
admin.site.register(Applicant, ApplicantAdmin)
admin.site.register(Program, ProgramAdmin)
admin.site.register(Application, ApplicationAdmin)
