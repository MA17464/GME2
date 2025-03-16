from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.utils import timezone
from django.http import JsonResponse
from django.core.mail import send_mass_mail
from django.conf import settings

from .models import Application, ApplicationDocument
from .forms import ApplicationForm, ApplicationDocumentForm, ApplicationStatusForm, BulkEmailForm
from programs.models import Program

class ApplicationCreateView(LoginRequiredMixin, CreateView):
    model = Application
    form_class = ApplicationForm
    template_name = 'applications/application_form.html'
    success_url = reverse_lazy('applications:document_upload')
    
    def dispatch(self, request, *args, **kwargs):
        # Check if user is an applicant
        if not request.user.is_applicant:
            messages.error(request, _('Only applicants can create applications.'))
            return redirect('core:dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        # Check if user already has an application
        if Application.objects.filter(user=self.request.user).exists():
            messages.error(self.request, _('You already have an active application.'))
            return redirect('core:dashboard')
        
        form.instance.user = self.request.user
        messages.success(self.request, _('Application submitted successfully. Please upload required documents.'))
        return super().form_valid(form)
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Add AJAX for dynamic program selection based on program type
        return form
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get program ID from URL parameter
        program_id = self.request.GET.get('program_id')
        if program_id:
            try:
                context['program'] = Program.objects.get(id=program_id)
            except Program.DoesNotExist:
                pass
        return context

@login_required
def get_programs_by_type(request):
    """AJAX view to get programs by type"""
    program_type = request.GET.get('program_type')
    if program_type:
        programs = Program.objects.filter(
            program_type=program_type,
            status=Program.STATUS_ACTIVE
        ).values('id', 'name', 'department')
        return JsonResponse({'programs': list(programs)}, safe=False)
    return JsonResponse({'programs': []}, safe=False)

@login_required
def document_upload_view(request):
    """View for uploading application documents"""
    # Check if user has an application
    try:
        application = Application.objects.get(user=request.user)
    except Application.DoesNotExist:
        messages.error(request, _('You need to create an application first.'))
        return redirect('applications:create')
    
    if request.method == 'POST':
        form = ApplicationDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.application = application
            
            # Check if document of this type already exists
            existing_doc = ApplicationDocument.objects.filter(
                application=application,
                document_type=document.document_type
            ).first()
            
            if existing_doc:
                # Replace the existing document
                existing_doc.file = document.file
                existing_doc.save()
                messages.success(request, _('Document updated successfully.'))
            else:
                document.save()
                messages.success(request, _('Document uploaded successfully.'))
            
            # Check if all required documents are uploaded
            if application.has_all_required_documents:
                messages.info(request, _('All required documents have been uploaded.'))
                return redirect('applications:detail', pk=application.pk)
            
            # Reset the form
            form = ApplicationDocumentForm()
    else:
        form = ApplicationDocumentForm()
    
    # Get existing documents
    documents = ApplicationDocument.objects.filter(application=application)
    
    # Determine which document types are still needed
    required_document_types = [
        ApplicationDocument.DOCUMENT_TYPE_NATIONAL_ID,
        ApplicationDocument.DOCUMENT_TYPE_CV,
        ApplicationDocument.DOCUMENT_TYPE_PAYMENT_RECEIPT,
        ApplicationDocument.DOCUMENT_TYPE_UNIVERSITY_CERTIFICATE,
    ]
    
    existing_document_types = documents.values_list('document_type', flat=True)
    missing_document_types = [
        doc_type for doc_type in required_document_types 
        if doc_type not in existing_document_types
    ]
    
    return render(request, 'applications/document_upload.html', {
        'form': form,
        'documents': documents,
        'application': application,
        'missing_document_types': missing_document_types,
        'required_document_types': dict(ApplicationDocument.DOCUMENT_TYPE_CHOICES),
    })

class ApplicationDetailView(LoginRequiredMixin, DetailView):
    model = Application
    template_name = 'applications/application_detail.html'
    context_object_name = 'application'
    
    def get_queryset(self):
        if self.request.user.is_gme_staff:
            return Application.objects.all()
        return Application.objects.filter(user=self.request.user)

class ApplicationListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Application
    template_name = 'applications/application_list.html'
    context_object_name = 'applications'
    
    def test_func(self):
        return self.request.user.is_gme_staff
    
    def get_queryset(self):
        queryset = Application.objects.all()
        
        # Filter by program if specified
        program_id = self.request.GET.get('program')
        if program_id:
            queryset = queryset.filter(program_id=program_id)
        
        # Filter by status if specified
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['programs'] = Program.objects.all()
        context['statuses'] = Application.STATUS_CHOICES
        return context

@login_required
def update_application_status(request, pk):
    """View for GME staff to update application status"""
    application = get_object_or_404(Application, pk=pk)
    
    # Check permissions
    if not (request.user.is_gme_staff or 
            (request.user.is_program_director and 
             request.user.department == application.program.department)):
        messages.error(request, _('You do not have permission to update application status.'))
        return redirect('core:dashboard')
    
    # Get status from URL parameter if provided
    status = request.GET.get('status')
    
    if request.method == 'POST':
        form = ApplicationStatusForm(request.POST, instance=application)
        if form.is_valid():
            app = form.save(commit=False)
            app.reviewed_by = request.user
            app.reviewed_at = timezone.now()
            app.save()
            
            messages.success(request, _('Application status updated successfully.'))
            
            # Handle AJAX requests
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'status': app.status,
                    'status_display': app.get_status_display()
                })
            
            # Redirect based on user role
            if request.user.is_program_director:
                return redirect('applications:program_applications', program_id=application.program.id)
            else:
                return redirect('applications:list')
    else:
        # If status is provided in URL, pre-fill the form
        initial_data = {}
        if status in dict(Application.STATUS_CHOICES):
            initial_data = {'status': status}
        form = ApplicationStatusForm(instance=application, initial=initial_data)
    
    return render(request, 'applications/update_status.html', {
        'form': form,
        'application': application,
    })

