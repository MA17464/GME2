from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import EmailValidator
from .models import User, Applicant, Program, Application

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
        fields = ('program_type', 'program', 'university_name', 'gpa', 
                  'national_id_document', 'cv', 'payment_receipt', 'university_certificate')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # If program_type is already selected, filter programs
        if 'program_type' in self.data:
            try:
                program_type = self.data.get('program_type')
                self.fields['program'].queryset = Program.objects.filter(
                    program_type=program_type, 
                    status='ACTIVE'
                )
            except (ValueError, TypeError):
                pass
        
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