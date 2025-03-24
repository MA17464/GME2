from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden, FileResponse, Http404
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q, F, Sum
from django.core.exceptions import PermissionDenied
from .models import User, Applicant, Program, Application, Interview, ApplicantScore
from .forms import (
    StaffRegistrationForm, ApplicantRegistrationForm, ProgramForm, 
    ApplicationForm, StaffApprovalForm, ApplicationStatusForm, BulkEmailForm,
    ResidencyInterviewForm, FellowshipInterviewForm, BulkScoreUploadForm,
    AdvancedFilterForm
)
import csv
import pandas as pd
import io
import logging
import os
from functools import wraps

# Set up logger
logger = logging.getLogger(__name__)

def can_access_file(user, application):
    """
    Check if user has permission to access application files
    """
    if user.user_type == 'GME_STAFF':
        return True
    elif user.user_type in ['PROGRAM_DIRECTOR', 'INTERVIEWER']:
        return application.program == user.program
    elif user.user_type == 'APPLICANT':
        return application.applicant == user
    return False

def verify_program_access(user, program):
    """
    Verify if user has access to the specified program
    """
    if user.user_type == 'GME_STAFF':
        return True
    return user.program == program

def check_interview_modification(interview):
    """
    Check if an interview can be modified
    """
    application = interview.application
    if application.final_score_submitted:
        return False
    return True

