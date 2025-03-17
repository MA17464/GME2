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
        ('DRAFT', 'Draft'),
        ('SUBMITTED', 'Submitted'),
        ('ELIGIBLE', 'Eligible'),
        ('NOT_ELIGIBLE', 'Not Eligible'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('INVITED_FOR_INTERVIEW', 'Invited for Interview'),
    )
    
    GPA_CHOICES = (
        ('SATISFACTORY', 'Satisfactory'),
        ('GOOD', 'Good'),
        ('VERY_GOOD', 'Very Good'),
        ('EXCELLENT', 'Excellent'),
    )
    
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='applications')
    university_name = models.CharField(max_length=100)
    gpa = models.CharField(max_length=20, choices=GPA_CHOICES)
    
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
    
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='SUBMITTED')
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

class Interview(models.Model):
    FORM_TYPE_CHOICES = (
        ('RESIDENCY', 'Residency'),
        ('FELLOWSHIP', 'Fellowship'),
    )
    
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='interviews')
    interviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conducted_interviews')
    form_type = models.CharField(max_length=20, choices=FORM_TYPE_CHOICES)
    
    # Common scores for both Residency and Fellowship
    professional_appearance = models.PositiveSmallIntegerField(default=0)
    interest = models.PositiveSmallIntegerField(default=0)
    behavior = models.PositiveSmallIntegerField(default=0)
    future_plans = models.PositiveSmallIntegerField(default=0)
    personality = models.PositiveSmallIntegerField(default=0)
    handling_emergencies = models.PositiveSmallIntegerField(default=0)
    professional_attitude = models.PositiveSmallIntegerField(default=0)
    knowledge = models.PositiveSmallIntegerField(default=0)
    research = models.PositiveSmallIntegerField(default=0)
    
    # Additional fields for test scores
    test_score = models.PositiveSmallIntegerField(default=0)
    medical_school_score = models.PositiveSmallIntegerField(default=0)
    
    # Fellowship specific field
    tentative_available_date = models.DateField(null=True, blank=True)
    
    # Meta data
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Interview for {self.application.applicant.username} by {self.interviewer.username}"
    
    def get_total_interview_score(self):
        """Calculate the total interview score based on form type"""
        base_score = (
            self.professional_appearance +
            self.interest +
            self.behavior +
            self.future_plans +
            self.personality +
            self.handling_emergencies +
            self.professional_attitude +
            self.knowledge +
            self.research
        )
        
        if self.form_type == 'RESIDENCY':
            # For Residency: interview score is out of 15
            return min(base_score, 15)
        else:
            # For Fellowship: interview score is out of 50
            return min(base_score, 50)
    
    def get_total_score(self):
        """Calculate the total score including test and medical school scores"""
        interview_score = self.get_total_interview_score()
        
        if self.form_type == 'RESIDENCY':
            # Residency: interview (15) + test (75) + medical school (10) = 100
            return interview_score + self.test_score + self.medical_school_score
        else:
            # Fellowship: interview (50) + test (40) + medical school (10) = 100
            return interview_score + self.test_score + self.medical_school_score

class ApplicantScore(models.Model):
    """Model to store scores uploaded via CSV/Excel for applicants"""
    national_id = models.CharField(max_length=20)
    test_score = models.PositiveSmallIntegerField()
    medical_school_score = models.PositiveSmallIntegerField()
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_scores')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_processed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Score for {self.national_id}: Test={self.test_score}, School={self.medical_school_score}"
