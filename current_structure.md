## Current Directory Structure
```
.
├── README.md
├── current_structure.md
├── db.sqlite3
├── gme
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── manage.py
├── media
│   └── documents
│       ├── certificates
│       ├── cv
│       ├── national_id
│       └── payment
└── users
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── forms.py
    ├── migrations
    │   ├── 0001_initial.py
    │   ├── 0002_alter_application_cv_and_more.py
    │   ├── 0003_alter_program_capacity.py
    │   ├── 0004_alter_program_name.py
    │   ├── 0005_alter_application_cv_and_more.py
    │   ├── 0006_remove_user_department.py
    │   ├── 0007_user_program.py
    │   ├── 0008_auto_20250317_0757.py
    │   ├── 0009_auto_20250317_0809.py
    │   ├── 0010_auto_20250317_0818.py
    │   ├── 0011_alter_application_gpa.py
    │   └── __init__.py
    ├── models.py
    ├── templates
    │   └── users
    │       ├── applicant_dashboard.html
    │       ├── applicant_register.html
    │       ├── apply.html
    │       ├── approve_staff.html
    │       ├── base.html
    │       ├── conduct_interview.html
    │       ├── dashboard.html
    │       ├── delete_program.html
    │       ├── edit_program.html
    │       ├── home.html
    │       ├── interviewer_dashboard.html
    │       ├── login.html
    │       ├── manage_programs.html
    │       ├── staff_register.html
    │       ├── update_application_status.html
    │       └── upload_scores.html
    ├── tests.py
    ├── urls.py
    └── views.py
```