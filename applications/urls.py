from django.urls import path
from . import views

app_name = 'applications'

urlpatterns = [
    path('', views.ApplicationListView.as_view(), name='list'),
    path('create/', views.ApplicationCreateView.as_view(), name='create'),
    path('<int:pk>/', views.ApplicationDetailView.as_view(), name='detail'),
    path('document-upload/', views.document_upload_view, name='document_upload'),
    path('get-programs-by-type/', views.get_programs_by_type, name='get_programs_by_type'),
    path('<int:pk>/update-status/', views.update_application_status, name='update_status'),
    path('bulk-email/', views.bulk_email_view, name='bulk_email'),
    path('program/<int:program_id>/', views.ProgramApplicationsListView.as_view(), name='program_applications'),
    path('delete-document/<int:document_id>/', views.delete_document, name='delete_document'),
] 