from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Program

class ProgramForm(forms.ModelForm):
    class Meta:
        model = Program
        fields = ('name', 'department', 'program_type', 'start_date', 'end_date', 'status', 'capacity', 'description')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'program_type': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-input', 'min': '1'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 4}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and start_date >= end_date:
            self.add_error('end_date', _('End date must be after start date'))
        
        return cleaned_data 