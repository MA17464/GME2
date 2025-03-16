from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

# Create your models here.

class Notification(models.Model):
    # Notification types
    TYPE_INFO = 'info'
    TYPE_SUCCESS = 'success'
    TYPE_WARNING = 'warning'
    TYPE_ERROR = 'error'
    
    TYPE_CHOICES = [
        (TYPE_INFO, _('Information')),
        (TYPE_SUCCESS, _('Success')),
        (TYPE_WARNING, _('Warning')),
        (TYPE_ERROR, _('Error')),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=100)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_INFO)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
    
    class Meta:
        ordering = ['-created_at']

class EmailTemplate(models.Model):
    # Template types
    TYPE_ACCOUNT_APPROVAL = 'account_approval'
    TYPE_ACCOUNT_REJECTION = 'account_rejection'
    TYPE_APPLICATION_STATUS_CHANGE = 'application_status_change'
    TYPE_CUSTOM = 'custom'
    
    TYPE_CHOICES = [
        (TYPE_ACCOUNT_APPROVAL, _('Account Approval')),
        (TYPE_ACCOUNT_REJECTION, _('Account Rejection')),
        (TYPE_APPLICATION_STATUS_CHANGE, _('Application Status Change')),
        (TYPE_CUSTOM, _('Custom')),
    ]
    
    name = models.CharField(max_length=100)
    template_type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    subject = models.CharField(max_length=200)
    body = models.TextField(help_text=_('You can use placeholders like {{user_name}}, {{program_name}}, etc.'))
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
