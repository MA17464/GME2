from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    # User types
    USER_TYPE_GME_STAFF = 'gme_staff'
    USER_TYPE_PROGRAM_DIRECTOR = 'program_director'
    USER_TYPE_INTERVIEWER = 'interviewer'
    USER_TYPE_APPLICANT = 'applicant'
    
    USER_TYPE_CHOICES = [
        (USER_TYPE_GME_STAFF, _('GME Staff')),
        (USER_TYPE_PROGRAM_DIRECTOR, _('Program Director')),
        (USER_TYPE_INTERVIEWER, _('Interviewer')),
        (USER_TYPE_APPLICANT, _('Applicant')),
    ]
    
    # Department choices
    DEPARTMENT_INTERNAL_MEDICINE = 'internal_medicine'
    DEPARTMENT_PEDIATRICS = 'pediatrics'
    DEPARTMENT_GENERAL_SURGERY = 'general_surgery'
    DEPARTMENT_RADIATION_ONCOLOGY = 'radiation_oncology'
    DEPARTMENT_PATHOLOGY = 'pathology'
    DEPARTMENT_NUCLEAR_MEDICINE = 'nuclear_medicine'
    DEPARTMENT_DIAGNOSTIC_RADIOLOGY = 'diagnostic_radiology'
    DEPARTMENT_ANESTHESIA = 'anesthesia'
    
    DEPARTMENT_CHOICES = [
        (DEPARTMENT_INTERNAL_MEDICINE, _('Internal Medicine Department')),
        (DEPARTMENT_PEDIATRICS, _('Pediatrics Department')),
        (DEPARTMENT_GENERAL_SURGERY, _('General Surgery Department')),
        (DEPARTMENT_RADIATION_ONCOLOGY, _('Radiation Oncology Department')),
        (DEPARTMENT_PATHOLOGY, _('Pathology and Laboratory Medicine Department')),
        (DEPARTMENT_NUCLEAR_MEDICINE, _('Nuclear Medicine Department')),
        (DEPARTMENT_DIAGNOSTIC_RADIOLOGY, _('Diagnostic Radiology Department')),
        (DEPARTMENT_ANESTHESIA, _('Anesthesia Department')),
    ]
    
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default=USER_TYPE_APPLICANT,
    )
    
    department = models.CharField(
        max_length=30,
        choices=DEPARTMENT_CHOICES,
        blank=True,
        null=True,
    )
    
    is_approved = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    national_id = models.CharField(max_length=20, blank=True, null=True)
    
    # Additional fields for applicants
    first_name_arabic = models.CharField(max_length=50, blank=True, null=True)
    second_name_arabic = models.CharField(max_length=50, blank=True, null=True)
    third_name_arabic = models.CharField(max_length=50, blank=True, null=True)
    last_name_arabic = models.CharField(max_length=50, blank=True, null=True)
    
    def __str__(self):
        return self.username
    
    @property
    def is_khcc_staff(self):
        return self.user_type in [
            self.USER_TYPE_GME_STAFF,
            self.USER_TYPE_PROGRAM_DIRECTOR,
            self.USER_TYPE_INTERVIEWER
        ]
    
    @property
    def is_gme_staff(self):
        return self.user_type == self.USER_TYPE_GME_STAFF
    
    @property
    def is_program_director(self):
        return self.user_type == self.USER_TYPE_PROGRAM_DIRECTOR
    
    @property
    def is_interviewer(self):
        return self.user_type == self.USER_TYPE_INTERVIEWER
    
    @property
    def is_applicant(self):
        return self.user_type == self.USER_TYPE_APPLICANT
    
    @property
    def full_name_english(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name_arabic(self):
        if all([self.first_name_arabic, self.last_name_arabic]):
            return f"{self.first_name_arabic} {self.last_name_arabic}"
        return self.full_name_english
