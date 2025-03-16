from django.urls import path
from . import views

app_name = 'programs'

urlpatterns = [
    path('', views.ProgramListView.as_view(), name='program_list'),
    path('<int:pk>/', views.ProgramDetailView.as_view(), name='program_detail'),
    path('create/', views.ProgramCreateView.as_view(), name='program_create'),
    path('<int:pk>/update/', views.ProgramUpdateView.as_view(), name='program_update'),
    path('<int:pk>/toggle-status/', views.toggle_program_status, name='toggle_program_status'),
] 