def require_program_access(view_func):
    """
    Decorator to verify program access
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        program_id = kwargs.get('program_id')
        if program_id:
            program = get_object_or_404(Program, id=program_id)
            if not verify_program_access(request.user, program):
                raise PermissionDenied("You don't have access to this program")
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def home(request):
    residency_programs = Program.objects.filter(program_type='RESIDENCY', status='ACTIVE')
    fellowship_programs = Program.objects.filter(program_type='FELLOWSHIP', status='ACTIVE')
    return render(request, 'users/home.html', {
        'residency_programs': residency_programs,
        'fellowship_programs': fellowship_programs
    })

def staff_register(request):
    if request.method == 'POST':
        form = StaffRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registration successful! Your account is pending approval.')
            return redirect('login')
    else:
        form = StaffRegistrationForm()
    return render(request, 'users/staff_register.html', {'form': form})

def applicant_register(request):
    if request.method == 'POST':
        form = ApplicantRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registration successful! You can now login.')
            return redirect('login')
    else:
        form = ApplicantRegistrationForm()
    return render(request, 'users/applicant_register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_approved:
                login(request, user)
                if user.user_type == 'GME_STAFF':
                    return redirect('dashboard')
                elif user.user_type == 'APPLICANT':
                    return redirect('applicant_dashboard')
                elif user.user_type == 'INTERVIEWER':
                    return redirect('interviewer_dashboard')
                elif user.user_type == 'PROGRAM_DIRECTOR':
                    return redirect('director_dashboard')
                else:
                    return redirect('home')
            else:
                messages.error(request, 'Your account is pending approval.')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'users/login.html')

@login_required
def user_logout(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('home')

def is_gme_staff(user):
    return user.is_authenticated and user.user_type == 'GME_STAFF'

def is_applicant(user):
    return user.is_authenticated and user.user_type == 'APPLICANT'

def is_interviewer(user):
    return user.is_authenticated and (user.user_type == 'INTERVIEWER' or user.user_type == 'PROGRAM_DIRECTOR')

def is_program_director(user):
    return user.is_authenticated and user.user_type == 'PROGRAM_DIRECTOR'

def error_403(request, exception):
    return render(request, 'users/error.html', {
        'error_code': '403',
        'error_title': 'Access Denied',
        'error_message': 'You do not have permission to access this page.',
    }, status=403)

def error_404(request, exception):
    return render(request, 'users/error.html', {
        'error_code': '404',
        'error_title': 'Page Not Found',
        'error_message': 'The page you are looking for does not exist.',
    }, status=404)

def error_500(request):
    return render(request, 'users/error.html', {
        'error_code': '500',
        'error_title': 'Server Error',
        'error_message': 'An internal server error occurred. Please try again later.',
    }, status=500)

class RoleRequiredMixin:
    @classmethod
    def as_view(cls, **initkwargs):
        view = super().as_view(**initkwargs)
        return login_required(user_passes_test(cls.role_test)(view))

def check_role_access(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
            
        allowed = False
        view_name = request.resolver_match.url_name
        user_type = request.user.user_type

        role_access_map = {
            'dashboard': ['GME_STAFF'],
            'applicant_dashboard': ['APPLICANT'],
            'interviewer_dashboard': ['INTERVIEWER', 'PROGRAM_DIRECTOR'],
            'director_dashboard': ['PROGRAM_DIRECTOR'],
            'manage_programs': ['GME_STAFF'],
            'approve_staff': ['GME_STAFF'],
            'conduct_interview': ['INTERVIEWER', 'PROGRAM_DIRECTOR'],
            'view_interview_results': ['PROGRAM_DIRECTOR'],
            'submit_final_score': ['PROGRAM_DIRECTOR'],
            'director_bulk_update': ['PROGRAM_DIRECTOR'],
            'view_application': ['GME_STAFF'],
            'edit_program': ['GME_STAFF'],
            'delete_program': ['GME_STAFF'],
            'update_application_status': ['GME_STAFF'],
            'create_program': ['GME_STAFF'],
            'bulk_update_status': ['GME_STAFF'],
            'upload_scores': ['GME_STAFF'],
            'process_scores': ['GME_STAFF'],
            'export_applications': ['GME_STAFF'],
            'bulk_send_email': ['GME_STAFF'],
            'bulk_actions': ['GME_STAFF'],
            'edit_application': ['APPLICANT'],
            'submit_draft': ['APPLICANT']
        }

        if view_name in role_access_map:
            allowed = user_type in role_access_map[view_name]

        if not allowed:
            raise PermissionDenied("You don't have permission to access this page.")

        return view_func(request, *args, **kwargs)
    return _wrapped_view

@login_required
@check_role_access
def dashboard(request):
    pending_staff = User.objects.filter(is_approved=False).exclude(user_type='APPLICANT')
    # Exclude draft applications from being shown to GME staff
    applications = Application.objects.exclude(status='DRAFT')
    
    # Advanced filtering
    filter_form = AdvancedFilterForm(request.GET or None)
    if filter_form.is_valid():
        status = filter_form.cleaned_data.get('status')
        program_type = filter_form.cleaned_data.get('program_type')
        program = filter_form.cleaned_data.get('program')
        gpa = filter_form.cleaned_data.get('gpa')
        min_test_score = filter_form.cleaned_data.get('min_test_score')
        max_test_score = filter_form.cleaned_data.get('max_test_score')
        
        if status:
            applications = applications.filter(status=status)
        
        if program_type:
            applications = applications.filter(program__program_type=program_type)
        
        if program:
            applications = applications.filter(program=program)
        
        if gpa:
            applications = applications.filter(gpa=gpa)
        
        if min_test_score is not None or max_test_score is not None:
            # Filter by test scores from interviews
            applications_with_interviews = applications.filter(interviews__isnull=False).distinct()
            
            if min_test_score is not None:
                applications_with_interviews = applications_with_interviews.filter(
                    interviews__test_score__gte=min_test_score
                )
            
            if max_test_score is not None:
                applications_with_interviews = applications_with_interviews.filter(
                    interviews__test_score__lte=max_test_score
                )
            
            applications = applications_with_interviews
    
    programs = Program.objects.all()
    
    return render(request, 'users/dashboard.html', {
        'pending_staff': pending_staff,
        'applications': applications,
        'programs': programs,
        'filter_form': filter_form
    })

@login_required
@check_role_access
def approve_staff(request, user_id):
    staff = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = StaffApprovalForm(request.POST, instance=staff)
        if form.is_valid():
            form.save()
            messages.success(request, f'Staff account for {staff.username} has been updated.')
            return redirect('dashboard')
    else:
        form = StaffApprovalForm(instance=staff)
    
    return render(request, 'users/approve_staff.html', {'form': form, 'staff': staff})

@login_required
@check_role_access
def manage_programs(request):
    programs = Program.objects.all()
    
    if request.method == 'POST':
        form = ProgramForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Program created successfully.')
            return redirect('manage_programs')
    else:
        form = ProgramForm()
    
    return render(request, 'users/manage_programs.html', {'form': form, 'programs': programs})

@login_required
@check_role_access
def create_program(request):
    if request.method == 'POST':
        form = ProgramForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Program created successfully.')
            return redirect('manage_programs')
    else:
        form = ProgramForm()
    
    return render(request, 'users/create_program.html', {'form': form})

@login_required
@check_role_access
def edit_program(request, program_id):
    program = get_object_or_404(Program, id=program_id)
    
    if request.method == 'POST':
        form = ProgramForm(request.POST, instance=program)
        if form.is_valid():
            form.save()
            messages.success(request, 'Program updated successfully.')
            return redirect('manage_programs')
    else:
        form = ProgramForm(instance=program)
    
    return render(request, 'users/edit_program.html', {'form': form, 'program': program})

@login_required
@check_role_access
def delete_program(request, program_id):
    program = get_object_or_404(Program, id=program_id)
    
    if request.method == 'POST':
        program.delete()
        messages.success(request, 'Program deleted successfully.')
        return redirect('manage_programs')
    
    return render(request, 'users/delete_program.html', {'program': program})

@login_required
@check_role_access
def update_application_status(request, application_id):
    application = get_object_or_404(Application, id=application_id)
    
    # Get file names for display, safely handling empty files
    file_names = {}
    for field_name in ['national_id_document', 'cv', 'payment_receipt', 'university_certificate', 'board_certification']:
        if hasattr(application, field_name) and getattr(application, field_name):
            file_names[field_name] = application.get_file_name(field_name)
        else:
            file_names[field_name] = None
    
    if request.method == 'POST':
        form = ApplicationStatusForm(request.POST, instance=application)
        if form.is_valid():
            form.save()
            messages.success(request, 'Application status updated successfully.')
            return redirect('dashboard')
    else:
        form = ApplicationStatusForm(instance=application)
    
    return render(request, 'users/update_application_status.html', {
        'form': form, 
        'application': application,
        'file_names': file_names
    })

@login_required
@check_role_access
def bulk_update_status(request):
    if request.method == 'POST':
        application_ids = request.POST.getlist('application_ids')
        new_status = request.POST.get('new_status')
        action_type = request.POST.get('action_type')
        
        print(f"DEBUG: POST data: {request.POST}")
        print(f"DEBUG: Bulk action request: action_type={action_type}, application_ids={application_ids}, new_status={new_status}")
        
        if not application_ids:
            messages.error(request, 'Please select at least one application.')
            return redirect('dashboard')
            
        if action_type == 'update_status':
            if new_status:
                try:
                    # Update all selected applications, but exclude any that might be drafts
                    applications_to_update = Application.objects.filter(id__in=application_ids).exclude(status='DRAFT')
                    count = applications_to_update.count()
                    
                    print(f"DEBUG: Found {count} applications to update to status {new_status}")
                    
                    if count > 0:
                        updated = applications_to_update.update(status=new_status)
                        print(f"DEBUG: Updated {updated} applications to status {new_status}")
                        messages.success(request, f'Successfully updated {count} applications to {new_status}.')
                    else:
                        messages.warning(request, 'No eligible applications were found to update.')
                except Exception as e:
                    print(f"ERROR: {str(e)}")
                    messages.error(request, f'Error updating applications: {str(e)}')
            else:
                messages.error(request, 'Please select a status.')
        elif action_type == 'send_email':
            subject = request.POST.get('email_subject')
            message = request.POST.get('email_message')
            
            if not subject or not message:
                messages.error(request, 'Please provide both subject and message for the email.')
                return redirect('dashboard')
                
            try:
                # Get the applications
                applications = Application.objects.filter(id__in=application_ids).exclude(status='DRAFT')
                recipient_list = [app.applicant.email for app in applications]
                
                if recipient_list:
                    # Send emails
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        recipient_list,
                        fail_silently=False,
                    )
                    
                    messages.success(request, f'Emails sent to {len(recipient_list)} applicants.')
                else:
                    messages.warning(request, 'No valid recipients found.')
            except Exception as e:
                messages.error(request, f'Error sending emails: {str(e)}')
        
        return redirect('dashboard')
    
    return redirect('dashboard')

@login_required
@check_role_access
def upload_scores(request):
    if request.method == 'POST':
        form = BulkScoreUploadForm(request.POST, request.FILES)
        if form.is_valid():
            score_file = request.FILES['score_file']
            
            try:
                # Process the file based on its type
                if score_file.name.endswith('.csv'):
                    # Read CSV with pandas to ensure proper handling of data types
                    df = pd.read_csv(score_file)
                else:  # Excel file
                    df = pd.read_excel(score_file)
                
                # Process each row
                success_count = 0
                error_count = 0
                
                for _, row in df.iterrows():
                    try:
                        # Convert to string to handle any numeric national IDs
                        national_id = str(row['national_id'])
                        
                        # Ensure test_score is read as an integer
                        test_score = int(row['test_score'])
                        
                        # Log the values for debugging
                        logger.info(f"Processing score: National ID={national_id}, Test Score={test_score}")
                        
                        # Use a default value for medical_school_score based on GPA
                        medical_school_score = 0
                        
                        # Check if a score already exists for this national ID
                        existing_score = ApplicantScore.objects.filter(national_id=national_id).first()
                        
                        if existing_score:
                            # Update the existing score with the exact value from the CSV
                            existing_score.test_score = test_score
                            existing_score.uploaded_by = request.user
                            existing_score.is_processed = False  # Mark as unprocessed so it gets processed again
                            existing_score.save()
                            logger.info(f"Updated existing score: {existing_score}")
                        else:
                            # Create a new score with the exact value from the CSV
                            new_score = ApplicantScore.objects.create(
                                national_id=national_id,
                                test_score=test_score,
                                medical_school_score=medical_school_score,
                                uploaded_by=request.user
                            )
                            logger.info(f"Created new score: {new_score}")
                        
                        success_count += 1
                    except Exception as e:
                        logger.error(f"Error processing row: {str(e)}")
                        error_count += 1
                
                # Don't show a success message here, as we're redirecting to process_scores
                # which will show its own message
                return redirect('process_scores')
            
            except Exception as e:
                logger.error(f"Error processing file: {str(e)}")
                messages.error(request, f'Error processing file: {str(e)}')
    else:
        form = BulkScoreUploadForm()
    
    return render(request, 'users/upload_scores.html', {'form': form})

@login_required
@check_role_access
def process_scores(request):
    # Get unprocessed scores
    unprocessed_scores = ApplicantScore.objects.filter(is_processed=False)
    
    success_count = 0
    not_found_count = 0
    total_processed = unprocessed_scores.count()
    
    for score in unprocessed_scores:
        # Find applicants with matching national ID
        try:
            applicant = Applicant.objects.get(national_id=score.national_id)
            user = applicant.user
            
            # Find applications for this user
            applications = Application.objects.filter(applicant=user)
            
            for application in applications:
                # Check if there's an interview record
                interviews = Interview.objects.filter(application=application)
                
                # If no interview exists, create one
                if not interviews.exists():
                    # Determine the form type based on program type
                    form_type = application.program.program_type
                    
                    # Create a new interview record with the exact test score from the CSV
                    interview = Interview.objects.create(
                        application=application,
                        interviewer=User.objects.filter(user_type='GME_STAFF').first(),  # Use a GME staff as default interviewer
                        form_type=form_type,
                        test_score=score.test_score,  # Use the exact score from the CSV
                        medical_school_score=score.medical_school_score
                    )
                    success_count += 1
                else:
                    # Update existing interviews with the exact test score from the CSV
                    for interview in interviews:
                        # Always use the exact test score from the CSV
                        interview.test_score = score.test_score
                        # Keep the existing medical_school_score if it's already set
                        if interview.medical_school_score == 0:
                            interview.medical_school_score = score.medical_school_score
                        interview.save()
                        success_count += 1
            
            # Mark as processed
            score.is_processed = True
            score.save()
            
        except Applicant.DoesNotExist:
            not_found_count += 1
            # Mark as processed even if not found to avoid counting it again in future runs
            score.is_processed = True
            score.save()
    
    # Also update any existing interviews for applicants with processed scores
    # This ensures all interviews have the latest test scores
    processed_scores = ApplicantScore.objects.filter(is_processed=True)
    updated_interviews = 0
    
    for score in processed_scores:
        try:
            applicant = Applicant.objects.get(national_id=score.national_id)
            user = applicant.user
            
            # Find all interviews for this user's applications
            interviews = Interview.objects.filter(application__applicant=user)
            
            for interview in interviews:
                # Always update with the exact test score from the CSV
                if interview.test_score != score.test_score:
                    interview.test_score = score.test_score
                    interview.save()
                    updated_interviews += 1
                    
        except Applicant.DoesNotExist:
            continue
    
    if updated_interviews > 0:
        messages.info(request, f'Additionally updated {updated_interviews} existing interviews with the latest scores.')
    
    if total_processed > 0:
        messages.success(request, f'Successfully uploaded and processed scores. Updated {success_count} interview records. {not_found_count} applicants not found.')
    else:
        messages.info(request, 'No new scores to process. Please upload a file first.')
    
    return redirect('dashboard')

@login_required
@check_role_access
def interviewer_dashboard(request):
    # Get the interviewer's program
    program = request.user.program
    
    if not program:
        messages.error(request, 'You are not assigned to any program.')
        return redirect('home')
    
    # Get applications for the interviewer's program that are invited for interview
    # Exclude draft applications
    applications = Application.objects.filter(
        program=program,
        status='INVITED_FOR_INTERVIEW'
    )
    
    # Get interviews already conducted by this interviewer
    conducted_interviews = Interview.objects.filter(interviewer=request.user)
    conducted_application_ids = conducted_interviews.values_list('application_id', flat=True)
    
    # Separate applications into those already interviewed and those pending
    interviewed_applications = applications.filter(id__in=conducted_application_ids)
    pending_applications = applications.exclude(id__in=conducted_application_ids)
    
    return render(request, 'users/interviewer_dashboard.html', {
        'program': program,
        'pending_applications': pending_applications,
        'interviewed_applications': interviewed_applications
    })

@login_required
@check_role_access
def conduct_interview(request, application_id):
    application = get_object_or_404(Application, id=application_id)
    
    # Verify the application is for the interviewer's program
    if not verify_program_access(request.user, application.program):
        messages.error(request, 'You are not authorized to interview this applicant.')
        return redirect('interviewer_dashboard')
    
    # Check if an interview already exists
    existing_interview = Interview.objects.filter(
        application=application,
        interviewer=request.user
    ).first()
    
    # Check if interview can be modified
    if existing_interview and not check_interview_modification(existing_interview):
        messages.error(request, 'Interview cannot be modified after final score submission.')
        return redirect('interviewer_dashboard')
    
    # Only check application status if this is a new interview
    if not existing_interview and application.status != 'INVITED_FOR_INTERVIEW':
        messages.error(request, 'This applicant is not currently scheduled for an interview.')
        return redirect('interviewer_dashboard')
    
    # Determine which form to use based on program type
    form_class = ResidencyInterviewForm if application.program.program_type == 'RESIDENCY' else FellowshipInterviewForm
    
    # Calculate medical school score based on GPA
    medical_school_score = 0
    if application.gpa == 'EXCELLENT':
        medical_school_score = 10
    elif application.gpa == 'VERY_GOOD':
        medical_school_score = 8
    elif application.gpa == 'GOOD':
        medical_school_score = 6
    elif application.gpa == 'SATISFACTORY':
        medical_school_score = 4
    
    # Try to get the latest test score from applicant scores
    latest_test_score = None
    try:
        applicant = Applicant.objects.get(user=application.applicant)
        applicant_score = ApplicantScore.objects.filter(
            national_id=applicant.national_id
        ).order_by('-uploaded_at').first()
        
        if applicant_score:
            latest_test_score = applicant_score.test_score
            logger.info(f"Found latest test score for {applicant.national_id}: {latest_test_score}")
    except (Applicant.DoesNotExist, Exception) as e:
        logger.error(f"Error getting latest test score: {str(e)}")
        pass
    
    if request.method == 'POST':
        if existing_interview:
            form = form_class(request.POST, instance=existing_interview)
        else:
            form = form_class(request.POST)
        
        if form.is_valid():
            interview = form.save(commit=False)
            interview.application = application
            interview.interviewer = request.user
            interview.form_type = application.program.program_type
            
            # Set medical school score only for Residency programs
            if application.program.program_type == 'RESIDENCY' and not interview.medical_school_score:
                interview.medical_school_score = medical_school_score
            
            # Always update test score with the latest value if available
            if latest_test_score is not None:
                interview.test_score = latest_test_score
                logger.info(f"Setting test score to {latest_test_score} for interview {interview}")
                
            interview.save()
            
            messages.success(request, 'Interview scores saved successfully.')
            
            # Redirect based on user type
            if request.user.user_type == 'PROGRAM_DIRECTOR':
                return redirect('director_dashboard')
            else:
                return redirect('interviewer_dashboard')
    else:
        if existing_interview:
            # If there's an existing interview but we have a newer test score, update it
            if latest_test_score is not None:
                existing_interview.test_score = latest_test_score
                existing_interview.save()
                logger.info(f"Updated existing interview test score to {latest_test_score}")
            
            form = form_class(instance=existing_interview)
        else:
            # Create a new form with initial values
            initial_data = {
                'medical_school_score': medical_school_score
            }
            
            # Use the latest test score if available
            if latest_test_score is not None:
                initial_data['test_score'] = latest_test_score
                logger.info(f"Setting initial test score to {latest_test_score}")
                
            form = form_class(initial=initial_data)
    
    return render(request, 'users/conduct_interview.html', {
        'form': form,
        'application': application,
        'program_type': application.program.program_type
    })

@login_required
@check_role_access
def applicant_dashboard(request):
    try:
        # Check if user has already applied
        existing_application = Application.objects.filter(applicant=request.user).first()
        
        if existing_application:
            # Get file names for display, safely handling empty files
            file_names = {}
            for field_name in ['national_id_document', 'cv', 'payment_receipt', 'university_certificate', 'board_certification']:
                if hasattr(existing_application, field_name) and getattr(existing_application, field_name):
                    file_names[field_name] = existing_application.get_file_name(field_name)
                else:
                    file_names[field_name] = None
            
            return render(request, 'users/applicant_dashboard.html', {
                'application': existing_application,
                'file_names': file_names
            })
        
        if request.method == 'POST':
            form = ApplicationForm(request.POST, request.FILES)
            if form.is_valid():
                # Create the application instance but don't save it yet
                application = form.save(commit=False)
                # Set the applicant
                application.applicant = request.user
                
                # Check if saving as draft
                if 'save_draft' in request.POST:
                    application.status = 'DRAFT'
                    messages.success(request, 'Your application has been saved as a draft.')
                else:
                    application.status = 'SUBMITTED'
                    messages.success(request, 'Your application has been submitted successfully.')
                
                # Handle optional files for fellowship programs
                program_type = form.cleaned_data.get('program_type')
                if program_type == 'FELLOWSHIP':
                    # If these fields are not provided, set them to None to avoid attribute errors
                    if 'payment_receipt' not in request.FILES:
                        application.payment_receipt = None
                    if 'university_certificate' not in request.FILES:
                        application.university_certificate = None
                
                # Now save the application
                application.save()
                return redirect('applicant_dashboard')
        else:
            form = ApplicationForm()
        
        return render(request, 'users/apply.html', {'form': form})
    
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return redirect('home')

@login_required
@check_role_access
def edit_application(request, application_id):
    # Get the application and verify it belongs to the user and is in DRAFT status
    application = get_object_or_404(
        Application, 
        id=application_id, 
        applicant=request.user, 
        status='DRAFT'
    )
    
    if request.method == 'POST':
        form = ApplicationForm(
            request.POST, 
            request.FILES, 
            instance=application
        )
        
        if form.is_valid():
            # Update the application
            application = form.save(commit=False)
            
            # Check if saving as draft or submitting
            if 'save_draft' in request.POST:
                application.status = 'DRAFT'
                messages.success(request, 'Your draft application has been updated.')
            else:
                application.status = 'SUBMITTED'
                messages.success(request, 'Your application has been submitted successfully.')
            
            # Handle optional files for fellowship programs
            if application.program.program_type == 'FELLOWSHIP':
                # Keep existing files if no new ones were uploaded
                if 'payment_receipt' not in request.FILES:
                    application.payment_receipt = application.payment_receipt
                if 'university_certificate' not in request.FILES:
                    application.university_certificate = application.university_certificate
            
            application.save()
            return redirect('applicant_dashboard')
    else:
        # Initialize the form with the existing application data
        initial_data = {
            'program_type': application.program.program_type,
        }
        form = ApplicationForm(instance=application, initial=initial_data)
    
    return render(request, 'users/apply.html', {
        'form': form,
        'application': application,
        'is_edit': True
    })

@login_required
@check_role_access
def submit_draft(request, application_id):
    application = get_object_or_404(Application, id=application_id, applicant=request.user, status='DRAFT')
    
    if request.method == 'POST':
        application.status = 'SUBMITTED'
        application.save()
        messages.success(request, 'Your application has been submitted successfully.')
    
    return redirect('applicant_dashboard')

def load_programs(request):
    program_type = request.GET.get('program_type')
    programs = Program.objects.filter(program_type=program_type, status='ACTIVE')
    return JsonResponse(list(programs.values('id', 'name')), safe=False)

@login_required
@check_role_access
def export_applications(request):
    # Get filtered applications
    filter_form = AdvancedFilterForm(request.GET or None)
    # Exclude draft applications from being exported
    applications = Application.objects.exclude(status='DRAFT')
    
    if filter_form.is_valid():
        status = filter_form.cleaned_data.get('status')
        program_type = filter_form.cleaned_data.get('program_type')
        program = filter_form.cleaned_data.get('program')
        gpa = filter_form.cleaned_data.get('gpa')
        
        if status:
            applications = applications.filter(status=status)
        
        if program_type:
            applications = applications.filter(program__program_type=program_type)
        
        if program:
            applications = applications.filter(program=program)
        
        if gpa:
            applications = applications.filter(gpa=gpa)
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="applications.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Applicant ID', 'Username', 'Email', 'First Name (EN)', 'Second Name (EN)', 'Third Name (EN)', 'Last Name (EN)',
        'First Name (AR)', 'Second Name (AR)', 'Third Name (AR)', 'Last Name (AR)', 'National ID', 'Phone Number',
        'Program', 'Program Type', 'University', 'GPA', 'Status', 'Submission Date', 'Last Updated',
        'Test Score', 'Medical School Score', 'Final Score', 'Final Score Submitted', 'Final Score Notes'
    ])
    
    for app in applications:
        # Get applicant profile data
        try:
            profile = app.applicant.applicant_profile
            first_name_en = profile.first_name_en
            second_name_en = profile.second_name_en
            third_name_en = profile.third_name_en
            last_name_en = profile.last_name_en
            first_name_ar = profile.first_name_ar
            second_name_ar = profile.second_name_ar
            third_name_ar = profile.third_name_ar
            last_name_ar = profile.last_name_ar
            national_id = profile.national_id
        except:
            first_name_en = second_name_en = third_name_en = last_name_en = ""
            first_name_ar = second_name_ar = third_name_ar = last_name_ar = ""
            national_id = ""
        
        # Get test score and medical school score from interviews
        test_score = ""
        medical_school_score = ""
        if app.interviews.exists():
            # Try to get scores from GME staff interview first
            gme_interview = app.interviews.filter(interviewer__user_type='GME_STAFF').first()
            if gme_interview:
                test_score = gme_interview.test_score
                medical_school_score = gme_interview.medical_school_score
            else:
                # If no GME staff interview, use the first interview
                test_score = app.interviews.first().test_score
                medical_school_score = app.interviews.first().medical_school_score
        
        writer.writerow([
            app.id,
            app.applicant.username,
            app.applicant.email,
            first_name_en,
            second_name_en,
            third_name_en,
            last_name_en,
            first_name_ar,
            second_name_ar,
            third_name_ar,
            last_name_ar,
            national_id,
            app.applicant.phone_number,
            app.program.name,
            app.program.get_program_type_display(),
            app.university_name,
            app.get_gpa_display(),
            app.get_status_display(),
            app.created_at.strftime('%Y-%m-%d'),
            app.updated_at.strftime('%Y-%m-%d'),
            test_score,
            medical_school_score,
            app.final_score if app.final_score_submitted else "",
            "Yes" if app.final_score_submitted else "No",
            app.final_score_notes if app.final_score_notes else ""
        ])
    
    return response

@login_required
@check_role_access
def director_dashboard(request):
    # Get the director's program
    program = request.user.program
    
    if not program:
        messages.error(request, 'You are not assigned to any program.')
        return redirect('home')
    
    # Get applications for the director's program that are invited for interview
    applications = Application.objects.filter(
        program=program,  # This ensures director only sees their program's applications
        status='INVITED_FOR_INTERVIEW'
    ).prefetch_related(
        'interviews',
        'interviews__interviewer'
    )
    
    # Get sort direction from query parameters
    sort_direction = request.GET.get('sort', 'desc')  # Default to descending
    
    # Process each application to calculate interview counts and scores
    for application in applications:
        # Calculate interview count (excluding GME staff)
        non_gme_interviews = [i for i in application.interviews.all() if i.interviewer.user_type != 'GME_STAFF']
        application.interview_count = len(non_gme_interviews)
        
        # Get test score from GME staff interview
        gme_interview = next((i for i in application.interviews.all() if i.interviewer.user_type == 'GME_STAFF'), None)
        application.test_score = gme_interview.test_score if gme_interview else None
        
        # Calculate average score
        if non_gme_interviews:
            total_score = sum(interview.get_total_score() for interview in non_gme_interviews)
            application.average_score = total_score / len(non_gme_interviews)
        else:
            application.average_score = None
    
    # Split applications based on final score submission rather than interview status
    interviewed_applications = [app for app in applications if app.final_score_submitted]
    pending_applications = [app for app in applications if not app.final_score_submitted]
    
    # Sort applications by average score
    if sort_direction == 'asc':
        pending_applications.sort(key=lambda x: x.average_score if x.average_score is not None else -1)
        interviewed_applications.sort(key=lambda x: x.average_score if x.average_score is not None else -1)
    else:  # desc
        pending_applications.sort(key=lambda x: x.average_score if x.average_score is not None else -1, reverse=True)
        interviewed_applications.sort(key=lambda x: x.average_score if x.average_score is not None else -1, reverse=True)
    
    return render(request, 'users/director_dashboard.html', {
        'program': program,
        'pending_applications': pending_applications,
        'interviewed_applications': interviewed_applications,
        'applications': applications,
        'current_sort': sort_direction
    })

@login_required
@check_role_access
def view_interview_results(request, application_id):
    application = get_object_or_404(Application, id=application_id)
    
    # Verify the application is for the director's program
    if not verify_program_access(request.user, application.program):
        messages.error(request, 'You are not authorized to view this application.')
        return redirect('director_dashboard')
    
    # Get all interviews for this application, excluding GME staff
    interviews = application.interviews.filter(~Q(interviewer__user_type='GME_STAFF'))
    
    # Calculate the average score
    average_score = application.get_average_score()
    
    return render(request, 'users/view_interview_results.html', {
        'application': application,
        'interviews': interviews,
        'average_score': average_score
    })

@login_required
@check_role_access
def submit_final_score(request, application_id):
    application = get_object_or_404(Application, id=application_id)
    
    # Verify the application is for the director's program
    if not verify_program_access(request.user, application.program):
        messages.error(request, 'You are not authorized to submit scores for this application.')
        return redirect('director_dashboard')
    
    # Check if there are any interviews for this application
    if not application.interviews.exists():
        messages.error(request, 'Cannot update status as no interviews have been conducted yet.')
        return redirect('view_interview_results', application_id=application_id)
    
    if request.method == 'POST':
        try:
            # Get the average score automatically
            final_score = application.get_average_score()
            notes = request.POST.get('notes', '')
            status = request.POST.get('status')
            
            if status in ['APPROVED', 'REJECTED', 'WAIT_LISTED']:
                # Submit final score and update status in one step
                application.submit_final_score(final_score, notes)
                application.status = status
                application.save()
                
                # Convert WAIT_LISTED to Waitlisted with no space
                status_display = status.replace('_', ' ').title()
                if status == 'WAIT_LISTED':
                    status_display = 'Waitlisted'
                
                messages.success(request, f'Application status updated to {status_display}.')
                return redirect('view_interview_results', application_id=application_id)
            else:
                messages.error(request, 'Please select a valid status (Approved, Rejected, or Waitlisted).')
        except (ValueError, TypeError):
            messages.error(request, 'An error occurred while updating the application status.')
    
    return redirect('view_interview_results', application_id=application_id)

@login_required
@check_role_access
def view_application(request, application_id):
    application = get_object_or_404(Application, id=application_id)
    
    # Get file names for display, safely handling empty files
    file_names = {}
    for field_name in ['national_id_document', 'cv', 'payment_receipt', 'university_certificate', 'board_certification']:
        if hasattr(application, field_name) and getattr(application, field_name):
            file_names[field_name] = application.get_file_name(field_name)
        else:
            file_names[field_name] = None
    
    return render(request, 'users/view_application.html', {
        'application': application,
        'file_names': file_names
    })

@login_required
def download_application_file(request, application_id, file_type):
    """
    View to handle secure file downloads
    """
    application = get_object_or_404(Application, id=application_id)
    
    # Check if user has permission to access the file
    if not can_access_file(request.user, application):
        raise PermissionDenied("You don't have permission to access this file")
    
    # Map of valid file types to their model fields
    file_map = {
        'cv': 'cv',
        'national_id': 'national_id_document',
        'payment': 'payment_receipt',
        'university': 'university_certificate',
        'board': 'board_certification'
    }
    
    if file_type not in file_map:
        raise Http404("Invalid file type")
    
    file_field = getattr(application, file_map[file_type])
    if not file_field:
        raise Http404("File not found")
    
    try:
        response = FileResponse(file_field)
        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_field.name)}"'
        return response
    except Exception as e:
        logger.error(f"Error downloading file: {str(e)}")
        raise Http404("Error accessing file")

@login_required
@check_role_access
def director_bulk_update(request):
    if request.method == 'POST':
        application_ids = request.POST.getlist('application_ids')
        new_status = request.POST.get('new_status')
        
        # Validate that at least one application is selected
        if not application_ids:
            messages.error(request, 'Please select at least one application.')
            return redirect('director_dashboard')
            
        # Validate new status
        if new_status not in ['APPROVED', 'REJECTED', 'WAIT_LISTED']:
            messages.error(request, 'Invalid status selected.')
            return redirect('director_dashboard')
        
        try:
            # Get the program associated with the director
            program = Program.objects.get(director=request.user)
            
            # Get applications that belong to the director's program
            applications = Application.objects.filter(
                id__in=application_ids,
                program=program
            )
            
            if not applications.exists():
                messages.error(request, 'No eligible applications found.')
                return redirect('director_dashboard')
                
            updated_count = 0
            for application in applications:
                # Only update if the application is in INVITED_FOR_INTERVIEW status
                if application.status == 'INVITED_FOR_INTERVIEW':
                    application.status = new_status
                    application.final_score_submitted = True
                    application.save()
                    updated_count += 1
            
            if updated_count == 0:
                messages.warning(request, 'No applications were updated. Ensure applications have been interviewed.')
            elif updated_count == 1:
                messages.success(request, f'1 application was updated to {dict(Application.STATUS_CHOICES)[new_status]}.')
            else:
                messages.success(request, f'{updated_count} applications were updated to {dict(Application.STATUS_CHOICES)[new_status]}.')
                
        except Program.DoesNotExist:
            messages.error(request, 'You are not assigned to any program.')
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            
    return redirect('director_dashboard')
