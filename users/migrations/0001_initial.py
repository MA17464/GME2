# Generated by Django 5.1.7 on 2025-03-26 07:26

import django.contrib.auth.models
import django.contrib.auth.validators
import django.core.validators
import django.db.models.deletion
import django.utils.timezone
import users.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Program',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, validators=[django.core.validators.MinLengthValidator(3)])),
                ('program_type', models.CharField(choices=[('RESIDENCY', 'Residency'), ('FELLOWSHIP', 'Fellowship')], max_length=20)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('status', models.CharField(choices=[('ACTIVE', 'Active'), ('INACTIVE', 'Inactive')], default='ACTIVE', max_length=10)),
                ('capacity', models.PositiveIntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('user_type', models.CharField(choices=[('GME_STAFF', 'GME Staff'), ('PROGRAM_DIRECTOR', 'Program Director'), ('INTERVIEWER', 'Interviewer'), ('APPLICANT', 'Applicant')], max_length=20)),
                ('phone_number', models.CharField(blank=True, max_length=15)),
                ('is_approved', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
                ('program', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='staff_members', to='users.program')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Applicant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name_en', models.CharField(max_length=50)),
                ('second_name_en', models.CharField(max_length=50)),
                ('third_name_en', models.CharField(max_length=50)),
                ('last_name_en', models.CharField(max_length=50)),
                ('first_name_ar', models.CharField(max_length=50)),
                ('second_name_ar', models.CharField(max_length=50)),
                ('third_name_ar', models.CharField(max_length=50)),
                ('last_name_ar', models.CharField(max_length=50)),
                ('national_id', models.CharField(max_length=20, unique=True)),
                ('profile_picture', models.ImageField(blank=True, null=True, upload_to=users.models.profile_picture_upload_path)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='applicant_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ApplicantScore',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('national_id', models.CharField(max_length=20)),
                ('test_score', models.PositiveSmallIntegerField()),
                ('medical_school_score', models.PositiveSmallIntegerField()),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('is_processed', models.BooleanField(default=False)),
                ('uploaded_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='uploaded_scores', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('university_name', models.CharField(max_length=100)),
                ('gpa', models.CharField(choices=[('SATISFACTORY', 'Satisfactory'), ('GOOD', 'Good'), ('VERY_GOOD', 'Very Good'), ('EXCELLENT', 'Excellent')], max_length=20)),
                ('final_score', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('final_score_submitted', models.BooleanField(default=False)),
                ('final_score_notes', models.TextField(blank=True)),
                ('final_score_submitted_at', models.DateTimeField(blank=True, null=True)),
                ('national_id_document', models.FileField(upload_to=users.models.Application.national_id_upload_path)),
                ('cv', models.FileField(upload_to=users.models.Application.cv_upload_path)),
                ('payment_receipt', models.FileField(blank=True, null=True, upload_to=users.models.Application.payment_upload_path)),
                ('university_certificate', models.FileField(blank=True, null=True, upload_to=users.models.Application.certificate_upload_path)),
                ('board_certification', models.FileField(blank=True, null=True, upload_to=users.models.Application.board_certification_upload_path)),
                ('status', models.CharField(choices=[('DRAFT', 'Draft'), ('SUBMITTED', 'Submitted'), ('ELIGIBLE', 'Eligible'), ('NOT_ELIGIBLE', 'Not Eligible'), ('APPROVED', 'Approved'), ('REJECTED', 'Rejected'), ('WAIT_LISTED', 'Waitlisted'), ('INVITED_FOR_INTERVIEW', 'Invited for Interview')], default='SUBMITTED', max_length=25)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('applicant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='applications', to=settings.AUTH_USER_MODEL)),
                ('program', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='applications', to='users.program')),
            ],
            options={
                'unique_together': {('applicant', 'program')},
            },
        ),
        migrations.CreateModel(
            name='Interview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('form_type', models.CharField(choices=[('RESIDENCY', 'Residency'), ('FELLOWSHIP', 'Fellowship')], max_length=20)),
                ('professional_appearance', models.PositiveSmallIntegerField(default=0)),
                ('interest', models.PositiveSmallIntegerField(default=0)),
                ('behavior', models.PositiveSmallIntegerField(default=0)),
                ('future_plans', models.PositiveSmallIntegerField(default=0)),
                ('personality', models.PositiveSmallIntegerField(default=0)),
                ('handling_emergencies', models.PositiveSmallIntegerField(default=0)),
                ('professional_attitude', models.PositiveSmallIntegerField(default=0)),
                ('knowledge', models.PositiveSmallIntegerField(default=0)),
                ('research', models.PositiveSmallIntegerField(default=0)),
                ('time_management', models.SmallIntegerField(default=0)),
                ('flexibility_teamwork', models.SmallIntegerField(default=0)),
                ('takes_feedback', models.SmallIntegerField(default=0)),
                ('stress_coping', models.SmallIntegerField(default=0)),
                ('problem_solving', models.SmallIntegerField(default=0)),
                ('leadership', models.SmallIntegerField(default=0)),
                ('test_score', models.PositiveSmallIntegerField(default=0)),
                ('medical_school_score', models.PositiveSmallIntegerField(default=0)),
                ('tentative_available_date', models.DateField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('application', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='interviews', to='users.application')),
                ('interviewer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='conducted_interviews', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
