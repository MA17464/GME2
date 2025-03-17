from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/staff/', views.staff_register, name='staff_register'),
    path('register/applicant/', views.applicant_register, name='applicant_register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # GME Staff URLs
    path('dashboard/', views.dashboard, name='dashboard'),
    path('approve-staff/<int:user_id>/', views.approve_staff, name='approve_staff'),
    path('programs/', views.manage_programs, name='manage_programs'),
    path('programs/edit/<int:program_id>/', views.edit_program, name='edit_program'),
    path('programs/delete/<int:program_id>/', views.delete_program, name='delete_program'),
    path('applications/update-status/<int:application_id>/', views.update_application_status, name='update_application_status'),
    path('applications/bulk-update-status/', views.bulk_update_status, name='bulk_update_status'),
    path('applications/upload-scores/', views.upload_scores, name='upload_scores'),
    path('applications/process-scores/', views.process_scores, name='process_scores'),
    path('applications/export/', views.export_applications, name='export_applications'),
    
    # Interviewer URLs
    path('interviewer/dashboard/', views.interviewer_dashboard, name='interviewer_dashboard'),
    path('interviewer/conduct-interview/<int:application_id>/', views.conduct_interview, name='conduct_interview'),
    
    # Applicant URLs
    path('applicant/dashboard/', views.applicant_dashboard, name='applicant_dashboard'),
    path('applicant/submit-draft/<int:application_id>/', views.submit_draft, name='submit_draft'),
    
    # AJAX
    path('ajax/load-programs/', views.load_programs, name='ajax_load_programs'),
] 