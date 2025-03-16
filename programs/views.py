from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy

from .models import Program
from .forms import ProgramForm

class ProgramListView(ListView):
    model = Program
    template_name = 'programs/program_list.html'
    context_object_name = 'programs'
    
    def get_queryset(self):
        queryset = Program.objects.all()
        
        # Filter by program type if specified
        program_type = self.request.GET.get('type')
        if program_type in [Program.PROGRAM_TYPE_RESIDENCY, Program.PROGRAM_TYPE_FELLOWSHIP]:
            queryset = queryset.filter(program_type=program_type)
        
        # Filter by department if specified
        department = self.request.GET.get('department')
        if department:
            queryset = queryset.filter(department=department)
        
        # Filter by status if specified
        status = self.request.GET.get('status')
        if status in [Program.STATUS_ACTIVE, Program.STATUS_INACTIVE]:
            queryset = queryset.filter(status=status)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['departments'] = Program.DEPARTMENT_CHOICES
        return context

class ProgramDetailView(DetailView):
    model = Program
    template_name = 'programs/program_detail.html'
    context_object_name = 'program'

class ProgramCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Program
    form_class = ProgramForm
    template_name = 'programs/program_form.html'
    success_url = reverse_lazy('programs:program_list')
    
    def test_func(self):
        return self.request.user.is_gme_staff
    
    def form_valid(self, form):
        messages.success(self.request, _('Program created successfully.'))
        return super().form_valid(form)

class ProgramUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Program
    form_class = ProgramForm
    template_name = 'programs/program_form.html'
    success_url = reverse_lazy('programs:program_list')
    
    def test_func(self):
        return self.request.user.is_gme_staff
    
    def form_valid(self, form):
        messages.success(self.request, _('Program updated successfully.'))
        return super().form_valid(form)

@login_required
def toggle_program_status(request, pk):
    if not request.user.is_gme_staff:
        messages.error(request, _('You do not have permission to change program status.'))
        return redirect('programs:program_list')
    
    program = get_object_or_404(Program, pk=pk)
    
    if program.status == Program.STATUS_ACTIVE:
        program.status = Program.STATUS_INACTIVE
        status_message = _('Program deactivated successfully.')
    else:
        program.status = Program.STATUS_ACTIVE
        status_message = _('Program activated successfully.')
    
    program.save()
    messages.success(request, status_message)
    
    return redirect('programs:program_list')
