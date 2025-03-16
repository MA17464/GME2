from django.urls import path
from . import views
from django.urls import reverse_lazy

app_name = 'accounts'

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('staff-approval/', views.StaffApprovalListView.as_view(), name='staff_approval_list'),
    path('staff-approval/<int:user_id>/approve/', views.approve_staff, name='approve_staff'),
    path('staff-approval/<int:user_id>/reject/', views.reject_staff, name='reject_staff'),
] 