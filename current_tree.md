Current Directory Structure:
.
├── README.md
├── accounts
│   ├── __init__.py
│   ├── __pycache__
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── migrations
│   │   ├── 0001_initial.py
│   │   ├── __init__.py
│   │   └── __pycache__
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── applications
│   ├── __init__.py
│   ├── __pycache__
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── migrations
│   │   ├── 0001_initial.py
│   │   ├── 0002_application_additional_info_and_more.py
│   │   ├── __init__.py
│   │   └── __pycache__
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── core
│   ├── __init__.py
│   ├── __pycache__
│   ├── admin.py
│   ├── apps.py
│   ├── migrations
│   │   ├── 0001_initial.py
│   │   ├── __init__.py
│   │   └── __pycache__
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── current_tree.md
├── db.sqlite3
├── gme
│   ├── __init__.py
│   ├── __pycache__
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── manage.py
├── media
│   └── documents
├── programs
│   ├── __init__.py
│   ├── __pycache__
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── migrations
│   │   ├── 0001_initial.py
│   │   ├── __init__.py
│   │   └── __pycache__
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── requirements.txt
├── static
│   ├── css
│   │   ├── forms.css
│   │   ├── main.css
│   │   └── notifications.css
│   ├── images
│   └── js
│       ├── applications.js
│       └── main.js
└── templates
    ├── accounts
    │   ├── login.html
    │   ├── profile.html
    │   ├── register.html
    │   └── staff_approval_list.html
    ├── applications
    │   ├── application_detail.html
    │   ├── application_form.html
    │   ├── application_list.html
    │   ├── bulk_email.html
    │   ├── document_upload.html
    │   └── update_status.html
    ├── base.html
    ├── core
    │   ├── dashboard.html
    │   └── home.html
    ├── programs
    │   ├── program_detail.html
    │   ├── program_form.html
    │   └── program_list.html
    └── shared