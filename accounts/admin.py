from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_type', 'department', 'is_approved', 'is_staff')
    list_filter = ('user_type', 'department', 'is_approved', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'national_id')
    ordering = ('username',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': (
            'first_name', 'last_name', 'email', 
            'first_name_arabic', 'second_name_arabic', 'third_name_arabic', 'last_name_arabic',
            'phone_number', 'national_id'
        )}),
        (_('User type'), {'fields': ('user_type', 'department', 'is_approved')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'user_type', 'is_approved'),
        }),
    )

admin.site.register(User, CustomUserAdmin)
