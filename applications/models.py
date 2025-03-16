from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from programs.models import Program

def document_upload_path(instance, filename):
    """Generate a path for document uploads"""
    return f'documents/{instance.application.user.id}/{instance.document_type}/{filename}'

class Application(models.Model):
    # Application status
    STATUS_SUBMITTED = 'submitted'
    STATUS_ELIGIBLE = 'eligible'
    STATUS_NOT_ELIGIBLE = 'not_eligible'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    
    STATUS_CHOICES = [
        (STATUS_SUBMITTED, _('Submitted')),
        (STATUS_ELIGIBLE, _('Eligible')),
        (STATUS_NOT_ELIGIBLE, _('Not Eligible')),
        (STATUS_APPROVED, _('Approved')),
        (STATUS_REJECTED, _('Rejected')),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='applications')
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='applications')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_SUBMITTED)
    
    # Education information
    university_name = models.CharField(max_length=100)
    gpa = models.DecimalField(max_digits=5, decimal_places=2)
    is_gpa_percentage = models.BooleanField(default=False, help_text=_('If checked, GPA is in percentage. Otherwise, it is on a scale of 4.'))
    
    # Application content
    personal_statement = models.TextField(blank=True, null=True, help_text=_('Explain why you are interested in this program and why you would be a good fit.'))
    additional_info = models.TextField(blank=True, null=True, help_text=_('Any additional information you would like to provide.'))
    
    # Application metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='reviewed_applications'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.program} - {self.get_status_display()}"
    
    @property
    def is_pending_review(self):
        return self.status == self.STATUS_SUBMITTED
    
    @property
    def is_eligible(self):
        return self.status == self.STATUS_ELIGIBLE
    
    @property
    def is_not_eligible(self):
        return self.status == self.STATUS_NOT_ELIGIBLE
    
    @property
    def is_approved(self):
        return self.status == self.STATUS_APPROVED
    
    @property
    def is_rejected(self):
        return self.status == self.STATUS_REJECTED
    
    @property
    def has_all_required_documents(self):
        required_document_types = [
            ApplicationDocument.DOCUMENT_TYPE_NATIONAL_ID,
            ApplicationDocument.DOCUMENT_TYPE_CV,
            ApplicationDocument.DOCUMENT_TYPE_PAYMENT_RECEIPT,
            ApplicationDocument.DOCUMENT_TYPE_UNIVERSITY_CERTIFICATE,
        ]
        
        existing_document_types = self.documents.values_list('document_type', flat=True)
        return all(doc_type in existing_document_types for doc_type in required_document_types)

class ApplicationDocument(models.Model):
    # Document types
    DOCUMENT_TYPE_NATIONAL_ID = 'national_id'
    DOCUMENT_TYPE_CV = 'cv'
    DOCUMENT_TYPE_PAYMENT_RECEIPT = 'payment_receipt'
    DOCUMENT_TYPE_UNIVERSITY_CERTIFICATE = 'university_certificate'
    DOCUMENT_TYPE_OTHER = 'other'
    
    DOCUMENT_TYPE_CHOICES = [
        (DOCUMENT_TYPE_NATIONAL_ID, _('National ID/Identification Card')),
        (DOCUMENT_TYPE_CV, _('Curriculum Vitae (CV)')),
        (DOCUMENT_TYPE_PAYMENT_RECEIPT, _('Payment Receipt')),
        (DOCUMENT_TYPE_UNIVERSITY_CERTIFICATE, _('University Certificate')),
        (DOCUMENT_TYPE_OTHER, _('Other')),
    ]
    
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=30, choices=DOCUMENT_TYPE_CHOICES)
    file = models.FileField(upload_to=document_upload_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.application.user.username} - {self.get_document_type_display()}"
