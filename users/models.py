from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, MinLengthValidator
import os
from uuid import uuid4

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('GME_STAFF', 'GME Staff'),
        ('PROGRAM_DIRECTOR', 'Program Director'),
        ('INTERVIEWER', 'Interviewer'),
        ('APPLICANT', 'Applicant'),
    )
    
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    phone_number = models.CharField(max_length=15, blank=True)
    is_approved = models.BooleanField(default=False)
    program = models.ForeignKey('Program', on_delete=models.SET_NULL, null=True, blank=True, related_name='staff_members')
    
    def save(self, *args, **kwargs):
        # Auto-approve applicants
        if self.user_type == 'APPLICANT':
            self.is_approved = True
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"

class Applicant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='applicant_profile')
    first_name_en = models.CharField(max_length=50)
    second_name_en = models.CharField(max_length=50)
    third_name_en = models.CharField(max_length=50)
    last_name_en = models.CharField(max_length=50)
    first_name_ar = models.CharField(max_length=50)
    second_name_ar = models.CharField(max_length=50)
    third_name_ar = models.CharField(max_length=50)
    last_name_ar = models.CharField(max_length=50)
    national_id = models.CharField(max_length=20, unique=True)
    
    def __str__(self):
        return f"{self.first_name_en} {self.last_name_en}"

class Program(models.Model):
    PROGRAM_TYPE_CHOICES = (
        ('RESIDENCY', 'Residency'),
        ('FELLOWSHIP', 'Fellowship'),
    )
    
    STATUS_CHOICES = (
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
    )
    
    name = models.CharField(max_length=100, validators=[MinLengthValidator(3)])
    program_type = models.CharField(max_length=20, choices=PROGRAM_TYPE_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ACTIVE')
    capacity = models.PositiveIntegerField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_program_type_display()})"

def get_file_path(instance, filename):
    """
    Generate a unique file path for uploaded documents.
    Format: documents/[document_type]/[username]_[uuid].[extension]
    """
    # Get the file extension
    ext = filename.split('.')[-1]
    # Generate a unique filename with username and uuid
    filename = f"{instance.applicant.username}_{uuid4().hex}.{ext}"
    
    # Determine the folder based on the field name that's currently being processed
    field_name = getattr(instance, '_current_field', None)
    if field_name:
        return os.path.join('documents', field_name, filename)
    
    return os.path.join('documents', 'other', filename)

class Application(models.Model):
    STATUS_CHOICES = (
        ('SUBMITTED', 'Submitted'),
        ('ELIGIBLE', 'Eligible'),
        ('NOT_ELIGIBLE', 'Not Eligible'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )
    
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='applications')
    university_name = models.CharField(max_length=100)
    gpa = models.FloatField()
    
    # Define a custom upload_to function for each field
    def national_id_upload_path(instance, filename):
        ext = filename.split('.')[-1]
        filename = f"{instance.applicant.username}_{uuid4().hex}.{ext}"
        return os.path.join('documents', 'national_id', filename)
    
    def cv_upload_path(instance, filename):
        ext = filename.split('.')[-1]
        filename = f"{instance.applicant.username}_{uuid4().hex}.{ext}"
        return os.path.join('documents', 'cv', filename)
    
    def payment_upload_path(instance, filename):
        ext = filename.split('.')[-1]
        filename = f"{instance.applicant.username}_{uuid4().hex}.{ext}"
        return os.path.join('documents', 'payment', filename)
    
    def certificate_upload_path(instance, filename):
        ext = filename.split('.')[-1]
        filename = f"{instance.applicant.username}_{uuid4().hex}.{ext}"
        return os.path.join('documents', 'certificates', filename)
    
    # Use the specific upload path functions for each field
    national_id_document = models.FileField(upload_to=national_id_upload_path)
    cv = models.FileField(upload_to=cv_upload_path)
    payment_receipt = models.FileField(upload_to=payment_upload_path)
    university_certificate = models.FileField(upload_to=certificate_upload_path)
    
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='SUBMITTED')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('applicant', 'program')
    
    def __str__(self):
        return f"{self.applicant.username} - {self.program.name} ({self.get_status_display()})"
    
    def get_file_name(self, field_name):
        """
        Get the original filename from a file field
        """
        field = getattr(self, field_name)
        if field:
            path = field.name
            # Extract just the filename without the path
            filename = os.path.basename(path)
            
            # Map field names to human-readable document types
            document_types = {
                'national_id_document': 'National ID',
                'cv': 'CV',
                'payment_receipt': 'Payment Receipt',
                'university_certificate': 'University Certificate'
            }
            
            # Return a user-friendly document name
            return f"{document_types.get(field_name, 'Document')}"
        return None
