from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import EmailValidator, FileExtensionValidator
from django.core.exceptions import ValidationError
from .models import User, Applicant, Program, Application, Interview, ApplicantScore
import csv
import io
import os

def validate_file_size(value):
    filesize = value.size
    if filesize > 10 * 1024 * 1024:  # 10MB
        raise ValidationError("Maximum file size is 10MB")

class KHCCEmailValidator(EmailValidator):
    def validate_domain_part(self, domain_part):
        return domain_part.lower() == 'khcc.jo'

class StaffRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        validators=[KHCCEmailValidator(message="KHCC staff must use an email with @khcc.jo domain")]
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'user_type', 'program', 'phone_number')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user_type'].choices = [
            choice for choice in User.USER_TYPE_CHOICES 
            if choice[0] != 'APPLICANT'
        ]
        
        # Make program field not required initially
        self.fields['program'].required = False
        self.fields['program'].queryset = Program.objects.filter(status='ACTIVE')
        
    def clean(self):
        cleaned_data = super().clean()
        user_type = cleaned_data.get('user_type')
        program = cleaned_data.get('program')
        
        if user_type in ['PROGRAM_DIRECTOR', 'INTERVIEWER'] and not program:
            self.add_error('program', 'Program is required for Program Director and Interviewer roles')
            
        return cleaned_data

class ApplicantRegistrationForm(UserCreationForm):
    first_name_en = forms.CharField(max_length=50)
    second_name_en = forms.CharField(max_length=50)
    third_name_en = forms.CharField(max_length=50)
    last_name_en = forms.CharField(max_length=50)
    first_name_ar = forms.CharField(max_length=50)
    second_name_ar = forms.CharField(max_length=50)
    third_name_ar = forms.CharField(max_length=50)
    last_name_ar = forms.CharField(max_length=50)
    national_id = forms.CharField(max_length=20)
    phone_number = forms.CharField(max_length=15)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'phone_number')
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'APPLICANT'
        
        if commit:
            user.save()
            Applicant.objects.create(
                user=user,
                first_name_en=self.cleaned_data['first_name_en'],
                second_name_en=self.cleaned_data['second_name_en'],
                third_name_en=self.cleaned_data['third_name_en'],
                last_name_en=self.cleaned_data['last_name_en'],
                first_name_ar=self.cleaned_data['first_name_ar'],
                second_name_ar=self.cleaned_data['second_name_ar'],
                third_name_ar=self.cleaned_data['third_name_ar'],
                last_name_ar=self.cleaned_data['last_name_ar'],
                national_id=self.cleaned_data['national_id']
            )
        
        return user

class ProgramForm(forms.ModelForm):
    class Meta:
        model = Program
        fields = ('name', 'program_type', 'start_date', 'end_date', 'status')
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name and len(name.strip()) < 3:
            raise forms.ValidationError("Program name must be at least 3 characters long.")
        return name.strip()

class ApplicationForm(forms.ModelForm):
    program_type = forms.ChoiceField(choices=Program.PROGRAM_TYPE_CHOICES)
    program = forms.ModelChoiceField(queryset=Program.objects.none())
    
    class Meta:
        model = Application
        fields = ['program', 'university_name', 'gpa', 'national_id_document', 'cv', 'payment_receipt', 'university_certificate']
        widgets = {
            'program': forms.Select(attrs={'class': 'form-select'}),
            'university_name': forms.TextInput(attrs={'class': 'form-control'}),
            'gpa': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['program'].queryset = Program.objects.filter(status='ACTIVE')
        
        # Add file validation to all file fields
        for field in ['national_id_document', 'cv', 'payment_receipt', 'university_certificate']:
            self.fields[field].validators = [
                FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png']),
                validate_file_size
            ]
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png'
            })
    
    def clean(self):
        cleaned_data = super().clean()
        program = cleaned_data.get('program')
        
        if program and hasattr(self.instance, 'applicant') and self.instance.applicant:
            # Check if user has already applied to this program
            if self.instance.pk:  # If updating existing application
                existing = Application.objects.filter(
                    applicant=self.instance.applicant,
                    program=program
                ).exclude(pk=self.instance.pk).first()
            else:  # If creating new application
                existing = Application.objects.filter(
                    applicant=self.instance.applicant,
                    program=program
                ).first()
            
            if existing:
                raise ValidationError('You have already applied to this program.')
        
        return cleaned_data

class StaffApprovalForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('is_approved',)

class ApplicationStatusForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ('status',)

class BulkEmailForm(forms.Form):
    subject = forms.CharField(max_length=100)
    message = forms.CharField(widget=forms.Textarea)
    applications = forms.ModelMultipleChoiceField(
        queryset=Application.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )
    
    def __init__(self, *args, **kwargs):
        queryset = kwargs.pop('queryset', None)
        super().__init__(*args, **kwargs)
        if queryset:
            self.fields['applications'].queryset = queryset

