from django.contrib import admin
from .models import Application, ApplicationDocument

class ApplicationDocumentInline(admin.TabularInline):
    model = ApplicationDocument
    extra = 0
    readonly_fields = ('uploaded_at',)

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('user', 'program', 'status', 'university_name', 'gpa', 'created_at')
    list_filter = ('status', 'program__program_type', 'program__department')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name', 'university_name')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ApplicationDocumentInline]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'program', 'reviewed_by')

@admin.register(ApplicationDocument)
class ApplicationDocumentAdmin(admin.ModelAdmin):
    list_display = ('application', 'document_type', 'uploaded_at')
    list_filter = ('document_type', 'uploaded_at')
    search_fields = ('application__user__username', 'application__user__email')
    date_hierarchy = 'uploaded_at'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('application', 'application__user')
