from django.db import models
from django.utils.translation import gettext_lazy as _

class Program(models.Model):
    # Program types
    PROGRAM_TYPE_RESIDENCY = 'residency'
    PROGRAM_TYPE_FELLOWSHIP = 'fellowship'
    
    PROGRAM_TYPE_CHOICES = [
        (PROGRAM_TYPE_RESIDENCY, _('Residency')),
        (PROGRAM_TYPE_FELLOWSHIP, _('Fellowship')),
    ]
    
    # Program status
    STATUS_ACTIVE = 'active'
    STATUS_INACTIVE = 'inactive'
    
    STATUS_CHOICES = [
        (STATUS_ACTIVE, _('Active')),
        (STATUS_INACTIVE, _('Inactive')),
    ]
    
    # Department choices (same as in User model)
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
    
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=30, choices=DEPARTMENT_CHOICES)
    program_type = models.CharField(max_length=20, choices=PROGRAM_TYPE_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    capacity = models.PositiveIntegerField()
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.get_department_display()} - {self.get_program_type_display()}"
    
    @property
    def is_active(self):
        return self.status == self.STATUS_ACTIVE
    
    @property
    def is_residency(self):
        return self.program_type == self.PROGRAM_TYPE_RESIDENCY
    
    @property
    def is_fellowship(self):
        return self.program_type == self.PROGRAM_TYPE_FELLOWSHIP