class ResidencyInterviewForm(forms.ModelForm):
    class Meta:
        model = Interview
        fields = [
            'professional_appearance', 'interest', 'behavior', 'future_plans',
            'personality', 'handling_emergencies', 'professional_attitude',
            'knowledge', 'research', 'test_score', 'medical_school_score'
        ]
        widgets = {
            'professional_appearance': forms.NumberInput(attrs={'min': 0, 'max': 5}),
            'interest': forms.NumberInput(attrs={'min': 0, 'max': 5}),
            'behavior': forms.NumberInput(attrs={'min': 0, 'max': 5}),
            'future_plans': forms.NumberInput(attrs={'min': 0, 'max': 5}),
            'personality': forms.NumberInput(attrs={'min': 0, 'max': 5}),
            'handling_emergencies': forms.NumberInput(attrs={'min': 0, 'max': 5}),
            'professional_attitude': forms.NumberInput(attrs={'min': 0, 'max': 5}),
            'knowledge': forms.NumberInput(attrs={'min': 0, 'max': 5}),
            'research': forms.NumberInput(attrs={'min': 0, 'max': 5}),
            'test_score': forms.HiddenInput(attrs={'max': 75}),
            'medical_school_score': forms.HiddenInput(attrs={'max': 10}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['form_type'] = forms.CharField(
            widget=forms.HiddenInput(),
            initial='RESIDENCY'
        )

class FellowshipInterviewForm(forms.ModelForm):
    class Meta:
        model = Interview
        fields = [
            'professional_appearance', 'interest', 'behavior', 'future_plans',
            'personality', 'handling_emergencies', 'professional_attitude',
            'knowledge', 'research', 'test_score', 'medical_school_score',
            'tentative_available_date'
        ]
        widgets = {
            'professional_appearance': forms.NumberInput(attrs={'min': 0, 'max': 5}),
            'interest': forms.NumberInput(attrs={'min': 0, 'max': 5}),
            'behavior': forms.NumberInput(attrs={'min': 0, 'max': 5}),
            'future_plans': forms.NumberInput(attrs={'min': 0, 'max': 5}),
            'personality': forms.NumberInput(attrs={'min': 0, 'max': 5}),
            'handling_emergencies': forms.NumberInput(attrs={'min': 0, 'max': 5}),
            'professional_attitude': forms.NumberInput(attrs={'min': 0, 'max': 5}),
            'knowledge': forms.NumberInput(attrs={'min': 0, 'max': 5}),
            'research': forms.NumberInput(attrs={'min': 0, 'max': 10}),
            'test_score': forms.HiddenInput(),
            'medical_school_score': forms.HiddenInput(),
            'tentative_available_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['form_type'] = forms.CharField(
            widget=forms.HiddenInput(),
            initial='FELLOWSHIP'
        )

class BulkScoreUploadForm(forms.Form):
    score_file = forms.FileField(
        label='Upload CSV/Excel file',
        help_text='File should contain columns: national_id, test_score'
    )
    
    def clean_score_file(self):
        file = self.cleaned_data.get('score_file')
        
        if not file:
            return None
            
        # Check file extension
        if not file.name.endswith(('.csv', '.xlsx', '.xls')):
            raise forms.ValidationError('File must be a CSV or Excel file')
            
        # For CSV files, validate structure
        if file.name.endswith('.csv'):
            try:
                # Read the CSV file
                csv_file = io.StringIO(file.read().decode('utf-8'))
                reader = csv.reader(csv_file)
                
                # Check header row
                header = next(reader, None)
                if not header or len(header) < 2:
                    raise forms.ValidationError('CSV file must have at least 2 columns')
                
                # Check if required columns exist
                required_columns = ['national_id', 'test_score']
                for col in required_columns:
                    if col.lower() not in [h.lower() for h in header]:
                        raise forms.ValidationError(f'Missing required column: {col}')
                
                # Reset file pointer
                file.seek(0)
                
            except Exception as e:
                raise forms.ValidationError(f'Error reading CSV file: {str(e)}')
                
        return file

class AdvancedFilterForm(forms.Form):
    STATUS_CHOICES = [('', '---')] + [(status, label) for status, label in Application.STATUS_CHOICES if status != 'DRAFT']
    PROGRAM_TYPE_CHOICES = [('', '---')] + list(Program.PROGRAM_TYPE_CHOICES)
    GPA_CHOICES = [('', '---')] + list(Application.GPA_CHOICES)
    
    status = forms.ChoiceField(choices=STATUS_CHOICES, required=False)
    program_type = forms.ChoiceField(choices=PROGRAM_TYPE_CHOICES, required=False)
    program = forms.ModelChoiceField(queryset=Program.objects.all(), required=False)
    gpa = forms.ChoiceField(choices=GPA_CHOICES, required=False)
    min_test_score = forms.IntegerField(required=False, min_value=0)
    max_test_score = forms.IntegerField(required=False, min_value=0)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['program'].queryset = Program.objects.filter(status='ACTIVE') 