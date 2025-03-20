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
    path('view-application/<int:application_id>/', views.view_application, name='view_application'),
    path('upload-scores/', views.upload_scores, name='upload_scores'),
    path('process-scores/', views.process_scores, name='process_scores'),
    path('export-applications/', views.export_applications, name='export_applications'),
    path('bulk-update-status/', views.bulk_update_status, name='bulk_update_status'),
    path('approve-staff/<int:user_id>/', views.approve_staff, name='approve_staff'),
    path('manage-programs/', views.manage_programs, name='manage_programs'),
    path('create-program/', views.create_program, name='create_program'),
    path('edit-program/<int:program_id>/', views.edit_program, name='edit_program'),
    path('delete-program/<int:program_id>/', views.delete_program, name='delete_program'),
    
    # Interviewer URLs
    path('interviewer/dashboard/', views.interviewer_dashboard, name='interviewer_dashboard'),
    path('interviewer/conduct-interview/<int:application_id>/', views.conduct_interview, name='conduct_interview'),
    
    # Applicant URLs
    path('applicant/dashboard/', views.applicant_dashboard, name='applicant_dashboard'),
    path('applicant/submit-draft/<int:application_id>/', views.submit_draft, name='submit_draft'),
    path('applicant/edit-application/<int:application_id>/', views.edit_application, name='edit_application'),
    
    # AJAX
    path('ajax/load-programs/', views.load_programs, name='ajax_load_programs'),

    # Program Director URLs
    path('director/dashboard/', views.director_dashboard, name='director_dashboard'),
    path('director/interview-results/<int:application_id>/', views.view_interview_results, name='view_interview_results'),
    path('director/submit-final-score/<int:application_id>/', views.submit_final_score, name='submit_final_score'),
    path('update-application-status/<int:application_id>/', views.update_application_status, name='update_application_status'),

    # File Download
    path('application/<int:application_id>/file/<str:file_type>/', views.download_application_file, name='download_application_file'),
] 