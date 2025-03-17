from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q
from .models import User, Applicant, Program, Application
from .forms import (
    StaffRegistrationForm, ApplicantRegistrationForm, ProgramForm, 
    ApplicationForm, StaffApprovalForm, ApplicationStatusForm, BulkEmailForm
)

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

@login_required
@user_passes_test(is_gme_staff)
def dashboard(request):
    pending_staff = User.objects.filter(is_approved=False).exclude(user_type='APPLICANT')
    applications = Application.objects.all()
    
    # Filter applications
    status_filter = request.GET.get('status')
    program_filter = request.GET.get('program')
    
    if status_filter:
        applications = applications.filter(status=status_filter)
    
    if program_filter:
        applications = applications.filter(program_id=program_filter)
    
    programs = Program.objects.all()
    
    return render(request, 'users/dashboard.html', {
        'pending_staff': pending_staff,
        'applications': applications,
        'programs': programs
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
    applications = Application.objects.all()
    
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
                application.save()
                
                messages.success(request, 'Your application has been submitted successfully.')
                return redirect('applicant_dashboard')
        else:
            form = ApplicationForm()
        
        return render(request, 'users/apply.html', {'form': form})
    
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return redirect('home')

def load_programs(request):
    program_type = request.GET.get('program_type')
    programs = Program.objects.filter(program_type=program_type, status='ACTIVE')
    return JsonResponse(list(programs.values('id', 'name')), safe=False)
