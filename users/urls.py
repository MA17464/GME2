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
    path('applications/bulk-email/', views.bulk_email, name='bulk_email'),
    
    # Applicant URLs
    path('applicant/dashboard/', views.applicant_dashboard, name='applicant_dashboard'),
    
    # AJAX
    path('ajax/load-programs/', views.load_programs, name='ajax_load_programs'),
] 