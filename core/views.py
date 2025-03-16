from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.db.models import Count

from programs.models import Program
from applications.models import Application
from accounts.models import User

def home_view(request):
    """Home page view"""
    # If user is already logged in, redirect to dashboard
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    
    # Get active programs for display
    residency_programs = Program.objects.filter(
        program_type=Program.PROGRAM_TYPE_RESIDENCY,
        status=Program.STATUS_ACTIVE
    )
    
    fellowship_programs = Program.objects.filter(
        program_type=Program.PROGRAM_TYPE_FELLOWSHIP,
        status=Program.STATUS_ACTIVE
    )
    
    context = {
        'residency_programs': residency_programs,
        'fellowship_programs': fellowship_programs,
    }
    
    return render(request, 'core/home.html', context)

@login_required
def dashboard_view(request):
    """Dashboard view based on user type"""
    user = request.user
    context = {}
    
    if user.is_gme_staff:
        # GME Staff Dashboard
        context['pending_staff_approvals'] = User.objects.filter(
            is_approved=False,
            user_type__in=[
                User.USER_TYPE_PROGRAM_DIRECTOR,
                User.USER_TYPE_INTERVIEWER
            ]
        ).count()
        
        context['total_applications'] = Application.objects.count()
        context['pending_applications'] = Application.objects.filter(
            status=Application.STATUS_SUBMITTED
        ).count()
        
        context['program_stats'] = Program.objects.values('program_type').annotate(
            count=Count('id')
        )
        
        context['application_stats'] = Application.objects.values('status').annotate(
            count=Count('id')
        )
        
    elif user.is_program_director or user.is_interviewer:
        # Program Director/Interviewer Dashboard
        if user.department:
            context['department_programs'] = Program.objects.filter(
                department=user.department,
                status=Program.STATUS_ACTIVE
            )
            
            context['department_applications'] = Application.objects.filter(
                program__department=user.department
            )
    
    elif user.is_applicant:
        # Applicant Dashboard
        try:
            context['application'] = Application.objects.get(user=user)
        except Application.DoesNotExist:
            context['application'] = None
        
        context['available_programs'] = Program.objects.filter(
            status=Program.STATUS_ACTIVE
        )
    
    return render(request, 'core/dashboard.html', context)
