from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, ListView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from .models import User
from .forms import UserRegistrationForm, UserLoginForm

class RegisterView(CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')
    
    def form_valid(self, form):
        user = form.save(commit=False)
        
        # Auto-approve applicants, but not KHCC staff
        if user.user_type == User.USER_TYPE_APPLICANT:
            user.is_approved = True
        
        user.save()
        messages.success(self.request, _('Your account has been created successfully.'))
        
        if user.is_khcc_staff:
            messages.info(self.request, _('Your account is pending approval by GME staff.'))
        else:
            # Auto-login for applicants
            login(self.request, user)
            return redirect('core:dashboard')
        
        return super().form_valid(form)

class CustomLoginView(LoginView):
    form_class = UserLoginForm
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def form_valid(self, form):
        remember_me = self.request.POST.get('remember_me')
        
        if not remember_me:
            # Session expires when the user closes the browser
            self.request.session.set_expiry(0)
        
        return super().form_valid(form)

@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html')

@login_required
def logout_view(request):
    """Custom logout view to ensure proper redirection"""
    logout(request)
    messages.success(request, _('You have been logged out successfully.'))
    return redirect('core:home')

class StaffApprovalListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = User
    template_name = 'accounts/staff_approval_list.html'
    context_object_name = 'staff_users'
    
    def test_func(self):
        return self.request.user.is_gme_staff
    
    def get_queryset(self):
        return User.objects.filter(
            is_approved=False,
            user_type__in=[
                User.USER_TYPE_PROGRAM_DIRECTOR,
                User.USER_TYPE_INTERVIEWER
            ]
        )

@login_required
def approve_staff(request, user_id):
    if not request.user.is_gme_staff:
        messages.error(request, _('You do not have permission to approve staff.'))
        return redirect('core:dashboard')
    
    staff_user = get_object_or_404(User, id=user_id)
    
    if not staff_user.is_khcc_staff:
        messages.error(request, _('This user is not a KHCC staff member.'))
        return redirect('accounts:staff_approval_list')
    
    staff_user.is_approved = True
    staff_user.save()
    
    messages.success(request, _(f'Staff member {staff_user.username} has been approved.'))
    
    # TODO: Send email notification to the approved staff
    
    return redirect('accounts:staff_approval_list')

@login_required
def reject_staff(request, user_id):
    if not request.user.is_gme_staff:
        messages.error(request, _('You do not have permission to reject staff.'))
        return redirect('core:dashboard')
    
    staff_user = get_object_or_404(User, id=user_id)
    
    if not staff_user.is_khcc_staff:
        messages.error(request, _('This user is not a KHCC staff member.'))
        return redirect('accounts:staff_approval_list')
    
    # TODO: Send email notification to the rejected staff before deletion
    
    staff_user.delete()
    messages.success(request, _('Staff member has been rejected and removed.'))
    
    return redirect('accounts:staff_approval_list')
