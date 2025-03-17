from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q, F, Sum
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
        form = ApplicantRegistrationForm(request.POST)
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
                elif user.user_type == 'INTERVIEWER' or user.user_type == 'PROGRAM_DIRECTOR':
                    return redirect('interviewer_dashboard')
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

@login_required
@user_passes_test(is_gme_staff)
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
@user_passes_test(is_gme_staff)
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
@user_passes_test(is_gme_staff)
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
@user_passes_test(is_gme_staff)
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
@user_passes_test(is_gme_staff)
def delete_program(request, program_id):
    program = get_object_or_404(Program, id=program_id)
    
    if request.method == 'POST':
        program.delete()
        messages.success(request, 'Program deleted successfully.')
        return redirect('manage_programs')
    
    return render(request, 'users/delete_program.html', {'program': program})

@login_required
@user_passes_test(is_gme_staff)
def update_application_status(request, application_id):
    application = get_object_or_404(Application, id=application_id)
    
    # Get file names for display
    file_names = {
        'national_id_document': application.get_file_name('national_id_document'),
        'cv': application.get_file_name('cv'),
        'payment_receipt': application.get_file_name('payment_receipt'),
        'university_certificate': application.get_file_name('university_certificate'),
    }
    
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
@user_passes_test(is_gme_staff)
def bulk_email(request):
    # Exclude draft applications from bulk emails
    applications = Application.objects.exclude(status='DRAFT')
    
    # Apply filters if provided
    status_filter = request.GET.get('status')
    program_filter = request.GET.get('program')
    
    if status_filter:
        applications = applications.filter(status=status_filter)
    
    if program_filter:
        applications = applications.filter(program_id=program_filter)
    
    if request.method == 'POST':
        form = BulkEmailForm(request.POST, queryset=applications)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            selected_applications = form.cleaned_data['applications']
            
            recipient_list = [app.applicant.email for app in selected_applications]
            
            # Send emails
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                recipient_list,
                fail_silently=False,
            )
            
            messages.success(request, f'Emails sent to {len(recipient_list)} applicants.')
            return redirect('dashboard')
    else:
        form = BulkEmailForm(queryset=applications)
    
    return render(request, 'users/bulk_email.html', {'form': form})

@login_required
@user_passes_test(is_gme_staff)
def bulk_update_status(request):
    if request.method == 'POST':
        application_ids = request.POST.getlist('application_ids')
        new_status = request.POST.get('new_status')
        
        if application_ids and new_status:
            # Update all selected applications, but exclude any that might be drafts
            Application.objects.filter(id__in=application_ids).exclude(status='DRAFT').update(status=new_status)
            messages.success(request, f'Successfully updated applications to {new_status}.')
        else:
            messages.error(request, 'Please select applications and a status.')
        
        return redirect('dashboard')
    
    return redirect('dashboard')

@login_required
@user_passes_test(is_gme_staff)
def upload_scores(request):
    if request.method == 'POST':
        form = BulkScoreUploadForm(request.POST, request.FILES)
        if form.is_valid():
            score_file = request.FILES['score_file']
            
            try:
                # Process the file based on its type
                if score_file.name.endswith('.csv'):
                    df = pd.read_csv(score_file)
                else:  # Excel file
                    df = pd.read_excel(score_file)
                
                # Process each row
                success_count = 0
                error_count = 0
                
                for _, row in df.iterrows():
                    try:
                        national_id = str(row['national_id'])
                        test_score = int(row['test_score'])
                        # Use a default value for medical_school_score based on GPA
                        medical_school_score = 0
                        
                        # Create or update the score
                        ApplicantScore.objects.create(
                            national_id=national_id,
                            test_score=test_score,
                            medical_school_score=medical_school_score,
                            uploaded_by=request.user
                        )
                        success_count += 1
                    except Exception as e:
                        error_count += 1
                
                messages.success(request, f'Successfully processed {success_count} scores. {error_count} errors.')
                return redirect('dashboard')
            
            except Exception as e:
                messages.error(request, f'Error processing file: {str(e)}')
    else:
        form = BulkScoreUploadForm()
    
    return render(request, 'users/upload_scores.html', {'form': form})

