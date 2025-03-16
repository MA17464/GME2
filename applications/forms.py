from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Application, ApplicationDocument
from programs.models import Program

class ApplicationForm(forms.ModelForm):
    program_type = forms.ChoiceField(
        choices=Program.PROGRAM_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True,
        label=_('Program Type')
    )
    
    program = forms.ModelChoiceField(
        queryset=Program.objects.filter(status=Program.STATUS_ACTIVE),
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True,
        label=_('Select Program')
    )
    
    class Meta:
        model = Application
        fields = ('program_type', 'program', 'university_name', 'gpa', 'is_gpa_percentage', 
                 'personal_statement', 'additional_info')
        widgets = {
            'university_name': forms.TextInput(attrs={'class': 'form-input'}),
            'gpa': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'min': '0'}),
            'is_gpa_percentage': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'personal_statement': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 5}),
            'additional_info': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Initially, filter programs by the first program type
        if 'program_type' in self.data:
            program_type = self.data.get('program_type')
            self.fields['program'].queryset = Program.objects.filter(
                program_type=program_type,
                status=Program.STATUS_ACTIVE
            )
        elif self.instance.pk:
            self.fields['program_type'].initial = self.instance.program.program_type
            self.fields['program'].queryset = Program.objects.filter(
                program_type=self.instance.program.program_type,
                status=Program.STATUS_ACTIVE
            )
        else:
            self.fields['program'].queryset = Program.objects.none()
    
    def clean_gpa(self):
        gpa = self.cleaned_data.get('gpa')
        is_percentage = self.cleaned_data.get('is_gpa_percentage')
        
        if is_percentage and (gpa < 0 or gpa > 100):
            raise forms.ValidationError(_('GPA percentage must be between 0 and 100'))
        elif not is_percentage and (gpa < 0 or gpa > 4):
            raise forms.ValidationError(_('GPA scale must be between 0 and 4'))
        
        return gpa

class ApplicationDocumentForm(forms.ModelForm):
    class Meta:
        model = ApplicationDocument
        fields = ('document_type', 'file')
        widgets = {
            'document_type': forms.Select(attrs={'class': 'form-select'}),
            'file': forms.FileInput(attrs={'class': 'form-file-input'}),
        }

class ApplicationStatusForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ('status', 'notes')
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3}),
        }

class BulkEmailForm(forms.Form):
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-input'})
    )
    
    message = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-textarea', 'rows': 5})
    )
    
    applications = forms.ModelMultipleChoiceField(
        queryset=Application.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-checkbox'}),
        required=True
    ) 