from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.translation import gettext_lazy as _
from .models import User

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': _('Email')})
    )
    
    user_type = forms.ChoiceField(
        choices=[
            (User.USER_TYPE_APPLICANT, _('Applicant')),
            (User.USER_TYPE_PROGRAM_DIRECTOR, _('Program Director')),
            (User.USER_TYPE_INTERVIEWER, _('Interviewer')),
        ],
        widget=forms.RadioSelect(attrs={'class': 'form-radio'}),
        initial=User.USER_TYPE_APPLICANT
    )
    
    department = forms.ChoiceField(
        choices=User.DEPARTMENT_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'user_type', 'department', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input', 'placeholder': _('Username')}),
            'first_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': _('First Name')}),
            'last_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': _('Last Name')}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-input', 'placeholder': _('Password')})
        self.fields['password2'].widget.attrs.update({'class': 'form-input', 'placeholder': _('Confirm Password')})
        
        # Make department field required for KHCC staff
        self.fields['department'].required = False
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        user_type = self.cleaned_data.get('user_type')
        
        # Check if KHCC staff email ends with @khcc.jo
        if user_type in [User.USER_TYPE_PROGRAM_DIRECTOR, User.USER_TYPE_INTERVIEWER] and not email.endswith('@khcc.jo'):
            raise forms.ValidationError(_('KHCC staff email must end with @khcc.jo'))
        
        return email
    
    def clean(self):
        cleaned_data = super().clean()
        user_type = cleaned_data.get('user_type')
        department = cleaned_data.get('department')
        
        # Department is required for Program Director and Interviewer
        if user_type in [User.USER_TYPE_PROGRAM_DIRECTOR, User.USER_TYPE_INTERVIEWER] and not department:
            self.add_error('department', _('Department is required for KHCC staff'))
        
        return cleaned_data

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': _('Username')})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': _('Password')})
    )
    
    error_messages = {
        'invalid_login': _(
            "Please enter a correct username and password. Note that both "
            "fields may be case-sensitive."
        ),
        'inactive': _("This account is inactive. Please contact the administrator."),
    }
    
    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        
        # Check if KHCC staff is approved
        if user.is_khcc_staff and not user.is_approved:
            raise forms.ValidationError(
                _("Your account is pending approval. Please contact the GME staff."),
                code='pending_approval',
            ) 