@login_required
@user_passes_test(is_gme_staff)
def process_scores(request):
    # Get unprocessed scores
    unprocessed_scores = ApplicantScore.objects.filter(is_processed=False)
    
    success_count = 0
    not_found_count = 0
    
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
                    
                    # Create a new interview record
                    interview = Interview.objects.create(
                        application=application,
                        interviewer=User.objects.filter(user_type='GME_STAFF').first(),  # Use a GME staff as default interviewer
                        form_type=form_type,
                        test_score=score.test_score,
                        medical_school_score=score.medical_school_score
                    )
                    success_count += 1
                else:
                    # Update existing interviews
                    for interview in interviews:
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
    
    messages.success(request, f'Updated {success_count} interview records. {not_found_count} applicants not found.')
    return redirect('dashboard')

@login_required
@user_passes_test(is_interviewer)
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
@user_passes_test(is_interviewer)
def conduct_interview(request, application_id):
    application = get_object_or_404(Application, id=application_id)
    
    # Verify the application is for the interviewer's program
    if application.program != request.user.program:
        messages.error(request, 'You are not authorized to interview this applicant.')
        return redirect('interviewer_dashboard')
    
    # Check if the application status is 'INVITED_FOR_INTERVIEW'
    if application.status != 'INVITED_FOR_INTERVIEW':
        messages.error(request, 'This applicant is not currently scheduled for an interview.')
        return redirect('interviewer_dashboard')
    
    # Check if an interview already exists
    existing_interview = Interview.objects.filter(
        application=application,
        interviewer=request.user
    ).first()
    
    # Determine which form to use based on program type
    form_class = ResidencyInterviewForm if application.program.program_type == 'RESIDENCY' else FellowshipInterviewForm
    
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
            interview.save()
            
            messages.success(request, 'Interview scores saved successfully.')
            return redirect('interviewer_dashboard')
    else:
        if existing_interview:
            form = form_class(instance=existing_interview)
        else:
            form = form_class()
    
    return render(request, 'users/conduct_interview.html', {
        'form': form,
        'application': application,
        'program_type': application.program.program_type
    })

@login_required
@user_passes_test(is_applicant)
def applicant_dashboard(request):
    try:
        # Check if user has already applied
        existing_application = Application.objects.filter(applicant=request.user).first()
        
        if existing_application:
            # Get file names for display
            file_names = {
                'national_id_document': existing_application.get_file_name('national_id_document'),
                'cv': existing_application.get_file_name('cv'),
                'payment_receipt': existing_application.get_file_name('payment_receipt'),
                'university_certificate': existing_application.get_file_name('university_certificate'),
            }
            
            return render(request, 'users/applicant_dashboard.html', {
                'application': existing_application,
                'file_names': file_names
            })
        
        if request.method == 'POST':
            form = ApplicationForm(request.POST, request.FILES)
            if form.is_valid():
                application = form.save(commit=False)
                application.applicant = request.user
                
                # Check if saving as draft
                if 'save_draft' in request.POST:
                    application.status = 'DRAFT'
                    messages.success(request, 'Your application has been saved as a draft.')
                else:
                    application.status = 'SUBMITTED'
                    messages.success(request, 'Your application has been submitted successfully.')
                
                application.save()
                return redirect('applicant_dashboard')
        else:
            form = ApplicationForm()
        
        return render(request, 'users/apply.html', {'form': form})
    
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return redirect('home')

@login_required
@user_passes_test(is_applicant)
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
@user_passes_test(is_gme_staff)
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
        'Applicant', 'Email', 'Program', 'University', 'GPA', 'Status', 
        'Submission Date', 'Last Updated'
    ])
    
    for app in applications:
        writer.writerow([
            app.applicant.username,
            app.applicant.email,
            app.program.name,
            app.university_name,
            app.get_gpa_display(),
            app.get_status_display(),
            app.created_at.strftime('%Y-%m-%d'),
            app.updated_at.strftime('%Y-%m-%d')
        ])
    
    return response