@login_required
def bulk_email_view(request):
    """View for GME staff to send bulk emails to applicants"""
    if not request.user.is_gme_staff:
        messages.error(request, _('You do not have permission to send bulk emails.'))
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        form = BulkEmailForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            applications = form.cleaned_data['applications']
            
            # Prepare emails
            emails = []
            for application in applications:
                user_email = application.user.email
                if user_email:
                    emails.append((
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [user_email]
                    ))
            
            # Send emails
            if emails:
                send_mass_mail(emails)
                messages.success(request, _(f'Emails sent to {len(emails)} applicants.'))
            else:
                messages.warning(request, _('No valid email addresses found.'))
            
            return redirect('applications:list')
    else:
        # Pre-select applications based on filters
        applications = Application.objects.all()
        
        # Apply filters if provided
        program_id = request.GET.get('program')
        if program_id:
            applications = applications.filter(program_id=program_id)
        
        status = request.GET.get('status')
        if status:
            applications = applications.filter(status=status)
        
        form = BulkEmailForm(initial={'applications': applications})
    
    return render(request, 'applications/bulk_email.html', {
        'form': form,
        'programs': Program.objects.all(),
        'statuses': Application.STATUS_CHOICES,
    })

class ProgramApplicationsListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """View for program directors to see applications for a specific program"""
    model = Application
    template_name = 'applications/application_list.html'
    context_object_name = 'applications'
    
    def test_func(self):
        # Only program directors for this department can view
        program = get_object_or_404(Program, pk=self.kwargs.get('program_id'))
        return (self.request.user.is_gme_staff or 
                (self.request.user.is_program_director and 
                 self.request.user.department == program.department))
    
    def get_queryset(self):
        program_id = self.kwargs.get('program_id')
        return Application.objects.filter(program_id=program_id)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        program_id = self.kwargs.get('program_id')
        context['program'] = get_object_or_404(Program, pk=program_id)
        context['statuses'] = Application.STATUS_CHOICES
        context['program_id'] = program_id  # Add this to help with navigation
        return context

@login_required
def delete_document(request, document_id):
    """View for deleting application documents"""
    document = get_object_or_404(ApplicationDocument, id=document_id)
    
    # Check if the user owns the document
    if document.application.user != request.user and not request.user.is_gme_staff:
        messages.error(request, _('You do not have permission to delete this document.'))
        return redirect('core:dashboard')
    
    document_type = document.get_document_type_display()
    document.delete()
    
    messages.success(request, _(f'Document "{document_type}" deleted successfully.'))
    
    return redirect('applications:document_upload')
